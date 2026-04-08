from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Activity(TimeStampedModel):
    """Actividad comercial: llamada, email, reunión, tarea."""
    TYPE_CHOICES = [
        ("call", "Llamada"),
        ("email", "Email"),
        ("meeting", "Reunión"),
        ("task", "Tarea"),
        ("note", "Nota"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
    ]

    activity_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Tipo")
    subject = models.CharField(max_length=255, verbose_name="Asunto")
    description = models.TextField(blank=True, verbose_name="Descripción")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha/Hora")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="Duración (min)")
    is_completed = models.BooleanField(default=False, verbose_name="Completada")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha completada")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="Prioridad")

    # Relaciones
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name="Contacto"
    )
    company = models.ForeignKey(
        "contacts.Company", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name="Empresa"
    )
    lead = models.ForeignKey(
        "leads.Lead", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name="Lead"
    )
    opportunity = models.ForeignKey(
        "opportunities.Opportunity", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name="Oportunidad"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_activities", verbose_name="Asignado a"
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.subject}"
