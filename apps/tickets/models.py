from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Ticket(TimeStampedModel):
    """Ticket de soporte / incidencia."""
    STATUS_CHOICES = [
        ("open", "Abierto"),
        ("in_progress", "En progreso"),
        ("waiting", "Esperando respuesta"),
        ("resolved", "Resuelto"),
        ("closed", "Cerrado"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
        ("critical", "Crítica"),
    ]
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("phone", "Teléfono"),
        ("chat", "Chat"),
        ("web", "Formulario web"),
    ]

    subject = models.CharField(max_length=255, verbose_name="Asunto")
    description = models.TextField(verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="Estado")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="Prioridad")
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="email", verbose_name="Canal")
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", verbose_name="Contacto"
    )
    company = models.ForeignKey(
        "contacts.Company", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", verbose_name="Empresa"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tickets", verbose_name="Asignado a"
    )
    resolved_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha resolución")
    sla_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Plazo SLA")
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"#{self.pk} - {self.subject}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.sla_deadline and self.status not in ("resolved", "closed"):
            return timezone.now() > self.sla_deadline
        return False


class TicketComment(TimeStampedModel):
    """Comentario/respuesta en un ticket."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments", verbose_name="Ticket")
    content = models.TextField(verbose_name="Contenido")
    is_internal = models.BooleanField(default=False, verbose_name="Nota interna")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comentario en {self.ticket}"
