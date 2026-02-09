from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_published', 'created_at', 'order')
    list_filter = ('is_published', 'teacher', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_published', 'order')