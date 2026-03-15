from rest_framework import serializers
from surveys.models import Question, Choice


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    text_answer = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_choice_ids(self, value):
        if not value:
            return value
        if not Choice.objects.filter(pk__in=value).exists():
            raise serializers.ValidationError('Invalid choice ids.')
        return value


class SubmitResponseSerializer(serializers.Serializer):
    answers = SubmitAnswerSerializer(many=True)
