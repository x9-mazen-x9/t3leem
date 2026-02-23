"""
نظام الإشعارات - Views
- NotificationViewSet: عرض إشعارات المستخدم + تعليم بالقراءة
- TeacherBroadcastView: المدرس يبعت رسالة لطلابه (كل أو محددين)
- PlatformBroadcastView: صاحب المنصة يبعت لكل المستخدمين أو محددين
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsPlatformOwner, IsVerifiedTeacher
from apps.users.models import User
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'تم التعليم بالقراءة'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'تم التعليم بالقراءة للكل'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class TeacherBroadcastView(APIView):
    """
    POST /api/notifications/teacher-broadcast/
    المدرس يبعت إشعار لطلابه.

    Body:
    {
        "title": "...",
        "message": "...",
        "student_ids": [1, 2, 3]  // اختياري، لو مش بعت = كل الطلاب
    }

    يشترط أن يكون المدرس:
    - موثق
    - اشتراكه ساري
    """
    permission_classes = [IsAuthenticated, IsVerifiedTeacher]

    def post(self, request):
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher:
            return Response(
                {'detail': 'فقط المدرسون يمكنهم إرسال إشعارات.'},
                status=status.HTTP_403_FORBIDDEN
            )

        title = request.data.get('title', '').strip()
        message = request.data.get('message', '').strip()
        student_ids = request.data.get('student_ids', None)

        if not title or not message:
            return Response(
                {'detail': 'title و message مطلوبان.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # جلب الطلاب المشتركين الحاليين مع المدرس
        from apps.students.models import Enrollment
        from django.utils import timezone

        active_enrollments = Enrollment.objects.filter(
            course__teacher=teacher,
            is_active=True,
            is_pending=False,
            expiry_date__gte=timezone.now().date(),
        ).select_related('student__user')

        if student_ids:
            active_enrollments = active_enrollments.filter(
                student__id__in=student_ids
            )

        target_users = [e.student.user for e in active_enrollments]

        if not target_users:
            return Response({'detail': 'لا يوجد طلاب لإرسال الإشعار إليهم.'})

        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type='broadcast',
            )
            for user in target_users
        ]
        Notification.objects.bulk_create(notifications)

        return Response({
            'status': 'تم الإرسال',
            'recipients_count': len(notifications),
        })


class PlatformBroadcastView(APIView):
    """
    POST /api/notifications/platform-broadcast/
    صاحب المنصة يبعت إشعار لكل المستخدمين أو لأشخاص محددين.

    Body:
    {
        "title": "...",
        "message": "...",
        "user_ids": [1, 2, 3],  // اختياري، لو مش بعت = كل المستخدمين
        "user_type": "teacher" | "student" | null  // تصفية حسب النوع
    }
    """
    permission_classes = [IsAuthenticated, IsPlatformOwner]

    def post(self, request):
        title = request.data.get('title', '').strip()
        message = request.data.get('message', '').strip()
        user_ids = request.data.get('user_ids', None)
        user_type = request.data.get('user_type', None)

        if not title or not message:
            return Response(
                {'detail': 'title و message مطلوبان.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = User.objects.filter(is_active=True)

        if user_ids:
            qs = qs.filter(id__in=user_ids)

        if user_type in ('teacher', 'student', 'admin'):
            qs = qs.filter(user_type=user_type)

        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type='broadcast',
            )
            for user in qs
        ]
        Notification.objects.bulk_create(notifications)

        return Response({
            'status': 'تم الإرسال',
            'recipients_count': len(notifications),
        })
