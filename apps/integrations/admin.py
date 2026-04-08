from django.contrib import admin
from .models import SyncLog


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "records_synced", "created_at")
    list_filter = ("service", "status")
    readonly_fields = ("service", "status", "records_synced", "details", "error_message", "created_at")
