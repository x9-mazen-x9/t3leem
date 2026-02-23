# apps/exams/models.py
from django.db import models
from django.core.exceptions import ValidationError
from apps.lessons.models import Lesson


class Exam(models.Model):
    """
    امتحان مرتبط بدرس — يحتوي على أسئلة MCQ و/أو مقالية.
    """
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='exam',
        verbose_name='الدرس'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان الامتحان')
    description = models.TextField(blank=True, verbose_name='وصف')
    duration_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name='مدة الامتحان (دقائق)'
    )
    pass_score = models.PositiveIntegerField(
        default=50,
        help_text='درجة النجاح (نسبة مئوية)',
        verbose_name='درجة النجاح %'
    )
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'امتحان'
        verbose_name_plural = 'الامتحانات'

    def __str__(self):
        return f"امتحان: {self.title}"

    @property
    def has_essay_questions(self):
        return self.questions.filter(question_type='essay').exists()

    @property
    def total_marks(self):
        return self.questions.aggregate(
            total=models.Sum('marks')
        )['total'] or 0


class Question(models.Model):
    """
    سؤال داخل الامتحان — MCQ أو مقالي.
    """
    QUESTION_TYPES = [
        ('mcq', 'اختيار من متعدد'),
        ('essay', 'مقالي'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='الامتحان'
    )
    text = models.TextField(verbose_name='نص السؤال')
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default='mcq',
        verbose_name='نوع السؤال'
    )
    marks = models.PositiveIntegerField(default=1, verbose_name='الدرجات')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:60]}"


class Choice(models.Model):
    """
    خيار لسؤال MCQ.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='السؤال'
    )
    text = models.CharField(max_length=500, verbose_name='نص الخيار')
    is_correct = models.BooleanField(default=False, verbose_name='الإجابة الصحيحة')

    class Meta:
        verbose_name = 'خيار'
        verbose_name_plural = 'الخيارات'

    def __str__(self):
        return f"{'✅' if self.is_correct else '❌'} {self.text[:50]}"


class ExamSubmission(models.Model):
    """
    تسليم الطالب للامتحان — حالة واحدة لكل طالب/امتحان.
    """
    STATUS_CHOICES = [
        ('in_progress', 'جارٍ'),
        ('submitted', 'تم التسليم'),
        ('graded', 'تم التصحيح'),
        ('pending_manual_grading', 'في انتظار التصحيح اليدوي'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='الامتحان'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_submissions',
        verbose_name='الطالب'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='الحالة'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت البدء')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت التسليم')

    # النتيجة
    mcq_score = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        verbose_name='درجة MCQ'
    )
    essay_score = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        verbose_name='درجة المقالي'
    )
    total_score = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        verbose_name='الدرجة الكلية'
    )
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='النسبة المئوية'
    )
    passed = models.BooleanField(default=False, verbose_name='ناجح')

    class Meta:
        unique_together = ('exam', 'student')
        verbose_name = 'تسليم امتحان'
        verbose_name_plural = 'تسليمات الامتحانات'
        indexes = [
            models.Index(fields=['exam', 'student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student} — {self.exam} [{self.status}]"

    def calculate_final_result(self):
        """
        حساب النتيجة النهائية:
        - لو فيه أسئلة مقالية: نستنى التصحيح اليدوي
        - لو MCQ فقط: نتيجة فورية
        """
        from django.utils import timezone

        total_marks = self.exam.total_marks
        if total_marks == 0:
            return

        # MCQ أُتيح تلقائياً عند submit
        if self.exam.has_essay_questions:
            # لو فيه أسئلة مقالية لسه ما اتصححتش
            ungraded_essays = self.answers.filter(
                question__question_type='essay',
                essay_score__isnull=True
            ).count()
            if ungraded_essays > 0:
                self.status = 'pending_manual_grading'
                self.save(update_fields=['status'])
                return

        # كل حاجة اتصحت
        essay_total = self.answers.filter(
            question__question_type='essay'
        ).aggregate(
            s=models.Sum('essay_score')
        )['s'] or 0

        self.essay_score = essay_total
        self.total_score = self.mcq_score + self.essay_score
        self.percentage = (self.total_score / total_marks) * 100
        self.passed = self.percentage >= self.exam.pass_score
        self.status = 'graded'
        self.submitted_at = timezone.now()
        self.save(update_fields=[
            'essay_score', 'total_score', 'percentage',
            'passed', 'status', 'submitted_at'
        ])


class Answer(models.Model):
    """
    إجابة الطالب على سؤال واحد.
    """
    submission = models.ForeignKey(
        ExamSubmission,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='التسليم'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='السؤال'
    )

    # MCQ: الخيار المختار
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='الخيار المختار'
    )

    # Essay: النص المكتوب
    essay_text = models.TextField(blank=True, verbose_name='إجابة مقالية')

    # التصحيح اليدوي للمقالي
    essay_score = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        verbose_name='درجة المقالي (يدوي)'
    )
    teacher_feedback = models.TextField(
        blank=True,
        verbose_name='ملاحظة المدرس'
    )

    # MCQ تصحيح تلقائي
    is_correct = models.BooleanField(null=True, verbose_name='صحيحة')

    class Meta:
        unique_together = ('submission', 'question')
        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'

    def auto_grade_mcq(self):
        """تصحيح MCQ تلقائياً."""
        if self.question.question_type == 'mcq' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
            self.save(update_fields=['is_correct'])
