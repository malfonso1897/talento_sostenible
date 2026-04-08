from django.contrib import admin
from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "stage", "amount", "probability", "assigned_to", "expected_close_date")
    list_filter = ("stage", "priority", "assigned_to")
    search_fields = ("name", "company__name")
    list_editable = ("stage",)
    date_hierarchy = "created_at"
