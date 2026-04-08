from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta


@login_required
def analytics_dashboard(request):
    from apps.opportunities.models import Opportunity
    from apps.leads.models import Lead
    from apps.activities.models import Activity

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        "pipeline_by_stage": Opportunity.objects.values("stage").annotate(
            count=Count("id"), total=Sum("amount")
        ).order_by("stage"),
        "leads_by_source": Lead.objects.values("source").annotate(count=Count("id")).order_by("-count"),
        "leads_by_status": Lead.objects.values("status").annotate(count=Count("id")),
        "monthly_won": Opportunity.objects.filter(
            stage="closed_won", closed_date__gte=month_start
        ).aggregate(count=Count("id"), total=Sum("amount")),
        "monthly_lost": Opportunity.objects.filter(
            stage="closed_lost", closed_date__gte=month_start
        ).aggregate(count=Count("id"), total=Sum("amount")),
        "avg_deal_size": Opportunity.objects.filter(
            stage="closed_won"
        ).aggregate(avg=Avg("amount"))["avg"] or 0,
        "activities_completed": Activity.objects.filter(
            is_completed=True, completed_date__date__gte=month_start
        ).count(),
    }
    return render(request, "analytics/analytics_dashboard.html", context)


@login_required
def sales_report(request):
    from apps.opportunities.models import Opportunity

    period = request.GET.get("period", "month")
    today = timezone.now().date()

    if period == "week":
        start = today - timedelta(days=7)
    elif period == "quarter":
        start = today - timedelta(days=90)
    elif period == "year":
        start = today - timedelta(days=365)
    else:
        start = today.replace(day=1)

    opportunities = Opportunity.objects.filter(created_at__date__gte=start)

    context = {
        "period": period,
        "total_pipeline": opportunities.filter(
            stage__in=["prospecting", "qualification", "proposal", "negotiation"]
        ).aggregate(total=Sum("amount"))["total"] or 0,
        "won": opportunities.filter(stage="closed_won").aggregate(
            count=Count("id"), total=Sum("amount")
        ),
        "lost": opportunities.filter(stage="closed_lost").aggregate(
            count=Count("id"), total=Sum("amount")
        ),
        "by_stage": opportunities.values("stage").annotate(
            count=Count("id"), total=Sum("amount")
        ),
    }
    return render(request, "analytics/sales_report.html", context)


@login_required
def leads_report(request):
    from apps.leads.models import Lead

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        "total_leads": Lead.objects.filter(created_at__date__gte=month_start).count(),
        "by_source": Lead.objects.filter(
            created_at__date__gte=month_start
        ).values("source").annotate(count=Count("id")).order_by("-count"),
        "by_status": Lead.objects.values("status").annotate(count=Count("id")),
        "conversion_rate": _calc_conversion_rate(),
        "avg_score": Lead.objects.aggregate(avg=Avg("score"))["avg"] or 0,
    }
    return render(request, "analytics/leads_report.html", context)


@login_required
def activities_report(request):
    from apps.activities.models import Activity

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        "by_type": Activity.objects.filter(
            created_at__date__gte=month_start
        ).values("activity_type").annotate(count=Count("id")),
        "completed": Activity.objects.filter(
            is_completed=True, completed_date__date__gte=month_start
        ).count(),
        "pending": Activity.objects.filter(is_completed=False).count(),
        "overdue": Activity.objects.filter(
            is_completed=False, due_date__date__lt=today
        ).count(),
    }
    return render(request, "analytics/activities_report.html", context)


@login_required
def forecast_view(request):
    from apps.opportunities.models import Opportunity

    open_opps = Opportunity.objects.filter(
        stage__in=["prospecting", "qualification", "proposal", "negotiation"]
    ).select_related("company", "assigned_to").order_by("expected_close_date")

    total_weighted = sum(opp.weighted_value for opp in open_opps)

    context = {
        "opportunities": open_opps,
        "total_weighted": total_weighted,
        "total_pipeline": open_opps.aggregate(total=Sum("amount"))["total"] or 0,
    }
    return render(request, "analytics/forecast.html", context)


def _calc_conversion_rate():
    from apps.leads.models import Lead
    total = Lead.objects.count()
    if total == 0:
        return 0
    converted = Lead.objects.filter(status="converted").count()
    return round((converted / total) * 100, 1)
