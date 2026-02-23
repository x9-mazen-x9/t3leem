# apps/social/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Comment, Report, PostLike, SavedPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author', 'author_type', 'share_count', 'created_at', 'reports_count')
    search_fields = ('title', 'content', 'author_teacher__user__email', 'author_student__user__email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'share_count')
    ordering = ('-created_at',)
    actions = ['delete_selected_posts']

    def get_author(self, obj):
        return obj.author_name
    get_author.short_description = 'الكاتب'

    def author_type(self, obj):
        return obj.author_type
    author_type.short_description = 'النوع'

    def reports_count(self, obj):
        count = obj.reports.filter(resolved=False).count()
        if count > 0:
            return format_html('<span style="color:red; font-weight:bold;">{} بلاغ</span>', count)
        return '—'
    reports_count.short_description = 'بلاغات معلقة'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_commenter', 'post', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'student__user__email', 'teacher_author__user__email')

    def get_commenter(self, obj):
        return obj.commenter_name
    get_commenter.short_description = 'المعلق'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    لوحة تحكم صاحب المنصة — إدارة البلاغات.
    يمكن مراجعة البلاغ، حذف المنشور، وتمييز البلاغ كـ "محلول".
    """
    list_display = (
        'get_post_title',
        'get_reporter',
        'reason',
        'created_at',
        'resolved',
        'delete_post_action',
    )
    list_filter = ('resolved', 'reason', 'created_at')
    search_fields = ('post__title', 'user__email', 'details')
    readonly_fields = ('post', 'user', 'reason', 'details', 'created_at')
    ordering = ('-created_at',)
    actions = ['mark_resolved', 'delete_reported_posts']

    def get_post_title(self, obj):
        url = reverse('admin:social_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    get_post_title.short_description = 'المنشور'

    def get_reporter(self, obj):
        return obj.user.email
    get_reporter.short_description = 'المبلغ'

    def delete_post_action(self, obj):
        url = reverse('admin:social_post_delete', args=[obj.post.id])
        return format_html(
            '<a href="{}" style="color:red; font-weight:bold;">🗑 حذف المنشور</a>',
            url
        )
    delete_post_action.short_description = 'إجراء'

    @admin.action(description='✅ تمييز البلاغات المحددة كمحلولة')
    def mark_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f"تم تمييز {updated} بلاغ كمحلول.")

    @admin.action(description='🗑 حذف المنشورات المُبلَّغ عنها')
    def delete_reported_posts(self, request, queryset):
        post_ids = queryset.values_list('post_id', flat=True).distinct()
        from .models import Post as PostModel
        deleted_count = PostModel.objects.filter(id__in=post_ids).delete()[0]
        queryset.update(resolved=True)
        self.message_user(request, f"تم حذف {deleted_count} منشور وتمييز بلاغاتها كمحلولة.")