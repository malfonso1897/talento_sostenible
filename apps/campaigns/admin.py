from django.contrib import admin
from .models import Campaign, CampaignMember


class CampaignMemberInline(admin.TabularInline):
    model = CampaignMember
    extra = 0
    raw_id_fields = ("contact",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "campaign_type", "status", "start_date", "end_date", "budget", "assigned_to")
    list_filter = ("campaign_type", "status")
    search_fields = ("name", "description")
    inlines = [CampaignMemberInline]
