"""
Access Control Service — قلب نظام الوصول للدروس.

المنطق:
1. لو is_trial = True → أي شخص يدخل (حتى بدون تسجيل)
2. لو الكورس FREE → أي مشترك (enrollment صالح) يدخل أي درس
3. لو SEQUENTIAL:
   - يجب أن يكون enrollment صالح (is_valid_for_access)
   - is_force_open = True → يدخل
   - أول درس في الكورس → يدخل
   - الدرس السابق lesson_completed = True → يدخل
   - غير ذلك → محجوب
"""
from django.utils import timezone
from apps.students.models import Enrollment
from apps.courses.models import Course


def user_can_access_lesson(user, lesson) -> bool:
    """
    يحدد هل المستخدم يمكنه الوصول لهذا الدرس.
    يُستخدم في الـ LessonSerializer ومحرك التقدم.
    """

    # 1) الحصة التجريبية: متاحة للجميع
    if lesson.is_trial:
        return True

    # 2) المستخدم يجب أن يكون طالباً
    if not hasattr(user, 'student_profile'):
        return False

    student = user.student_profile

    # 3) جلب الـ enrollment
    try:
        enrollment = Enrollment.objects.get(
            student=student,
            course=lesson.course
        )
    except Enrollment.DoesNotExist:
        return False

    # 4) الاشتراك لازم يكون صالح (نشط + غير منتهي)
    if not enrollment.is_valid_for_access:
        return False

    # 5) الكورس FREE → يدخل كل الدروس
    if lesson.course.access_type == Course.ACCESS_FREE:
        return True

    # 6) SEQUENTIAL Logic
    # 6a) is_force_open → يدخل حتى لو ما اكتملش اللي قبله
    if lesson.is_force_open:
        return True

    # 6b) أول درس في الكورس → يدخل دائماً
    is_first = not lesson.course.lessons.filter(
        order__lt=lesson.order
    ).exists()
    if is_first:
        return True

    # 6c) تحقق من إتمام الدرس السابق
    previous_lesson = (
        lesson.course.lessons
        .filter(order__lt=lesson.order)
        .order_by('-order')
        .first()
    )
    if previous_lesson is None:
        return True

    # لو الدرس السابق is_force_open → لا يشترط إتمامه
    if previous_lesson.is_force_open:
        return True

    from apps.progress.models import LessonProgress
    try:
        prev_progress = LessonProgress.objects.get(
            student=student,
            lesson=previous_lesson
        )
        return prev_progress.lesson_completed
    except LessonProgress.DoesNotExist:
        return False


def get_next_lesson(lesson):
    """يجيب الدرس الذي يلي الدرس الحالي في نفس الكورس."""
    return (
        lesson.course.lessons
        .filter(order__gt=lesson.order)
        .order_by('order')
        .first()
    )


def get_unlocked_lessons_for_student(student, course):
    """
    يعيد قائمة IDs الدروس المفتوحة للطالب في كورس معين.
    مفيد للـ API لعرض حالة كل درس.
    """
    from apps.progress.models import LessonProgress

    lessons = list(
        course.lessons
        .filter(is_published=True)
        .order_by('order')
    )

    if course.access_type == Course.ACCESS_FREE:
        return [l.id for l in lessons]

    # SEQUENTIAL: نبني قائمة تدريجية
    unlocked_ids = []
    for lesson in lessons:
        if lesson.is_trial or lesson.is_force_open:
            unlocked_ids.append(lesson.id)
            continue

        if not unlocked_ids and not any(
            l.order < lesson.order for l in lessons
        ):
            # أول درس
            unlocked_ids.append(lesson.id)
            continue

        # أول درس فعلياً (order أصغر)
        is_first = True
        for l in lessons:
            if l.order < lesson.order:
                is_first = False
                break
        if is_first:
            unlocked_ids.append(lesson.id)
            continue

        # تحقق من إتمام السابق
        prev_lesson = None
        for l in reversed(lessons):
            if l.order < lesson.order:
                prev_lesson = l
                break

        if prev_lesson is None or prev_lesson.is_force_open:
            unlocked_ids.append(lesson.id)
            continue

        try:
            prog = LessonProgress.objects.get(
                student=student, lesson=prev_lesson
            )
            if prog.lesson_completed:
                unlocked_ids.append(lesson.id)
        except LessonProgress.DoesNotExist:
            pass

    return unlocked_ids
