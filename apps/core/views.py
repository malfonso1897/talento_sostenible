from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta


def home(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return redirect("accounts:login")


@login_required
def dashboard(request):
    from apps.contacts.models import Contact, Company
    from apps.leads.models import Lead
    from apps.opportunities.models import Opportunity
    from apps.activities.models import Activity
    from apps.tickets.models import Ticket

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        "total_contacts": Contact.objects.count(),
        "total_companies": Company.objects.count(),
        "new_leads_month": Lead.objects.filter(created_at__date__gte=month_start).count(),
        "open_opportunities": Opportunity.objects.filter(
            stage__in=["prospecting", "qualification", "proposal", "negotiation"]
        ).count(),
        "pipeline_value": Opportunity.objects.filter(
            stage__in=["prospecting", "qualification", "proposal", "negotiation"]
        ).aggregate(total=Sum("amount"))["total"] or 0,
        "won_this_month": Opportunity.objects.filter(
            stage="closed_won", closed_date__gte=month_start
        ).count(),
        "today_activities": Activity.objects.filter(
            due_date__date=today, is_completed=False
        ).count(),
        "open_tickets": Ticket.objects.filter(
            status__in=["open", "in_progress"]
        ).count(),
        "upcoming_activities": Activity.objects.filter(
            due_date__date__gte=today, is_completed=False
        ).select_related("assigned_to", "contact").order_by("due_date")[:10],
        "recent_leads": Lead.objects.select_related("assigned_to").order_by("-created_at")[:5],
        "recent_opportunities": Opportunity.objects.select_related(
            "company", "assigned_to"
        ).order_by("-updated_at")[:5],
    }
    return render(request, "dashboard.html", context)


@login_required
def global_search(request):
    from apps.contacts.models import Contact, Company
    from apps.leads.models import Lead
    from apps.opportunities.models import Opportunity

    query = request.GET.get("q", "").strip()
    results = {"contacts": [], "companies": [], "leads": [], "opportunities": []}

    if query and len(query) >= 2:
        results["contacts"] = Contact.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )[:10]
        results["companies"] = Company.objects.filter(
            Q(name__icontains=query) | Q(industry__icontains=query)
        )[:10]
        results["leads"] = Lead.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )[:10]
        results["opportunities"] = Opportunity.objects.filter(
            Q(name__icontains=query) | Q(company__name__icontains=query)
        )[:10]

    context = {"query": query, "results": results}

    if request.htmx:
        return render(request, "partials/search_results.html", context)
    return render(request, "search.html", context)
