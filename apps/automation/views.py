from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workflow
from .forms import WorkflowForm


@login_required
def workflow_list(request):
    workflows = Workflow.objects.all()
    return render(request, "automation/workflow_list.html", {"workflows": workflows})


@login_required
def workflow_create(request):
    if request.method == "POST":
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.created_by = request.user
            workflow.save()
            messages.success(request, f"Workflow '{workflow.name}' creado.")
            return redirect("automation:workflow_detail", pk=workflow.pk)
    else:
        form = WorkflowForm()
    return render(request, "automation/workflow_form.html", {"form": form, "title": "Nuevo Workflow"})


@login_required
def workflow_detail(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    logs = workflow.logs.all()[:20]
    return render(request, "automation/workflow_detail.html", {"workflow": workflow, "logs": logs})


@login_required
def workflow_edit(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    if request.method == "POST":
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            messages.success(request, "Workflow actualizado.")
            return redirect("automation:workflow_detail", pk=workflow.pk)
    else:
        form = WorkflowForm(instance=workflow)
    return render(request, "automation/workflow_form.html", {"form": form, "title": "Editar Workflow", "workflow": workflow})


@login_required
def workflow_toggle(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    if request.method == "POST":
        workflow.is_active = not workflow.is_active
        workflow.save()
        state = "activado" if workflow.is_active else "desactivado"
        messages.success(request, f"Workflow {state}.")
    return redirect("automation:workflow_detail", pk=workflow.pk)


@login_required
def workflow_delete(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    if request.method == "POST":
        workflow.delete()
        messages.success(request, "Workflow eliminado.")
        return redirect("automation:workflow_list")
    return render(request, "automation/workflow_confirm_delete.html", {"workflow": workflow})
