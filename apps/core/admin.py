from django.contrib import admin
from .models import AuditLog, Tag, Attachment, Note


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "model_name", "object_id", "timestamp")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("description", "user__email")
    readonly_fields = ("user", "action", "model_name", "object_id", "description", "ip_address", "timestamp", "changes")
    date_hierarchy = "timestamp"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "related_model", "created_at")
    list_filter = ("content_type", "related_model")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("content", "related_model", "is_pinned", "created_at")
    list_filter = ("is_pinned", "related_model")
