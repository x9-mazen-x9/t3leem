from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'unit', 'order',
        'is_trial', 'is_force_open', 'has_homework',
        'is_published', 'publish_date'
    ]
    list_filter = [
        'is_trial', 'is_force_open', 'has_homework',
        'is_published', 'course'
    ]
    list_editable = ['is_force_open', 'is_trial', 'is_published']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']
    raw_id_fields = ['course', 'unit', 'teacher']