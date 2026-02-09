from django.contrib import admin
from .models import Teacher, Partner

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at')
    search_fields = ('user__email', 'user__first_name')
    raw_id_fields = ('user',) 

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'revenue_share_percentage')
    list_filter = ('teacher',)