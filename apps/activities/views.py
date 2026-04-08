from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Activity
from .forms import ActivityForm


@login_required
def activity_list(request):
    queryset = Activity.objects.select_related("contact", "assigned_to", "opportunity").all()
    search = request.GET.get("q", "")
    activity_type = request.GET.get("type", "")
    completed = request.GET.get("completed", "")

    if search:
        queryset = queryset.filter(Q(subject__icontains=search) | Q(description__icontains=search))
    if activity_type:
        queryset = queryset.filter(activity_type=activity_type)
    if completed == "yes":
        queryset = queryset.filter(is_completed=True)
    elif completed == "no":
        queryset = queryset.filter(is_completed=False)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "activities": page,
        "search": search,
        "type_choices": Activity.TYPE_CHOICES,
    }
    if request.htmx:
        return render(request, "activities/partials/activity_table.html", context)
    return render(request, "activities/activity_list.html", context)


@login_required
def calendar_view(request):
    """Vista de calendario con las actividades."""
    activities = Activity.objects.filter(
        due_date__isnull=False, is_completed=False
    ).select_related("contact", "assigned_to").order_by("due_date")
    return render(request, "activities/calendar.html", {"activities": activities})


@login_required
def activity_create(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, f"Actividad '{activity.subject}' creada.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm()
    return render(request, "activities/activity_form.html", {"form": form, "title": "Nueva Actividad"})


@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(
        Activity.objects.select_related("contact", "company", "lead", "opportunity", "assigned_to"), pk=pk
    )
    return render(request, "activities/activity_detail.html", {"activity": activity})


@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, "Actividad actualizada.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm(instance=activity)
    return render(request, "activities/activity_form.html", {"form": form, "title": "Editar Actividad", "activity": activity})


@login_required
def activity_complete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        activity.is_completed = True
        activity.completed_date = timezone.now()
        activity.save()
        messages.success(request, "Actividad completada.")
    return redirect("activities:activity_detail", pk=activity.pk)


@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        activity.delete()
        messages.success(request, "Actividad eliminada.")
        return redirect("activities:activity_list")
    return render(request, "activities/activity_confirm_delete.html", {"activity": activity})
