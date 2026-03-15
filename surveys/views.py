from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Survey, Question, Choice
from .serializers import (
    SurveySerializer,
    SurveyListSerializer,
    SurveyDetailSerializer,
    QuestionSerializer,
    QuestionWriteSerializer,
    ChoiceSerializer,
    ChoiceWriteSerializer,
)
from .permissions import IsAuthorOrReadOnly, IsSurveyAuthor


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = SurveySerializer

    def get_queryset(self):
        qs = Survey.objects.annotate(responses_count=Count('responses')).select_related('author')
        # Фильтр: мои опросы
        if self.request.query_params.get('my') == 'true':
            qs = qs.filter(author=self.request.user)
        # Фильтр по статусу
        st = self.request.query_params.get('status')
        if st in [Survey.Status.DRAFT, Survey.Status.PUBLISHED, Survey.Status.CLOSED]:
            qs = qs.filter(status=st)
        # Сортировка
        order = self.request.query_params.get('order', 'date')
        if order == 'responses_count':
            qs = qs.order_by('-responses_count', '-created_at')
        else:
            qs = qs.order_by('-created_at')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return SurveyListSerializer
        if self.action == 'retrieve':
            return SurveyDetailSerializer
        return SurveySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Survey.Status.DRAFT:
            return Response(
                {'detail': 'Cannot edit survey that is not in draft status.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Survey.Status.DRAFT:
            return Response(
                {'detail': 'Cannot delete survey that is not in draft status.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSurveyAuthor])
    def publish(self, request, pk=None):
        survey = self.get_object()
        if survey.status != Survey.Status.DRAFT:
            return Response(
                {'detail': 'Only draft surveys can be published.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        survey.status = Survey.Status.PUBLISHED
        survey.save(update_fields=['status', 'updated_at'])
        return Response({'status': survey.status})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSurveyAuthor])
    def close(self, request, pk=None):
        survey = self.get_object()
        if survey.status != Survey.Status.PUBLISHED:
            return Response(
                {'detail': 'Only published surveys can be closed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        survey.status = Survey.Status.CLOSED
        survey.save(update_fields=['status', 'updated_at'])
        return Response({'status': survey.status})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='take')
    def take(self, request, pk=None):
        """Получить опрос для прохождения (только опубликованные)."""
        survey = self.get_object()
        if survey.status != Survey.Status.PUBLISHED:
            return Response(
                {'detail': 'Survey is not available for taking (only published surveys).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SurveyDetailSerializer(survey)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(survey_id=self.kwargs['survey_pk']).order_by('order')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return QuestionWriteSerializer
        return QuestionSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['survey'] = Survey.objects.get(pk=self.kwargs['survey_pk'])
        return ctx

    def perform_create(self, serializer):
        survey = Survey.objects.get(pk=self.kwargs['survey_pk'])
        if survey.author != self.request.user:
            raise PermissionDenied('Only author can add questions.')
        if survey.status != Survey.Status.DRAFT:
            raise ValidationError({'detail': 'Cannot edit published or closed survey.'})
        serializer.save(survey=survey)

    def check_survey_editable(self):
        survey = Survey.objects.get(pk=self.kwargs['survey_pk'])
        if survey.author != self.request.user:
            raise PermissionDenied('Only author can edit questions.')
        if survey.status != Survey.Status.DRAFT:
            raise ValidationError({'detail': 'Cannot edit published or closed survey.'})

    def update(self, request, *args, **kwargs):
        self.check_survey_editable()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_survey_editable()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_survey_editable()
        return super().destroy(request, *args, **kwargs)


class ChoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(question_id=self.kwargs['question_pk'])

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ChoiceWriteSerializer
        return ChoiceSerializer

    def get_question(self):
        return Question.objects.select_related('survey').get(
            pk=self.kwargs['question_pk'],
            survey_id=self.kwargs['survey_pk'],
        )

    def check_can_edit_choices(self):
        question = self.get_question()
        if question.survey.author != self.request.user:
            raise PermissionDenied('Only author can edit choices.')
        if question.survey.status != Survey.Status.DRAFT:
            raise ValidationError({'detail': 'Cannot edit published or closed survey.'})
        if question.type == Question.Type.TEXT:
            raise ValidationError({'detail': 'Text questions cannot have choices.'})
        return question

    def perform_create(self, serializer):
        question = self.check_can_edit_choices()
        serializer.save(question=question)

    def update(self, request, *args, **kwargs):
        self.check_can_edit_choices()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_can_edit_choices()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_can_edit_choices()
        return super().destroy(request, *args, **kwargs)
