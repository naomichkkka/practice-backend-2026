from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Survey, Question, Choice

User = get_user_model()


class SurveyLifecycleTests(APITestCase):
    """Жизненный цикл: опубликованный опрос нельзя редактировать."""

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='testpass123')
        self.other = User.objects.create_user(username='other', password='testpass123')
        self.survey = Survey.objects.create(
            title='Draft Survey',
            description='',
            status=Survey.Status.DRAFT,
            author=self.author,
        )
        self.question = Question.objects.create(
            survey=self.survey, text='Q1', type=Question.Type.SINGLE, order=1,
        )
        self.choice = Choice.objects.create(question=self.question, text='Yes')

    def test_cannot_edit_published_survey_structure(self):
        """Нельзя добавлять/редактировать вопросы у опубликованного опроса."""
        self.survey.status = Survey.Status.PUBLISHED
        self.survey.save()
        self.client.force_authenticate(user=self.author)
        # Попытка добавить вопрос
        r = self.client.post(
            f'/api/surveys/{self.survey.id}/questions/',
            {'text': 'New Q', 'type': Question.Type.TEXT, 'order': 2},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        # Попытка обновить опрос (например заголовок) — по ТЗ нельзя редактировать структуру;
        # в нашей реализации мы запретили update для не-черновика целиком
        r = self.client.patch(
            f'/api/surveys/{self.survey.id}/',
            {'title': 'Hacked'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_edit_draft_survey(self):
        """Черновик можно редактировать."""
        self.client.force_authenticate(user=self.author)
        r = self.client.patch(
            f'/api/surveys/{self.survey.id}/',
            {'title': 'Updated title'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.title, 'Updated title')

    def test_cannot_add_choices_to_text_question(self):
        """К текстовому вопросу нельзя добавить варианты ответов."""
        text_q = Question.objects.create(
            survey=self.survey, text='Text Q', type=Question.Type.TEXT, order=2,
        )
        self.client.force_authenticate(user=self.author)
        r = self.client.post(
            f'/api/surveys/{self.survey.id}/questions/{text_q.id}/choices/',
            {'text': 'Option'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
