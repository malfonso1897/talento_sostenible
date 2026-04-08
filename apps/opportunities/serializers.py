from rest_framework import serializers
from .models import Opportunity


class OpportunitySerializer(serializers.ModelSerializer):
    weighted_value = serializers.ReadOnlyField()

    class Meta:
        model = Opportunity
        fields = "__all__"
