from rest_framework import viewsets
from .models import Opportunity
from .serializers import OpportunitySerializer


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.select_related("company", "contact", "assigned_to").all()
    serializer_class = OpportunitySerializer
    filterset_fields = ["stage", "priority", "assigned_to"]
    search_fields = ["name", "company__name"]
    ordering_fields = ["amount", "probability", "created_at"]
