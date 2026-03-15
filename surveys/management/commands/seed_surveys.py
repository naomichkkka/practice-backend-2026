from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from surveys.models import Survey, Question, Choice

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users and surveys (draft and published) with questions and choices.'

    def handle(self, *args, **options):
        author, created = User.objects.get_or_create(
            username='author1',
            defaults={'email': 'author1@test.com', 'is_staff': False},
        )
        author.set_password('testpass123')
        author.save()

        respondent, _ = User.objects.get_or_create(
            username='respondent1',
            defaults={'email': 'resp1@test.com', 'is_staff': False},
        )
        respondent.set_password('testpass123')
        respondent.save()

        # Черновик с разными типами вопросов
        draft, _ = Survey.objects.get_or_create(
            title='Опрос (черновик)',
            author=author,
            defaults={'description': 'Тестовый черновик', 'status': Survey.Status.DRAFT},
        )
        if draft.status != Survey.Status.DRAFT:
            draft.status = Survey.Status.DRAFT
            draft.save(update_fields=['status'])
        q1, _ = Question.objects.get_or_create(
            survey=draft, order=1,
            defaults={'text': 'Один вариант?', 'type': Question.Type.SINGLE},
        )
        for i, text in enumerate(['Да', 'Нет'], start=1):
            Choice.objects.get_or_create(question=q1, text=text)
        q2, _ = Question.objects.get_or_create(
            survey=draft, order=2,
            defaults={'text': 'Несколько вариантов?', 'type': Question.Type.MULTIPLE},
        )
        for text in ['A', 'B', 'C']:
            Choice.objects.get_or_create(question=q2, text=text)
        Question.objects.get_or_create(
            survey=draft, order=3,
            defaults={'text': 'Ваш комментарий', 'type': Question.Type.TEXT},
        )

        # Опубликованный опрос
        published, _ = Survey.objects.get_or_create(
            title='Опубликованный опрос',
            author=author,
            defaults={'description': 'Можно проходить', 'status': Survey.Status.PUBLISHED},
        )
        if published.status != Survey.Status.PUBLISHED:
            published.status = Survey.Status.PUBLISHED
            published.save(update_fields=['status'])
        qp1, _ = Question.objects.get_or_create(
            survey=published, order=1,
            defaults={'text': 'Выберите один', 'type': Question.Type.SINGLE},
        )
        for text in ['Вариант 1', 'Вариант 2']:
            Choice.objects.get_or_create(question=qp1, text=text)
        Question.objects.get_or_create(
            survey=published, order=2,
            defaults={'text': 'Напишите ответ', 'type': Question.Type.TEXT},
        )

        self.stdout.write(self.style.SUCCESS(
            'Created users author1 / respondent1 (password: testpass123), '
            'draft survey and published survey with questions.'
        ))
