from rest_framework import serializers
from .models import Campaign, CampaignMember


class CampaignSerializer(serializers.ModelSerializer):
    roi = serializers.ReadOnlyField()
    leads_count = serializers.ReadOnlyField()

    class Meta:
        model = Campaign
        fields = "__all__"


class CampaignMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMember
        fields = "__all__"
