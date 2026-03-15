from django.urls import path
from .views import SubmitSurveyView, SurveyAnalyticsView, SurveyExportView

urlpatterns = [
    path('surveys/<int:survey_id>/submit/', SubmitSurveyView.as_view(), name='survey-submit'),
    path('surveys/<int:survey_id>/analytics/', SurveyAnalyticsView.as_view(), name='survey-analytics'),
    path('surveys/<int:survey_id>/export/', SurveyExportView.as_view(), name='survey-export'),
]
