from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Lead
        fields = "__all__"
