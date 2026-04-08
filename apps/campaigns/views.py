from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Campaign
from .forms import CampaignForm


@login_required
def campaign_list(request):
    queryset = Campaign.objects.select_related("assigned_to").all()
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {"campaigns": page, "search": search, "status_choices": Campaign.STATUS_CHOICES}
    return render(request, "campaigns/campaign_list.html", context)


@login_required
def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()
            form.save_m2m()
            messages.success(request, f"Campaña '{campaign.name}' creada.")
            return redirect("campaigns:campaign_detail", pk=campaign.pk)
    else:
        form = CampaignForm()
    return render(request, "campaigns/campaign_form.html", {"form": form, "title": "Nueva Campaña"})


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign.objects.select_related("assigned_to"), pk=pk)
    members = campaign.members.select_related("contact").all()
    leads = campaign.leads.all()
    return render(request, "campaigns/campaign_detail.html", {
        "campaign": campaign, "members": members, "leads": leads,
    })


@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, "Campaña actualizada.")
            return redirect("campaigns:campaign_detail", pk=campaign.pk)
    else:
        form = CampaignForm(instance=campaign)
    return render(request, "campaigns/campaign_form.html", {"form": form, "title": "Editar Campaña", "campaign": campaign})


@login_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        campaign.delete()
        messages.success(request, "Campaña eliminada.")
        return redirect("campaigns:campaign_list")
    return render(request, "campaigns/campaign_confirm_delete.html", {"campaign": campaign})
