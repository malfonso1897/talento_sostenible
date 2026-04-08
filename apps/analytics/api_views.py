from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from django.utils import timezone


class SalesSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.opportunities.models import Opportunity

        today = timezone.now().date()
        month_start = today.replace(day=1)

        data = {
            "pipeline": Opportunity.objects.filter(
                stage__in=["prospecting", "qualification", "proposal", "negotiation"]
            ).aggregate(count=Count("id"), total=Sum("amount")),
            "won_this_month": Opportunity.objects.filter(
                stage="closed_won", closed_date__gte=month_start
            ).aggregate(count=Count("id"), total=Sum("amount")),
            "by_stage": list(Opportunity.objects.values("stage").annotate(
                count=Count("id"), total=Sum("amount")
            )),
        }
        return Response(data)
