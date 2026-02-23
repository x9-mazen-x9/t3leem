# apps/exams/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Exam, Question, Choice, ExamSubmission, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['text', 'is_correct']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'marks', 'order']
    show_change_link = True


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'duration_minutes', 'pass_score', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'lesson__title')
    inlines = [QuestionInline]
    readonly_fields = ('created_at', 'updated_at')

    def get_total_marks(self, obj):
        return obj.total_marks
    get_total_marks.short_description = 'إجمالي الدرجات'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'exam', 'question_type', 'marks', 'order')
    list_filter = ('question_type', 'exam')
    search_fields = ('text',)
    inlines = [ChoiceInline]

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'السؤال'


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'student_name', 'exam', 'status',
        'mcq_score', 'essay_score', 'total_score',
        'percentage', 'passed', 'submitted_at'
    )
    list_filter = ('status', 'passed', 'exam')
    search_fields = ('student__user__email', 'exam__title')
    readonly_fields = (
        'exam', 'student', 'started_at', 'submitted_at',
        'mcq_score', 'total_score', 'percentage', 'passed'
    )
    ordering = ('-submitted_at',)

    def student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.email
    student_name.short_description = 'الطالب'

    def get_pending_count(self, request):
        return ExamSubmission.objects.filter(
            status='pending_manual_grading'
        ).count()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pending_count'] = ExamSubmission.objects.filter(
            status='pending_manual_grading'
        ).count()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question_short', 'is_correct', 'essay_score')
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('submission__student__user__email',)

    def question_short(self, obj):
        return obj.question.text[:60]
    question_short.short_description = 'السؤال'
