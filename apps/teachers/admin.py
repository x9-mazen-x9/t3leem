from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Teacher, Partner, ServiceRequest

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'subscription_expiry', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('user__email', 'user__first_name')
    raw_id_fields = ('user',)
    actions = ['extend_subscription']

    @admin.action(description='تمديد الاشتراك لمدة 31 يومًا')
    def extend_subscription(self, request, queryset):
        today = timezone.now().date()
        for teacher in queryset:
            if teacher.subscription_expiry and teacher.subscription_expiry >= today:
                teacher.subscription_expiry += timedelta(days=31)
            else:
                teacher.subscription_expiry = today + timedelta(days=31)
            teacher.save()
        self.message_user(request, f"تم تمديد اشتراك {queryset.count()} مدرسين.")

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'revenue_share_percentage')
    list_filter = ('teacher',)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'service', 'status', 'requested_at', 'activated_at', 'expiry_date')
    list_filter = ('status', 'service')
    actions = ['activate_requests', 'reject_requests']

    @admin.action(description='تفعيل الطلبات المحددة (يتطلب مشرف)')
    def activate_requests(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "يجب أن تكون مشرفاً لتفعيل الطلبات.", level=40)
            return
        for req in queryset:
            req.status = 'active'
            req.activated_at = timezone.now()
            duration = req.service.duration_days or 31
            req.expiry_date = req.activated_at.date() + timedelta(days=duration)
            req.save()
        self.message_user(request, f"تم تفعيل {queryset.count()} طلبات.")

    @admin.action(description='رفض الطلبات المحددة')
    def reject_requests(self, request, queryset):
        for req in queryset:
            req.status = 'rejected'
            req.save(update_fields=['status'])
        self.message_user(request, f"تم رفض {queryset.count()} طلبات.")
