# apps/social/serializers.py
from rest_framework import serializers
from .models import Post, Comment, PostImage, Report


class CommentSerializer(serializers.ModelSerializer):
    commenter_name = serializers.SerializerMethodField()
    commenter_type = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'commenter_name', 'commenter_type', 'created_at']
        read_only_fields = ['commenter_name', 'commenter_type', 'created_at']

    def get_commenter_name(self, obj):
        return obj.commenter_name

    def get_commenter_type(self, obj):
        return obj.commenter_type


class PostImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'url']

    def get_url(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer للمنشور — يدعم كاتب مدرس أو طالب.
    """
    author_name = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()
    author_verified = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    share_count = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField()
    remaining_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'image',
            'created_at',
            'author_name',
            'author_type',
            'author_verified',
            'comments',
            'likes_count',
            'share_count',
            'images',
            'remaining_count',
        ]
        read_only_fields = [
            'author_name', 'author_type', 'author_verified',
            'created_at', 'likes_count', 'share_count',
            'images', 'remaining_count',
        ]

    def get_author_name(self, obj):
        return obj.author_name

    def get_author_type(self, obj):
        return obj.author_type

    def get_author_verified(self, obj):
        if obj.author_teacher:
            return obj.author_teacher.is_verified_paid or obj.author_teacher.is_verified_auto
        return False

    def get_likes_count(self, obj):
        # يدعم annotated value أو الـ count مباشرة
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.likes.count()

    def get_images(self, obj):
        qs = obj.images.all().order_by('created_at')[:4]
        return PostImageSerializer(qs, many=True).data

    def get_remaining_count(self, obj):
        count = obj.images.count()
        return max(0, count - 4)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'reason', 'details', 'created_at']
        read_only_fields = ['created_at']
