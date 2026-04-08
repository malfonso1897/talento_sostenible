from django.contrib import admin
from .models import Workflow, WorkflowLog


class WorkflowLogInline(admin.TabularInline):
    model = WorkflowLog
    extra = 0
    readonly_fields = ("executed_at", "success", "details", "affected_object_id")


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "action", "is_active", "execution_count", "last_executed")
    list_filter = ("is_active", "trigger", "action")
    search_fields = ("name", "description")
    inlines = [WorkflowLogInline]
