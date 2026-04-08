from rest_framework import viewsets
from .models import Ticket
from .serializers import TicketSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("contact", "assigned_to").all()
    serializer_class = TicketSerializer
    filterset_fields = ["status", "priority", "channel", "assigned_to"]
    search_fields = ["subject", "description"]
    ordering_fields = ["priority", "created_at"]
