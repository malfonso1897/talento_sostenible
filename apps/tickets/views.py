from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Ticket
from .forms import TicketForm, TicketCommentForm


@login_required
def ticket_list(request):
    queryset = Ticket.objects.select_related("contact", "assigned_to").all()
    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")

    if search:
        queryset = queryset.filter(Q(subject__icontains=search) | Q(description__icontains=search))
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)

    paginator = Paginator(queryset, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "tickets": page, "search": search,
        "status_choices": Ticket.STATUS_CHOICES,
        "priority_choices": Ticket.PRIORITY_CHOICES,
    }
    return render(request, "tickets/ticket_list.html", context)


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            form.save_m2m()
            messages.success(request, f"Ticket '{ticket.subject}' creado.")
            return redirect("tickets:ticket_detail", pk=ticket.pk)
    else:
        form = TicketForm()
    return render(request, "tickets/ticket_form.html", {"form": form, "title": "Nuevo Ticket"})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related("contact", "company", "assigned_to"), pk=pk)
    comments = ticket.comments.select_related("created_by").all()
    comment_form = TicketCommentForm()
    return render(request, "tickets/ticket_detail.html", {
        "ticket": ticket, "comments": comments, "comment_form": comment_form,
    })


@login_required
def ticket_edit(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket actualizado.")
            return redirect("tickets:ticket_detail", pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket)
    return render(request, "tickets/ticket_form.html", {"form": form, "title": "Editar Ticket", "ticket": ticket})


@login_required
def ticket_add_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.created_by = request.user
            comment.save()
            messages.success(request, "Comentario añadido.")
    return redirect("tickets:ticket_detail", pk=ticket.pk)


@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        ticket.delete()
        messages.success(request, "Ticket eliminado.")
        return redirect("tickets:ticket_list")
    return render(request, "tickets/ticket_confirm_delete.html", {"ticket": ticket})
