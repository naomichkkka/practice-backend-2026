from rest_framework import serializers

from .models import Survey, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text')


class ChoiceWriteSerializer(serializers.ModelSerializer):
    """Создание/обновление варианта. Валидация «не для текстового вопроса» — во view."""

    class Meta:
        model = Choice
        fields = ('id', 'text')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'order', 'choices')

    def validate_type(self, value):
        if value not in [Question.Type.SINGLE, Question.Type.MULTIPLE, Question.Type.TEXT]:
            raise serializers.ValidationError('Invalid question type.')
        return value


class QuestionWriteSerializer(serializers.ModelSerializer):
    """Без choices (варианты добавляются отдельно)."""

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'order')

    def validate_type(self, value):
        if value not in [Question.Type.SINGLE, Question.Type.MULTIPLE, Question.Type.TEXT]:
            raise serializers.ValidationError('Invalid question type.')
        return value


class SurveyListSerializer(serializers.ModelSerializer):
    """Краткий список для списка опросов (с опциональным responses_count)."""

    responses_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'status', 'author', 'created_at', 'updated_at', 'responses_count')

    def get_responses_count(self, obj):
        return getattr(obj, 'responses_count', None) or obj.responses.count()


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Опрос с вложенными вопросами и вариантами."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'status', 'author', 'created_at', 'updated_at', 'questions')


class SurveySerializer(serializers.ModelSerializer):
    """Для создания/обновления опроса (без вопросов)."""

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'status', 'author', 'created_at', 'updated_at')
        read_only_fields = ('author',)

    def validate_status(self, value):
        if value not in [Survey.Status.DRAFT, Survey.Status.PUBLISHED, Survey.Status.CLOSED]:
            raise serializers.ValidationError('Invalid status.')
        return value
