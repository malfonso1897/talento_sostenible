from rest_framework import viewsets
from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("assigned_to", "campaign").all()
    serializer_class = LeadSerializer
    filterset_fields = ["status", "source", "priority", "assigned_to"]
    search_fields = ["first_name", "last_name", "email", "company_name"]
    ordering_fields = ["score", "created_at", "priority"]
