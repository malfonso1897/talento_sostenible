from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Report(TimeStampedModel):
    """Informe personalizado."""
    TYPE_CHOICES = [
        ("sales", "Ventas"),
        ("leads", "Leads"),
        ("activities", "Actividades"),
        ("campaigns", "Campañas"),
        ("tickets", "Tickets"),
        ("custom", "Personalizado"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nombre")
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    filters = models.JSONField(default=dict, blank=True, verbose_name="Filtros")
    is_favorite = models.BooleanField(default=False, verbose_name="Favorito")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reports", verbose_name="Propietario"
    )

    class Meta:
        verbose_name = "Informe"
        verbose_name_plural = "Informes"

    def __str__(self):
        return self.name


class Dashboard(TimeStampedModel):
    """Dashboard personalizado del usuario."""
    name = models.CharField(max_length=255, verbose_name="Nombre")
    is_default = models.BooleanField(default=False, verbose_name="Dashboard por defecto")
    layout = models.JSONField(default=list, blank=True, verbose_name="Layout de widgets")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="dashboards", verbose_name="Propietario"
    )

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"

    def __str__(self):
        return self.name
