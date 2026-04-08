from rest_framework import viewsets
from .models import Activity
from .serializers import ActivitySerializer


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related("contact", "assigned_to").all()
    serializer_class = ActivitySerializer
    filterset_fields = ["activity_type", "is_completed", "priority", "assigned_to"]
    search_fields = ["subject", "description"]
    ordering_fields = ["due_date", "created_at"]
