from django.db import models
from apps.core.models import TimeStampedModel


class SyncLog(TimeStampedModel):
    """Registro de sincronizaciones con apps de macOS."""
    SERVICE_CHOICES = [
        ("calendar", "Calendario"),
        ("contacts", "Contactos"),
        ("phone", "Teléfono"),
        ("files", "Archivos"),
        ("email", "Mail"),
    ]
    STATUS_CHOICES = [
        ("success", "Éxito"),
        ("error", "Error"),
        ("partial", "Parcial"),
    ]

    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, verbose_name="Servicio")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Estado")
    records_synced = models.PositiveIntegerField(default=0, verbose_name="Registros sincronizados")
    details = models.TextField(blank=True, verbose_name="Detalles")
    error_message = models.TextField(blank=True, verbose_name="Error")

    class Meta:
        verbose_name = "Log de sincronización"
        verbose_name_plural = "Logs de sincronización"

    def __str__(self):
        return f"{self.get_service_display()} - {self.status} ({self.created_at})"
