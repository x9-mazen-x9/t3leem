# apps/social/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, F, IntegerField, ExpressionWrapper
from django.db import transaction
from .models import Post, TrendingPost

@shared_task
def calculate_trending_posts():
    """
    مهمة خلفية (Background Task) تعمل كل 5 دقائق.
    تحسب التفاعل خلال آخر 24 ساعة وتقوم بتحديث جدول TrendingPost بالكامل.
    """
    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    query = Post.objects.annotate(
        recent_likes=Count(
            'likes', 
            filter=Q(likes__created_at__gte=last_24h), 
            distinct=True
        ),
        recent_comments=Count(
            'comments', 
            filter=Q(comments__created_at__gte=last_24h), 
            distinct=True
        )
    ).annotate(
        calculated_score=ExpressionWrapper(
            (F('recent_likes') * 1) + (F('recent_comments') * 2) + (F('share_count') * 3),
            output_field=IntegerField()
        )
    ).filter(
        # لجعل العملية أسرع، نأخذ فقط المنشورات التي لها سكور في آخر 24 ساعة
        calculated_score__gt=0
    )

    with transaction.atomic():
        # نمسح السجلات القديمة بالكامل بتعليمة SQL واحدة سريعة جداً
        TrendingPost.objects.all().delete()
        
        # نجهز المنشورات الجديدة للإدخال (Bulk Insert)
        # نستخدم iterator() لكي لا نملأ الذاكرة (RAM) إذا كان العدد كبيراً جداً
        trending_objects = []
        for post in query.iterator(chunk_size=2000):
            trending_objects.append(
                TrendingPost(
                    post_id=post.id,
                    score=post.calculated_score,
                    post_created_at=post.created_at,  # ← أهم تعديل
                    calculated_at=now
                )
            )
        
        # إدخالها دفعة واحدة
        if trending_objects:
            TrendingPost.objects.bulk_create(trending_objects, batch_size=2000)
