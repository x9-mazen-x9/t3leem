from django.contrib import admin
from .models import Course, Unit


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'price', 'access_type', 'has_trial', 'is_published', 'created_at']
    list_filter = ['access_type', 'is_published', 'has_trial']
    search_fields = ['title', 'teacher__user__email']
    list_editable = ['is_published', 'access_type', 'price']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'has_unit_exam']
    list_filter = ['has_unit_exam', 'course']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']
