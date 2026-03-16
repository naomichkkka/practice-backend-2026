from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from surveys.models import Survey, Question, Choice
from .models import Response as SurveyResponse, Answer

User = get_user_model()


class SubmitValidationTests(APITestCase):
    """Валидация ответов по типам вопросов и защита от повторного прохождения."""

    def setUp(self):
        self.user = User.objects.create_user(username='resp', password='testpass123')
        self.survey = Survey.objects.create(
            title='Test', description='', status=Survey.Status.PUBLISHED, author=self.user,
        )
        self.q_single = Question.objects.create(
            survey=self.survey, text='Single?', type=Question.Type.SINGLE, order=1,
        )
        self.c1 = Choice.objects.create(question=self.q_single, text='A')
        self.c2 = Choice.objects.create(question=self.q_single, text='B')
        self.q_multiple = Question.objects.create(
            survey=self.survey, text='Multiple?', type=Question.Type.MULTIPLE, order=2,
        )
        self.c3 = Choice.objects.create(question=self.q_multiple, text='X')
        self.c4 = Choice.objects.create(question=self.q_multiple, text='Y')
        self.q_text = Question.objects.create(
            survey=self.survey, text='Comment', type=Question.Type.TEXT, order=3,
        )

    def test_single_choice_must_have_exactly_one(self):
        """Одиночный выбор: ровно один вариант."""
        self.client.force_authenticate(user=self.user)
        # Ноль вариантов — ошибка
        payload = {
            'answers': [
                {'question_id': self.q_single.id, 'choice_ids': []},
                {'question_id': self.q_multiple.id, 'choice_ids': [self.c3.id]},
                {'question_id': self.q_text.id, 'text_answer': 'ok'},
            ],
        }
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        # Два варианта — ошибка
        payload['answers'][0]['choice_ids'] = [self.c1.id, self.c2.id]
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        # Один вариант — ок
        payload['answers'][0]['choice_ids'] = [self.c1.id]
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_multiple_choice_at_least_one(self):
        """Множественный выбор: минимум один вариант."""
        self.client.force_authenticate(user=self.user)
        payload = {
            'answers': [
                {'question_id': self.q_single.id, 'choice_ids': [self.c1.id]},
                {'question_id': self.q_multiple.id, 'choice_ids': []},
                {'question_id': self.q_text.id, 'text_answer': 'ok'},
            ],
        }
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        payload['answers'][1]['choice_ids'] = [self.c3.id, self.c4.id]
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_text_question_requires_text(self):
        """Текстовый вопрос: обязателен текст, нельзя передавать choice_ids."""
        self.client.force_authenticate(user=self.user)
        payload = {
            'answers': [
                {'question_id': self.q_single.id, 'choice_ids': [self.c1.id]},
                {'question_id': self.q_multiple.id, 'choice_ids': [self.c3.id]},
                {'question_id': self.q_text.id, 'text_answer': ''},
            ],
        }
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        payload['answers'][2]['text_answer'] = 'Some text'
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_cannot_submit_twice(self):
        """Один респондент — один раз на опрос."""
        self.client.force_authenticate(user=self.user)
        payload = {
            'answers': [
                {'question_id': self.q_single.id, 'choice_ids': [self.c1.id]},
                {'question_id': self.q_multiple.id, 'choice_ids': [self.c3.id]},
                {'question_id': self.q_text.id, 'text_answer': 'First'},
            ],
        }
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already', r.data.get('detail', ''))

    def test_closed_survey_rejects_submit(self):
        """Закрытый опрос не принимает ответы."""
        self.survey.status = Survey.Status.CLOSED
        self.survey.save()
        self.client.force_authenticate(user=self.user)
        payload = {
            'answers': [
                {'question_id': self.q_single.id, 'choice_ids': [self.c1.id]},
                {'question_id': self.q_multiple.id, 'choice_ids': [self.c3.id]},
                {'question_id': self.q_text.id, 'text_answer': 'No'},
            ],
        }
        r = self.client.post(f'/api/surveys/{self.survey.id}/submit/', payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
