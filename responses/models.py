from django.db import models
from django.contrib.auth import get_user_model
from surveys.models import Survey, Question, Choice

User = get_user_model()


class Response(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    respondent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('survey', 'respondent')


class Answer(models.Model):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    text_answer = models.TextField(blank=True, null=True)
    selected_choices = models.ManyToManyField(Choice, blank=True)