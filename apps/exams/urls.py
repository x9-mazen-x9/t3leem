# apps/exams/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, GradeEssayView, AllSubmissionsView

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),

    # المدرس يصحح الأسئلة المقالية لتسليم معين
    # POST /api/exams/submissions/<submission_id>/grade-essay/
    path(
        'exams/submissions/<int:submission_id>/grade-essay/',
        GradeEssayView.as_view(),
        name='grade-essay'
    ),

    # المدرس يرى كل تسليمات امتحان معين
    # GET /api/exams/<exam_id>/submissions/
    path(
        'exams/<int:exam_id>/submissions/',
        AllSubmissionsView.as_view(),
        name='exam-submissions'
    ),
]
