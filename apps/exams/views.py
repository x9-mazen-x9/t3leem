# apps/exams/views.py
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Exam, Question, Choice, ExamSubmission, Answer
from .serializers import (
    ExamSerializer,
    ExamSubmitSerializer,
    SubmissionResultSerializer,
    EssayGradeSerializer,
)
from apps.core.permissions import IsPlatformOwner
from apps.core.utils import log_activity


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    الطالب يرى الامتحانات المتاحة — بدون الإجابات الصحيحة.
    """
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Exam.objects
            .filter(is_active=True)
            .prefetch_related('questions__choices')
            .select_related('lesson')
        )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        الطالب يرسل إجاباته.
        - MCQ: تصحيح فوري تلقائي
        - Essay: في انتظار المدرس
        - MCQ + Essay: في انتظار المدرس لحد ما يصحح المقالي
        """
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {"detail": "هذه العملية للطلاب فقط."},
                status=status.HTTP_403_FORBIDDEN
            )

        exam = self.get_object()
        student = request.user.student_profile

        # منع تقديم أكثر من مرة
        if ExamSubmission.objects.filter(exam=exam, student=student).exists():
            return Response(
                {"detail": "لقد قدمت هذا الامتحان من قبل."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ExamSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers_data = serializer.validated_data['answers']

        with transaction.atomic():
            submission = ExamSubmission.objects.create(
                exam=exam,
                student=student,
                status='submitted',
                submitted_at=timezone.now()
            )

            mcq_score = 0

            for ans in answers_data:
                question_id = ans['question_id']
                try:
                    question = exam.questions.get(id=question_id)
                except Question.DoesNotExist:
                    continue

                answer = Answer(submission=submission, question=question)

                if question.question_type == 'mcq':
                    choice_id = ans.get('selected_choice_id')
                    if choice_id:
                        try:
                            choice = question.choices.get(id=choice_id)
                            answer.selected_choice = choice
                            answer.is_correct = choice.is_correct
                            if choice.is_correct:
                                mcq_score += question.marks
                        except Choice.DoesNotExist:
                            pass

                elif question.question_type == 'essay':
                    answer.essay_text = ans.get('essay_text', '')

                answer.save()

            submission.mcq_score = mcq_score
            submission.save(update_fields=['mcq_score'])

            # حساب النتيجة — لو فيه مقالي هيظل pending
            submission.calculate_final_result()
            
            # log activity
            log_activity(
                user=request.user,
                action="سلم امتحان",
                description=f"سلم امتحان: {exam.title}"
            )

        result = SubmissionResultSerializer(submission).data
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='my-result')
    def my_result(self, request, pk=None):
        """الطالب يشوف نتيجته."""
        if not hasattr(request.user, 'student_profile'):
            return Response({"detail": "للطلاب فقط."}, status=403)
        exam = self.get_object()
        try:
            submission = ExamSubmission.objects.prefetch_related(
                'answers__question', 'answers__selected_choice'
            ).get(exam=exam, student=request.user.student_profile)
        except ExamSubmission.DoesNotExist:
            return Response({"detail": "لم تقدم هذا الامتحان بعد."}, status=404)
        return Response(SubmissionResultSerializer(submission).data)


class GradeEssayView(APIView):
    """
    المدرس يصحح الأسئلة المقالية لتسليم معين.
    يرسل قائمة بالـ answer_id والدرجة.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, submission_id, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            return Response({"detail": "للمدرسين فقط."}, status=403)

        try:
            submission = ExamSubmission.objects.select_related(
                'exam__lesson__teacher'
            ).get(id=submission_id)
        except ExamSubmission.DoesNotExist:
            return Response({"detail": "التسليم غير موجود."}, status=404)

        # التحقق أن المدرس هو صاحب الدرس
        if submission.exam.lesson.teacher != request.user.teacher_profile:
            return Response({"detail": "ليس لديك صلاحية تصحيح هذا الامتحان."}, status=403)

        grades = request.data.get('grades', [])
        with transaction.atomic():
            for grade_data in grades:
                s = EssayGradeSerializer(data=grade_data)
                s.is_valid(raise_exception=True)

                try:
                    answer = submission.answers.get(
                        id=s.validated_data['answer_id'],
                        question__question_type='essay'
                    )
                    answer.essay_score = s.validated_data['essay_score']
                    answer.teacher_feedback = s.validated_data.get('teacher_feedback', '')
                    answer.save(update_fields=['essay_score', 'teacher_feedback'])
                except Answer.DoesNotExist:
                    continue

            # إعادة حساب النتيجة بعد التصحيح
            submission.calculate_final_result()
            
        # log activity
        log_activity(
            user=request.user,
            action="صحح امتحان",
            description=f"صحح الأسئلة المقالية لامتحان {submission.exam.title} للطالب {submission.student.user.get_full_name()}"
        )

        submission.refresh_from_db()
        return Response(SubmissionResultSerializer(submission).data)


class AllSubmissionsView(APIView):
    """
    المدرس يرى تسليمات طلابه لامتحان معين.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            return Response({"detail": "للمدرسين فقط."}, status=403)

        try:
            exam = Exam.objects.select_related('lesson__teacher').get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({"detail": "الامتحان غير موجود."}, status=404)

        if exam.lesson.teacher != request.user.teacher_profile:
            return Response({"detail": "ليس لديك صلاحية عرض هذا الامتحان."}, status=403)

        submissions = (
            ExamSubmission.objects
            .filter(exam=exam)
            .select_related('student__user')
            .prefetch_related('answers__question')
            .order_by('-submitted_at')
        )

        data = []
        for sub in submissions:
            data.append({
                "submission_id": sub.id,
                "student_name": sub.student.user.get_full_name(),
                "student_email": sub.student.user.email,
                "status": sub.status,
                "total_score": sub.total_score,
                "percentage": sub.percentage,
                "passed": sub.passed,
                "submitted_at": sub.submitted_at,
            })

        return Response(data)
