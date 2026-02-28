from rest_framework import serializers
from .models import Lesson
from .services import user_can_access_lesson
from django.conf import settings
from django.utils import timezone
import hashlib
import hmac
from datetime import datetime, timedelta


class LessonListSerializer(serializers.ModelSerializer):
    """خفيف للقوائم - بدون URL الفيديو."""
    is_accessible = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "unit",
            "title",
            "order",
            "is_trial",
            "is_force_open",
            "has_homework",
            "publish_date",
            "is_accessible",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_is_accessible(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return obj.is_trial
        return user_can_access_lesson(request.user, obj)


class LessonSerializer(serializers.ModelSerializer):
    """كامل مع URL الفيديو (للـ retrieve فقط)."""
    video_url = serializers.SerializerMethodField()
    is_accessible = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "unit",
            "title",
            "description",
            "order",
            "is_trial",
            "is_force_open",
            "has_homework",
            "publish_date",
            "video_url",
            "lesson_material",
            "is_accessible",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_is_accessible(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return obj.is_trial
        return user_can_access_lesson(request.user, obj)

    def get_video_url(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            if obj.is_trial:
                # Trial: إرجاع الـ embed URL بدون توقيع
                if obj.bunny_video_id:
                    return obj.embed_url
            return None

        if not user_can_access_lesson(request.user, obj):
            return None

        if not obj.bunny_video_id:
            return None

        # Signed URL
        expiration = int(
            (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        )

        library_id = settings.BUNNY_STREAM_LIBRARY_ID
        api_key = settings.BUNNY_STREAM_API_KEY

        base_url = f"https://iframe.mediadelivery.net/embed/{library_id}/{obj.bunny_video_id}"

        string_to_sign = f"{api_key}{obj.bunny_video_id}{expiration}{request.user.id}"

        # BUG FIX: Bunny Stream Token Auth uses plain SHA256, not HMAC.
        signature = hashlib.sha256(string_to_sign.encode("utf-8")).hexdigest()

        return f"{base_url}?expires={expiration}&signature={signature}&user={request.user.id}"
