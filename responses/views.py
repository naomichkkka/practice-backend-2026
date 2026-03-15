from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from surveys.models import Survey, Question, Choice
from .models import Response as SurveyResponse, Answer
from .serializers import SubmitResponseSerializer


def _validate_answers(survey, answers_data):
    """Валидация ответов по типам вопросов. Возвращает (errors dict или None, list of (question, choice_ids, text))."""
    questions = {q.id: q for q in survey.questions.prefetch_related('choices').all()}
    if not questions:
        return {'answers': 'Survey has no questions.'}, None

    answers_by_q = {a['question_id']: a for a in answers_data}
    result = []

    for qid, question in questions.items():
        a = answers_by_q.get(qid)
        if a is None:
            return {'answers': f'Missing answer for question {qid}.'}, None

        choice_ids = a.get('choice_ids') or []
        text_answer = (a.get('text_answer') or '').strip()

        if question.type == Question.Type.TEXT:
            if choice_ids:
                return {'answers': f'Question {qid} is text, cannot submit choice_ids.'}, None
            if not text_answer:
                return {'answers': f'Question {qid} requires text answer.'}, None
            result.append((question, [], text_answer))
            continue

        if question.type == Question.Type.SINGLE:
            if len(choice_ids) != 1:
                return {'answers': f'Question {qid} (single choice) must have exactly one choice.'}, None
        else:  # multiple_choice
            if len(choice_ids) < 1:
                return {'answers': f'Question {qid} (multiple choice) must have at least one choice.'}, None

        valid_choice_ids = set(question.choices.values_list('id', flat=True))
        if not set(choice_ids) <= valid_choice_ids:
            return {'answers': f'Invalid choices for question {qid}.'}, None
        result.append((question, choice_ids, ''))
    return None, result


class SubmitSurveyView(APIView):
    """POST /api/surveys/{id}/submit/ — отправить ответы респондента."""

    permission_classes = [IsAuthenticated]

    def post(self, request, survey_id):
        try:
            survey = Survey.objects.prefetch_related('questions', 'questions__choices').get(pk=survey_id)
        except Survey.DoesNotExist:
            return Response({'detail': 'Survey not found.'}, status=status.HTTP_404_NOT_FOUND)

        if survey.status != Survey.Status.PUBLISHED:
            return Response(
                {'detail': 'Survey is not accepting responses (only published surveys).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if SurveyResponse.objects.filter(survey=survey, respondent=request.user).exists():
            return Response(
                {'detail': 'You have already submitted a response to this survey.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = SubmitResponseSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        errors, validated = _validate_answers(survey, ser.validated_data['answers'])
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            resp = SurveyResponse.objects.create(survey=survey, respondent=request.user)
            for question, choice_ids, text_answer in validated:
                ans = Answer.objects.create(
                    response=resp,
                    question=question,
                    text_answer=text_answer or None,
                )
                if choice_ids:
                    ans.selected_choices.set(choice_ids)
        return Response({'response_id': resp.id}, status=status.HTTP_201_CREATED)


class SurveyAnalyticsView(APIView):
    """GET /api/surveys/{id}/analytics/ — аналитика для автора."""

    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        try:
            survey = Survey.objects.prefetch_related(
                'questions', 'questions__choices',
                'responses', 'responses__answers', 'responses__answers__selected_choices',
            ).get(pk=survey_id)
        except Survey.DoesNotExist:
            return Response({'detail': 'Survey not found.'}, status=status.HTTP_404_NOT_FOUND)

        if survey.author_id != request.user.id:
            return Response({'detail': 'Only author can view analytics.'}, status=status.HTTP_403_FORBIDDEN)

        respondents_count = survey.responses.count()
        questions_data = []

        for q in survey.questions.all():
            if q.type == Question.Type.TEXT:
                text_answers = list(
                    Answer.objects.filter(response__survey=survey, question=q)
                    .values_list('text_answer', flat=True)
                )
                questions_data.append({
                    'question_id': q.id,
                    'question_text': q.text,
                    'type': q.type,
                    'text_answers': text_answers,
                })
            else:
                choices_stats = []
                for choice in q.choices.all():
                    count = Answer.objects.filter(
                        response__survey=survey,
                        question=q,
                        selected_choices=choice,
                    ).count()
                    pct = round(100 * count / respondents_count, 2) if respondents_count else 0
                    choices_stats.append({
                        'choice_id': choice.id,
                        'text': choice.text,
                        'count': count,
                        'percent': pct,
                    })
                questions_data.append({
                    'question_id': q.id,
                    'question_text': q.text,
                    'type': q.type,
                    'choices': choices_stats,
                })

        return Response({
            'survey_id': survey.id,
            'respondents_count': respondents_count,
            'questions': questions_data,
        })


class SurveyExportView(APIView):
    """GET /api/surveys/{id}/export/ — экспорт результатов в JSON."""

    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        try:
            survey = Survey.objects.prefetch_related(
                'questions', 'questions__choices',
                'responses', 'responses__answers', 'responses__answers__selected_choices',
            ).get(pk=survey_id)
        except Survey.DoesNotExist:
            return Response({'detail': 'Survey not found.'}, status=status.HTTP_404_NOT_FOUND)

        if survey.author_id != request.user.id:
            return Response({'detail': 'Only author can export.'}, status=status.HTTP_403_FORBIDDEN)

        responses_data = []
        for resp in survey.responses.select_related('respondent').prefetch_related('answers', 'answers__question', 'answers__selected_choices'):
            answers_list = []
            for ans in resp.answers.all():
                if ans.text_answer is not None:
                    answers_list.append({'question_id': ans.question_id, 'text_answer': ans.text_answer})
                else:
                    answers_list.append({
                        'question_id': ans.question_id,
                        'choice_ids': list(ans.selected_choices.values_list('id', flat=True)),
                    })
            responses_data.append({
                'respondent_id': resp.respondent_id,
                'created_at': resp.created_at.isoformat(),
                'answers': answers_list,
            })

        payload = {
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'status': survey.status,
            },
            'respondents_count': survey.responses.count(),
            'responses': responses_data,
        }
        return JsonResponse(payload, json_dumps_params={'ensure_ascii': False})
