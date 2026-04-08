from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import SyncLog
from . import macos_calendar, macos_contacts, macos_phone, macos_files


@login_required
def integrations_dashboard(request):
    logs = SyncLog.objects.all()[:20]
    return render(request, "integrations/dashboard.html", {"logs": logs})


@login_required
def sync_calendar(request):
    if request.method == "POST":
        try:
            events = macos_calendar.get_today_events()
            SyncLog.objects.create(
                service="calendar", status="success",
                records_synced=len(events),
                details=f"Eventos de hoy obtenidos: {len(events)}",
                created_by=request.user,
            )
            messages.success(request, f"Calendario sincronizado: {len(events)} eventos de hoy.")
        except Exception as e:
            SyncLog.objects.create(
                service="calendar", status="error",
                error_message=str(e), created_by=request.user,
            )
            messages.error(request, f"Error al sincronizar calendario: {e}")
    return redirect("integrations:dashboard")


@login_required
def sync_contacts(request):
    if request.method == "POST":
        try:
            from apps.contacts.models import Contact
            contacts = Contact.objects.filter(status="customer")
            synced = 0
            for contact in contacts:
                success, _ = macos_contacts.create_macos_contact(
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    email=contact.email,
                    phone=contact.phone,
                    company=contact.company.name if contact.company else "",
                )
                if success:
                    synced += 1

            SyncLog.objects.create(
                service="contacts", status="success",
                records_synced=synced,
                details=f"Contactos exportados a Contactos.app: {synced}",
                created_by=request.user,
            )
            messages.success(request, f"{synced} contactos sincronizados con Contactos.app.")
        except Exception as e:
            SyncLog.objects.create(
                service="contacts", status="error",
                error_message=str(e), created_by=request.user,
            )
            messages.error(request, f"Error al sincronizar contactos: {e}")
    return redirect("integrations:dashboard")


@login_required
def make_call(request, phone_number):
    success, error = macos_phone.make_phone_call(phone_number)
    if success:
        messages.success(request, f"Llamada iniciada a {phone_number}.")
    else:
        messages.error(request, f"No se pudo iniciar la llamada: {error}")
    return redirect(request.META.get("HTTP_REFERER", "/dashboard/"))


@login_required
def entity_files(request, entity_type, entity_id):
    files = macos_files.list_files(entity_type, str(entity_id))
    return render(request, "integrations/entity_files.html", {
        "files": files, "entity_type": entity_type, "entity_id": entity_id,
    })


@login_required
def upload_file(request, entity_type, entity_id):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded = request.FILES["file"]
        path = macos_files.save_file(entity_type, str(entity_id), uploaded)
        messages.success(request, f"Archivo '{uploaded.name}' guardado.")
        return redirect("integrations:entity_files", entity_type=entity_type, entity_id=entity_id)
    messages.error(request, "No se recibió ningún archivo.")
    return redirect("integrations:entity_files", entity_type=entity_type, entity_id=entity_id)


@login_required
def open_finder(request, entity_type, entity_id):
    macos_files.open_in_finder(entity_type, str(entity_id))
    messages.success(request, "Carpeta abierta en Finder.")
    return redirect(request.META.get("HTTP_REFERER", "/dashboard/"))


@login_required
def open_finder_root(request):
    import subprocess
    from django.conf import settings
    import os
    path = os.path.expanduser(settings.CRM_FILES_DIR)
    os.makedirs(path, exist_ok=True)
    subprocess.Popen(["open", path])
    messages.success(request, "Carpeta raíz abierta en Finder.")
    return redirect("integrations:dashboard")
