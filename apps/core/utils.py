# apps/core/utils.py
from apps.core.models import ActivityLog

def log_activity(user, action, description=""):
    """
    تسجيل نشاط المستخدم في قاعدة البيانات.
    """
    if not user or not user.is_authenticated:
        return None
        
    return ActivityLog.objects.create(
        user=user,
        action=action,
        description=description
    )
