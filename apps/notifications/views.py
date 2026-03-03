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
from uuid import uuid4

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

        from apps.students.models import Enrollment
        from django.utils import timezone
        from apps.notifications.tasks import fanout_teacher_broadcast

        today = timezone.now().date()
        base_qs = Enrollment.objects.filter(
            course__teacher=teacher,
            is_active=True,
            is_pending=False,
            expiry_date__gte=today,
        )
        if student_ids:
            base_qs = base_qs.filter(student_id__in=student_ids)

        recipients_count = (
            base_qs.values_list("student__user_id", flat=True)
            .distinct()
            .count()
        )
        if recipients_count == 0:
            return Response({'detail': 'لا يوجد طلاب لإرسال الإشعار إليهم.'})

        broadcast_id = str(uuid4())
        async_result = fanout_teacher_broadcast.delay(
            teacher_id=teacher.id,
            title=title,
            message=message,
            broadcast_id=broadcast_id,
            student_ids=student_ids if isinstance(student_ids, list) else None,
        )

        return Response(
            {
                "status": "queued",
                "broadcast_id": broadcast_id,
                "task_id": async_result.id,
                "recipients_count": recipients_count,
            },
            status=status.HTTP_202_ACCEPTED,
        )


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

        from apps.notifications.tasks import fanout_platform_broadcast

        qs = User.objects.filter(is_active=True)
        if user_ids:
            qs = qs.filter(id__in=user_ids)
        if user_type in ('teacher', 'student', 'admin'):
            qs = qs.filter(user_type=user_type)

        recipients_count = qs.count()
        if recipients_count == 0:
            return Response({"detail": "لا يوجد مستخدمون لإرسال الإشعار إليهم."}, status=400)

        broadcast_id = str(uuid4())
        async_result = fanout_platform_broadcast.delay(
            title=title,
            message=message,
            broadcast_id=broadcast_id,
            user_ids=user_ids if isinstance(user_ids, list) else None,
            user_type=user_type,
        )

        return Response(
            {
                "status": "queued",
                "broadcast_id": broadcast_id,
                "task_id": async_result.id,
                "recipients_count": recipients_count,
            },
            status=status.HTTP_202_ACCEPTED,
        )
