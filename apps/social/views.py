# apps/social/views.py
from rest_framework import viewsets, exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Count, Prefetch, F
from django.db import transaction
from .models import Post, Comment, PostImage, PostLike, Report, SavedPost
from .serializers import PostSerializer, CommentSerializer, ReportSerializer
from apps.core.permissions import (
    IsTeacherOwnerOrReadOnly,
    IsStudentOwnerOrReadOnly,
    IsPlatformOwner,
    CanCreatePost,
)


# ==============================
# Post ViewSet
# ==============================

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Post.objects
            .select_related("author_teacher__user", "author_student__user")
            .prefetch_related(
                "likes",
                Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related(
                        "student__user", "teacher_author__user"
                    )
                ),
                Prefetch(
                    "images",
                    queryset=PostImage.objects.all()
                )
            )
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated(), CanCreatePost()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'teacher_profile'):
            serializer.save(author_teacher=user.teacher_profile, teacher=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            serializer.save(author_student=user.student_profile, teacher=None)
        else:
            raise exceptions.PermissionDenied("يجب أن تكون مدرساً أو طالباً لإنشاء منشور.")

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user

        # صاحب المنصة يمسح أي منشور
        if user.is_superuser:
            post.delete()
            return Response({"detail": "تم حذف المنشور بنجاح."}, status=status.HTTP_200_OK)

        # المدرس يمسح منشوره فقط
        if hasattr(user, 'teacher_profile') and post.author_teacher == user.teacher_profile:
            post.delete()
            return Response({"detail": "تم حذف المنشور."}, status=status.HTTP_200_OK)

        # الطالب يمسح منشوره فقط
        if hasattr(user, 'student_profile') and post.author_student == user.student_profile:
            post.delete()
            return Response({"detail": "تم حذف المنشور."}, status=status.HTTP_200_OK)

        raise exceptions.PermissionDenied("لا يمكنك حذف هذا المنشور.")

    # ── Like / Unlike ───────────────────────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """إعجاب/إلغاء إعجاب."""
        # المدرس منتهي الاشتراك لا يمكنه الإعجاب
        if hasattr(request.user, 'teacher_profile'):
            from django.utils import timezone
            profile = request.user.teacher_profile
            today = timezone.now().date()
            if not profile.subscription_expiry or profile.subscription_expiry < today:
                return Response(
                    {'detail': 'حسابك متجمد. جدد اشتراكك لتتفاعل.'},
                    status=403
                )

        post = self.get_object()
        like_obj, created = PostLike.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            like_obj.delete()
            liked = False
        else:
            liked = True

        return Response({
            "liked": liked,
            "likes_count": post.likes.count(),
        })

    # ── Share ────────────────────────────────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        post = self.get_object()
        with transaction.atomic():
            post.share_count = F("share_count") + 1
            post.save(update_fields=["share_count"])
            post.refresh_from_db()
        return Response({"share_count": post.share_count})

    # ── Report ───────────────────────────────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """
        أي مستخدم يبلّغ عن منشور.
        صاحب المنصة يرى البلاغات في الـ Admin ويقرر الحذف.
        """
        post = self.get_object()
        user = request.user

        # منع البلاغ المكرر
        if Report.objects.filter(post=post, user=user).exists():
            return Response(
                {"detail": "لقد أرسلت بلاغاً على هذا المنشور من قبل."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=user)

        return Response(
            {"detail": "تم إرسال البلاغ. سيراجعه فريق الإدارة."},
            status=status.HTTP_201_CREATED
        )

    # ── Save / Unsave ────────────────────────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def save_post(self, request, pk=None):
        """حفظ/إلغاء حفظ المنشور."""
        post = self.get_object()
        user = request.user
        saved, created = SavedPost.objects.get_or_create(user=user, post=post)
        if not created:
            saved.delete()
            return Response({"saved": False})
        return Response({"saved": True})


# ==============================
# Comment ViewSet
# ==============================

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Comment.objects
            .select_related(
                "student__user",
                "teacher_author__user",
                "post"
            )
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            serializer.save(student=user.student_profile)
        elif hasattr(user, 'teacher_profile'):
            serializer.save(teacher_author=user.teacher_profile)
        else:
            raise exceptions.PermissionDenied("يجب أن تكون مدرساً أو طالباً للتعليق.")

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user

        # صاحب المنصة
        if user.is_superuser:
            comment.delete()
            return Response({"detail": "تم حذف التعليق."})

        # الطالب يمسح تعليقه
        if hasattr(user, 'student_profile') and comment.student == user.student_profile:
            comment.delete()
            return Response({"detail": "تم حذف التعليق."})

        # المدرس يمسح تعليقه
        if hasattr(user, 'teacher_profile') and comment.teacher_author == user.teacher_profile:
            comment.delete()
            return Response({"detail": "تم حذف التعليق."})

        raise exceptions.PermissionDenied("لا يمكنك حذف هذا التعليق.")
