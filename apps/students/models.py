from django.db import models
from apps.users.models import User

class Student(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    
    
    
    
    def __str__(self):
        return f"الطالب: {self.user.get_full_name()}"

    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلاب'