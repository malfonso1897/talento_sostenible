from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Lead
from .forms import LeadForm


@login_required
def lead_list(request):
    queryset = Lead.objects.select_related("assigned_to", "campaign").all()
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    source = request.GET.get("source", "")

    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(email__icontains=search) | Q(company_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if source:
        queryset = queryset.filter(source=source)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "leads": page,
        "search": search,
        "status_choices": Lead.STATUS_CHOICES,
        "source_choices": Lead.SOURCE_CHOICES,
    }
    if request.htmx:
        return render(request, "leads/partials/lead_table.html", context)
    return render(request, "leads/lead_list.html", context)


@login_required
def lead_create(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            form.save_m2m()
            messages.success(request, f"Lead {lead.full_name} creado correctamente.")
            return redirect("leads:lead_detail", pk=lead.pk)
    else:
        form = LeadForm()
    return render(request, "leads/lead_form.html", {"form": form, "title": "Nuevo Lead"})


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead.objects.select_related("assigned_to", "campaign"), pk=pk)
    from apps.activities.models import Activity
    activities = Activity.objects.filter(lead=lead).order_by("-due_date")[:10]
    return render(request, "leads/lead_detail.html", {"lead": lead, "activities": activities})


@login_required
def lead_edit(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead actualizado.")
            return redirect("leads:lead_detail", pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    return render(request, "leads/lead_form.html", {"form": form, "title": "Editar Lead", "lead": lead})


@login_required
def lead_convert(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        contact, company = lead.convert_to_contact(user=request.user)
        messages.success(request, f"Lead convertido a contacto: {contact.full_name}")
        return redirect("contacts:contact_detail", pk=contact.pk)
    return render(request, "leads/lead_convert.html", {"lead": lead})


@login_required
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        lead.delete()
        messages.success(request, "Lead eliminado.")
        return redirect("leads:lead_list")
    return render(request, "leads/lead_confirm_delete.html", {"lead": lead})
