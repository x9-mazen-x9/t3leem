# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.lessons.views import LessonViewSet
from apps.social.views import PostViewSet, CommentViewSet
from apps.notifications.views import NotificationViewSet, TeacherBroadcastView, PlatformBroadcastView
from apps.teachers.views import TeacherViewSet, TeacherServiceRequestView
from apps.students.views import StudentProfileView, BulkActivateRenewView, EnrollmentViewSet
from apps.students.views import StudentPublicView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.core.views import health_view, owner_dashboard_view
from apps.users.views import RegisterView, MeView, AvatarUploadView
from apps.courses.views import (
    CourseViewSet, UnitViewSet,
    CourseDetailPublicView, GenerateCodesView,
    ListCodesView, RedeemCodeView, CourseStudentProgressView,
)
from apps.progress.views import LessonProgressViewSet
from apps.exams.views import ExamViewSet, GradeEssayView, AllSubmissionsView

router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'progress', LessonProgressViewSet, basename='progress')
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    path('admin/', admin.site.urls),

    # مسارات التوثيق (Docs)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # مسارات المصادقة (JWT)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    path('api/auth/avatar/', AvatarUploadView.as_view(), name='auth_avatar'),

    # مسارات الـ API Router
    path('api/', include(router.urls)),

    # مسارات إضافية
    path('api/me/student/', StudentProfileView.as_view(), name='student_profile'),
    path('api/students/public/<int:student_id>/', StudentPublicView.as_view(), name='student_public'),
    path('api/bulk/activate-renew/', BulkActivateRenewView.as_view(), name='bulk_activate_renew'),
    path('api/admin/owner-dashboard/', owner_dashboard_view, name='owner_dashboard'),
    path('health/', health_view, name='health'),
    path('api/teachers/services/request/', TeacherServiceRequestView.as_view(), name='teacher_service_request'),

    # ─── Notifications Broadcast ──────────────────────────────────────────────
    # المدرس يبعت إشعار لطلابه
    path('api/notifications/teacher-broadcast/', TeacherBroadcastView.as_view(), name='teacher_broadcast'),
    # صاحب المنصة يبعت إشعار للكل أو لمحددين
    path('api/notifications/platform-broadcast/', PlatformBroadcastView.as_view(), name='platform_broadcast'),

    # ─── Exams ────────────────────────────────────────────────────────────────
    # المدرس يصحح الأسئلة المقالية لتسليم معين
    path('api/exams/submissions/<int:submission_id>/grade-essay/', GradeEssayView.as_view(), name='grade-essay'),
    # المدرس يرى كل تسليمات امتحان معين
    path('api/exams/<int:exam_id>/submissions/', AllSubmissionsView.as_view(), name='exam-submissions'),
    # ─── Courses — Detail, Activation Codes, Progress ──────────────────────────
    # صفحة تفاصيل الكورس (للطالب): بيانات الكورس + أرقام التواصل للدفع
    path('api/courses/<int:course_id>/detail/', CourseDetailPublicView.as_view(), name='course-detail'),
    # المدرس ينشئ أكواد تفعيل جديدة (max 25 في المرة)
    path('api/courses/<int:course_id>/generate-codes/', GenerateCodesView.as_view(), name='course-generate-codes'),
    # المدرس يرى قائمة الأكواد مع حالتها
    path('api/courses/<int:course_id>/codes/', ListCodesView.as_view(), name='course-list-codes'),
    # الطالب يدخل كود التفعيل → اشتراك 35 يوم
    path('api/courses/redeem/', RedeemCodeView.as_view(), name='course-redeem'),
    # المدرس يرى تبويب تقدم الطلاب في الكورس
    path('api/courses/<int:course_id>/student-progress/', CourseStudentProgressView.as_view(), name='course-student-progress'),
]
