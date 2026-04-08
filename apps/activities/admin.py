from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("subject", "activity_type", "contact", "due_date", "is_completed", "assigned_to")
    list_filter = ("activity_type", "is_completed", "priority")
    search_fields = ("subject", "description", "contact__first_name", "contact__last_name")
    date_hierarchy = "due_date"
