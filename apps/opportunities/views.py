from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Opportunity
from .forms import OpportunityForm


@login_required
def opportunity_list(request):
    queryset = Opportunity.objects.select_related("company", "contact", "assigned_to").all()
    search = request.GET.get("q", "")
    stage = request.GET.get("stage", "")

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(company__name__icontains=search))
    if stage:
        queryset = queryset.filter(stage=stage)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "opportunities": page,
        "search": search,
        "stage_choices": Opportunity.STAGE_CHOICES,
    }
    if request.htmx:
        return render(request, "opportunities/partials/opportunity_table.html", context)
    return render(request, "opportunities/opportunity_list.html", context)


@login_required
def pipeline_view(request):
    """Vista visual del embudo comercial."""
    stages = {}
    for key, label in Opportunity.STAGE_CHOICES:
        opps = Opportunity.objects.filter(stage=key).select_related("company", "assigned_to")
        stages[key] = {
            "label": label,
            "opportunities": opps,
            "count": opps.count(),
            "total": opps.aggregate(total=Sum("amount"))["total"] or 0,
        }
    return render(request, "opportunities/pipeline.html", {"stages": stages})


@login_required
def opportunity_create(request):
    if request.method == "POST":
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.created_by = request.user
            opp.save()
            form.save_m2m()
            messages.success(request, f"Oportunidad '{opp.name}' creada.")
            return redirect("opportunities:opportunity_detail", pk=opp.pk)
    else:
        form = OpportunityForm()
    return render(request, "opportunities/opportunity_form.html", {"form": form, "title": "Nueva Oportunidad"})


@login_required
def opportunity_detail(request, pk):
    opp = get_object_or_404(Opportunity.objects.select_related("company", "contact", "assigned_to"), pk=pk)
    from apps.activities.models import Activity
    activities = Activity.objects.filter(opportunity=opp).order_by("-due_date")[:10]
    return render(request, "opportunities/opportunity_detail.html", {"opportunity": opp, "activities": activities})


@login_required
def opportunity_edit(request, pk):
    opp = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        form = OpportunityForm(request.POST, instance=opp)
        if form.is_valid():
            form.save()
            messages.success(request, "Oportunidad actualizada.")
            return redirect("opportunities:opportunity_detail", pk=opp.pk)
    else:
        form = OpportunityForm(instance=opp)
    return render(request, "opportunities/opportunity_form.html", {"form": form, "title": "Editar Oportunidad", "opportunity": opp})


@login_required
def opportunity_delete(request, pk):
    opp = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        opp.delete()
        messages.success(request, "Oportunidad eliminada.")
        return redirect("opportunities:opportunity_list")
    return render(request, "opportunities/opportunity_confirm_delete.html", {"opportunity": opp})
