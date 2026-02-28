from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from apps.teachers.models import Teacher
from apps.students.models import Student
from .permissions import IsPlatformOwner

@api_view(['GET'])
def health_view(request):
    return Response({"status": "ok", "timestamp": timezone.now()})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPlatformOwner])
def owner_dashboard_view(request):
    today = timezone.now().date()
    forty_eight_hours_later = today + timedelta(days=2)
    seven_days_ago = timezone.now() - timedelta(days=7)

    try:
        active_teachers_count = Teacher.objects.filter(
            subscription_expiry__gte=today, is_verified=True
        ).count()
    except Exception:
        active_teachers_count = 0

    from django.conf import settings
    SUBSCRIPTION_PRICE = getattr(settings, 'TEACHER_SUBSCRIPTION_PRICE', 900.0)
    total_revenue = float(active_teachers_count) * SUBSCRIPTION_PRICE

    try:
        urgent_expiries_qs = Teacher.objects.filter(
            subscription_expiry__range=[today, forty_eight_hours_later]
        ).select_related('user')
        urgent_alerts = [
            {
                "teacher_id": t.id,
                "name": getattr(t.user, "get_full_name", lambda: "")(),
                "email": getattr(t.user, "email", None),
                "expiry_date": getattr(t, "subscription_expiry", None),
            }
            for t in urgent_expiries_qs
        ]
    except Exception:
        urgent_alerts = []

    try:
        new_students_count = Student.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
    except Exception:
        new_students_count = 0

    return Response({
        "revenue_stats": {
            "active_teachers": active_teachers_count,
            "estimated_monthly_revenue": total_revenue,
            "currency": "EGP"  # BUG-04 FIX: كانت USD خطأً والأسعار كلها بالجنيه المصري
        },
        "urgent_alerts": urgent_alerts,
        "growth_metrics": {
            "new_students_last_7_days": new_students_count
        }
    })
