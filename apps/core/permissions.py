# apps/core/permissions.py
from rest_framework import permissions

class IsTeacherOwnerOrReadOnly(permissions.BasePermission):
    """
    السماح للمدرس بتعديل وحذف محتواه فقط.
    السماح للطلاب بالقراءة فقط.
    """
    def has_object_permission(self, request, view, obj):
        # القراءة مسموحة للجميع (بعد المصادقة)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # الكتابة مسموحة فقط لمالك المحتوى (المدرس)
        # نفترض أن نموذج الدرس والبوست لديه حقل teacher
        return obj.teacher == request.user.teacher_profile

class IsStudentOwnerOrReadOnly(permissions.BasePermission):
    """
    للتعليقات: الطالب يحذف تعليقه هو فقط.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # التحقق: هل المستخدم هو صاحب التعليق؟
        # أين يتم التحقق؟ هنا نتحقق من تطابق الـ IDs
        return obj.user == request.user