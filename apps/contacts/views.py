from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Contact, Company
from .forms import ContactForm, CompanyForm


@login_required
def contact_list(request):
    queryset = Contact.objects.select_related("company", "assigned_to").all()

    # Filtros
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    company_id = request.GET.get("company", "")

    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(email__icontains=search) | Q(phone__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if company_id:
        queryset = queryset.filter(company_id=company_id)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "contacts": page,
        "search": search,
        "status_choices": Contact.STATUS_CHOICES,
        "companies": Company.objects.all().order_by("name"),
    }

    if request.htmx:
        return render(request, "contacts/partials/contact_table.html", context)
    return render(request, "contacts/contact_list.html", context)


@login_required
def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            form.save_m2m()
            messages.success(request, f"Contacto {contact.full_name} creado correctamente.")
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        form = ContactForm()
    return render(request, "contacts/contact_form.html", {"form": form, "title": "Nuevo Contacto"})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact.objects.select_related("company", "assigned_to"), pk=pk)
    from apps.activities.models import Activity
    from apps.opportunities.models import Opportunity

    activities = Activity.objects.filter(contact=contact).order_by("-due_date")[:10]
    opportunities = Opportunity.objects.filter(
        Q(contact=contact) | Q(company=contact.company)
    ).order_by("-created_at")[:5] if contact.company else Opportunity.objects.filter(contact=contact)[:5]

    context = {
        "contact": contact,
        "activities": activities,
        "opportunities": opportunities,
    }
    return render(request, "contacts/contact_detail.html", context)


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Contacto actualizado correctamente.")
            return redirect("contacts:contact_detail", pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    return render(request, "contacts/contact_form.html", {"form": form, "title": "Editar Contacto", "contact": contact})


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contacto eliminado.")
        return redirect("contacts:contact_list")
    return render(request, "contacts/contact_confirm_delete.html", {"contact": contact})


@login_required
def company_list(request):
    queryset = Company.objects.select_related("assigned_to").all()
    search = request.GET.get("q", "")
    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(industry__icontains=search))

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "contacts/company_list.html", {"companies": page, "search": search})


@login_required
def company_create(request):
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, f"Empresa {company.name} creada correctamente.")
            return redirect("contacts:company_detail", pk=company.pk)
    else:
        form = CompanyForm()
    return render(request, "contacts/company_form.html", {"form": form, "title": "Nueva Empresa"})


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company.objects.select_related("assigned_to"), pk=pk)
    contacts = company.contacts.all()
    from apps.opportunities.models import Opportunity
    opportunities = Opportunity.objects.filter(company=company).order_by("-created_at")

    context = {"company": company, "contacts": contacts, "opportunities": opportunities}
    return render(request, "contacts/company_detail.html", context)


@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa actualizada correctamente.")
            return redirect("contacts:company_detail", pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, "contacts/company_form.html", {"form": form, "title": "Editar Empresa", "company": company})
