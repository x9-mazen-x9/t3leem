# apps/teachers/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from apps.teachers.models import Teacher, Follow, Service, ServiceRequest
from apps.teachers.serializers import TeacherMiniSerializer

@method_decorator(cache_page(60 * 5), name="list")
class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherMiniSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Teacher.objects
            .select_related("user")
            .annotate(follower_count=Count('followers', distinct=True))
        )

    def list(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        qs = self.get_queryset()

        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(bio__icontains=q)
            )

        # نقطة 17: ترتيب الظهور
        # 1. أولوية الظهور (مدفوعة)
        # 2. توثيق تلقائي (5000 متابع)
        # 3. توثيق مدفوع
        # 4. عدد المتابعين
        qs = qs.order_by(
            '-priority_service',   
            '-is_verified_auto',   
            '-is_verified_paid',   
            '-follower_count',
            '-created_at'
        )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # باقي الدوال (follow, stats) تظل كما هي
    # ...
    def follow(self, request, pk=None):
        """
        متابعة / إلغاء متابعة مدرس.
        يرجع: { following: bool, followers_count: int }
        """
        teacher = self.get_object()
        user = request.user

        try:
            follow_obj, created = Follow.objects.get_or_create(user=user, teacher=teacher)
        except IntegrityError:
            created = False
            follow_obj = Follow.objects.get(user=user, teacher=teacher)

        if not created:
            follow_obj.delete()
            following = False
        else:
            following = True
            # التحقق التلقائي عند وصول 5000 متابع
            _check_auto_verify(teacher)

        followers_count = Follow.objects.filter(teacher=teacher).count()
        return Response({
            "following": following,
            "followers_count": followers_count,
        })

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="stats"
    )
    def stats(self, request, pk=None):
        """
        إحصائيات المدرس — بدون قائمة المتابعين (خصوصية).
        """
        teacher = self.get_object()
        followers_count = Follow.objects.filter(teacher=teacher).count()

        # عدد المتابَعين (من يتابعهم هذا المدرس — غير متاح حالياً)
        # نرجع فقط followers_count
        return Response({
            "followers_count": followers_count,
            "is_verified_paid": teacher.is_verified_paid,
            "is_verified_auto": teacher.is_verified_auto,
            "priority_service": teacher.priority_service,
        })


def _check_auto_verify(teacher):
    """
    تحقق تلقائي عند وصول المدرس لـ 5000 متابع.
    يُستدعى بعد كل متابعة جديدة.
    """
    if not teacher.is_verified_auto:
        count = Follow.objects.filter(teacher=teacher).count()
        if count >= 5000:
            Teacher.objects.filter(pk=teacher.pk).update(is_verified_auto=True)


class TeacherServiceRequestView(APIView):
    """
    المدرس يطلب خدمة (توثيق مدفوع / أولوية بحث).
    يتم التفعيل يدوياً من لوحة الإدارة.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {"detail": "هذه العملية متاحة للمدرسين فقط."},
                status=status.HTTP_403_FORBIDDEN
            )
        teacher = request.user.teacher_profile
        code = request.data.get('service_code')
        if not code:
            return Response(
                {"detail": "service_code مطلوب."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = Service.objects.get(code__iexact=code)
        except Service.DoesNotExist:
            return Response(
                {"detail": "الخدمة غير موجودة."},
                status=status.HTTP_404_NOT_FOUND
            )

        ServiceRequest.objects.create(teacher=teacher, service=service, status='pending')
        return Response({
            "status": "pending",
            "message": "يرجى التواصل مع الإدارة للدفع لإتمام تفعيل الخدمة.",
            "duration_days": service.duration_days,
            "price_egp": str(service.price_egp),
        }, status=status.HTTP_201_CREATED)
