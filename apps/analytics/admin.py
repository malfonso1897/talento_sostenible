from django.contrib import admin
from .models import Report, Dashboard


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "report_type", "owner", "is_favorite", "created_at")
    list_filter = ("report_type", "is_favorite")


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_default", "created_at")
