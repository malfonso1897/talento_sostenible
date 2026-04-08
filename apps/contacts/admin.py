from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Company, Contact


@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    list_display = ("name", "industry", "size", "city", "country", "assigned_to", "created_at")
    list_filter = ("industry", "size", "country")
    search_fields = ("name", "email", "city")
    filter_horizontal = ("tags",)


@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "status", "assigned_to", "created_at")
    list_filter = ("status", "company", "country")
    search_fields = ("first_name", "last_name", "email", "phone")
    filter_horizontal = ("tags",)
    raw_id_fields = ("company", "assigned_to")
