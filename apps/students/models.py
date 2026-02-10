from django.db import models
from apps.users.models import User
from apps.teachers.models import Teacher

class Student(models.Model):
    """
    بيانات الطالب الشخصية فقط.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    
    def __str__(self):
        return f"الطالب: {self.user.get_full_name()}"

    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلاب'


class Enrollment(models.Model):
    """
    نموذج الاشتراك: يربط الطالب بمدرس معين.
    هنا نحدد هل الاشتراك مفعل أم لا.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='enrolled_students')
    
    # حالة الاشتراك: مفعل (True) أو في الانتظار (False)
    is_active = models.BooleanField(default=False, verbose_name='تم تفعيل الاشتراك')
    
    # يمكننا إضافة تاريخ الاشتراك
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الاشتراك')
    
    class Meta:
        # لضمان عدم تكرار اشتراك الطالب مع نفس المدرس أكثر من مرة
        unique_together = ('student', 'teacher') 
        verbose_name = 'اشتراك'
        verbose_name_plural = 'قائمة الاشتراكات'

    def __str__(self):
        status = "مفعل" if self.is_active else "قيد الانتظار"
        return f"{self.student.user.email} -> {self.teacher.user.email} ({status})"