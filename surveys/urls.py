from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SurveyViewSet, QuestionViewSet, ChoiceViewSet

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='surveys')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'surveys/<int:survey_pk>/questions/',
        QuestionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='survey-questions-list',
    ),
    path(
        'surveys/<int:survey_pk>/questions/<int:pk>/',
        QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='survey-questions-detail',
    ),
    path(
        'surveys/<int:survey_pk>/questions/<int:question_pk>/choices/',
        ChoiceViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='survey-question-choices-list',
    ),
    path(
        'surveys/<int:survey_pk>/questions/<int:question_pk>/choices/<int:pk>/',
        ChoiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='survey-question-choices-detail',
    ),
]
