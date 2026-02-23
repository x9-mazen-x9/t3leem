from django.contrib import admin
from .models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'lesson', 'watched_percentage',
        'video_completed', 'homework_submitted',
        'lesson_completed', 'updated_at'
    ]
    list_filter = ['video_completed', 'homework_submitted', 'lesson_completed']
    search_fields = ['student__user__email', 'lesson__title']
    readonly_fields = ['lesson_completed', 'updated_at', 'created_at']
