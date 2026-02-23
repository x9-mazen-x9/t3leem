# apps/exams/serializers.py
from rest_framework import serializers
from .models import Exam, Question, Choice, ExamSubmission, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']
        # نخفي is_correct عن الطالب


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'marks', 'order', 'choices']


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    total_marks = serializers.IntegerField(read_only=True)
    has_essay_questions = serializers.BooleanField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'duration_minutes',
            'pass_score', 'total_marks', 'has_essay_questions', 'questions'
        ]


# ── إجابة الطالب على سؤال واحد ───────────────────────────────────────────────
class AnswerInputSerializer(serializers.Serializer):
    """مستخدم عند submit من الطالب."""
    question_id = serializers.IntegerField()
    selected_choice_id = serializers.IntegerField(required=False, allow_null=True)
    essay_text = serializers.CharField(required=False, allow_blank=True)


class ExamSubmitSerializer(serializers.Serializer):
    """
    الطالب يرسل إجاباته كلها دفعة واحدة.
    """
    answers = AnswerInputSerializer(many=True)


# ── نتيجة التسليم ─────────────────────────────────────────────────────────────
class AnswerResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    max_marks = serializers.IntegerField(source='question.marks', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'question_text', 'question_type', 'max_marks',
            'is_correct', 'essay_score', 'teacher_feedback', 'essay_text'
        ]


class SubmissionResultSerializer(serializers.ModelSerializer):
    answers = AnswerResultSerializer(many=True, read_only=True)

    class Meta:
        model = ExamSubmission
        fields = [
            'id', 'status', 'mcq_score', 'essay_score',
            'total_score', 'percentage', 'passed',
            'started_at', 'submitted_at', 'answers'
        ]


# ── تصحيح المدرس للمقالي ──────────────────────────────────────────────────────
class EssayGradeSerializer(serializers.Serializer):
    """المدرس يصحح الأسئلة المقالية."""
    answer_id = serializers.IntegerField()
    essay_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    teacher_feedback = serializers.CharField(required=False, allow_blank=True)
