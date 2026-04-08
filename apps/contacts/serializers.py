from rest_framework import serializers
from .models import Contact, Company


class CompanySerializer(serializers.ModelSerializer):
    contacts_count = serializers.ReadOnlyField()

    class Meta:
        model = Company
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Contact
        fields = "__all__"
