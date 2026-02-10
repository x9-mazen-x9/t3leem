from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.lessons.models import Lesson

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with test data'

    def handle(self, *args, **options):
        # ---------------------------------------------------------
        # 1. إنشاء المستخدمين (Users) أولاً بدون تحديد الدور
        # ---------------------------------------------------------
        
        # المدرس A
        user_a, created = User.objects.get_or_create(
            email='teacher_a@school.com',
            defaults={
                'first_name': 'Ahmed',
                'last_name': 'Ali'
                # ملاحظة: لم نضع is_teacher لأن الحقل غير موجود في موديل User
            }
        )
        if created:
            user_a.set_password('password123') # تشفير كلمة المرور
            user_a.save()
            self.stdout.write(self.style.SUCCESS('Created User A'))
        else:
            self.stdout.write(self.style.WARNING('User A already exists'))

        # المدرس B
        user_b, created = User.objects.get_or_create(
            email='teacher_b@school.com',
            defaults={
                'first_name': 'Sara',
                'last_name': 'Mohamed'
            }
        )
        if created:
            user_b.set_password('password123')
            user_b.save()
            self.stdout.write(self.style.SUCCESS('Created User B'))
        else:
            self.stdout.write(self.style.WARNING('User B already exists'))

        # الطالب
        user_student, created = User.objects.get_or_create(
            email='student@school.com',
            defaults={
                'first_name': 'Omar',
                'last_name': 'Khaled'
            }
        )
        if created:
            user_student.set_password('password123')
            user_student.save()
            self.stdout.write(self.style.SUCCESS('Created Student User'))
        else:
            self.stdout.write(self.style.WARNING('Student User already exists'))

        # ---------------------------------------------------------
        # 2. ربط المستخدمين بملفاتهم الشخصية (Profiles)
        #    هنا يتم تحديد الدور (Teacher or Student)
        # ---------------------------------------------------------

        # إنشاء Teacher Profile للمستخدم A
        teacher_a, created = Teacher.objects.get_or_create(
            user=user_a,
            defaults={'bio': 'Math Teacher'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Teacher Profile for A'))

        # إنشاء Teacher Profile للمستخدم B
        teacher_b, created = Teacher.objects.get_or_create(
            user=user_b,
            defaults={'bio': 'Science Teacher'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Teacher Profile for B'))

        # إنشاء Student Profile للطالب وربطه بالمدرس A
        student, created = Student.objects.get_or_create(
            user=user_student,
            defaults={'teacher': teacher_a}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Student Profile linked to Teacher A'))

        # ---------------------------------------------------------
        # 3. إنشاء الدروس (Lessons)
        # ---------------------------------------------------------

        lesson, created = Lesson.objects.get_or_create(
            title='Algebra 101',
            defaults={
                'description': 'Intro to Algebra',
                'video_id': 'test_video_id_1',
                'teacher': teacher_a
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Lesson for Teacher A'))
        else:
            self.stdout.write(self.style.WARNING('Lesson already exists'))

        self.stdout.write(self.style.SUCCESS('Data Seeding Process Finished!'))