from django.db import models
from django.conf import settings

class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantModel(TimeStampedModel):
    teacher = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.CASCADE, 
        related_name='%(class)s_records',
        help_text="المالك الأساسي لهذا السجل"
    )

    class Meta:
        abstract = True