from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin):
    list_display = ("first_name", "last_name", "email", "company_name", "status", "source", "score", "priority", "assigned_to")
    list_filter = ("status", "source", "priority", "created_at")
    search_fields = ("first_name", "last_name", "email", "company_name")
    list_editable = ("status", "priority")
    raw_id_fields = ("assigned_to",)
    date_hierarchy = "created_at"
