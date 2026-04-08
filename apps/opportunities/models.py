from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Opportunity(TimeStampedModel):
    """Oportunidad de venta - Pipeline comercial."""
    STAGE_CHOICES = [
        ("prospecting", "Prospección"),
        ("qualification", "Cualificación"),
        ("proposal", "Propuesta"),
        ("negotiation", "Negociación"),
        ("closed_won", "Cerrada - Ganada"),
        ("closed_lost", "Cerrada - Perdida"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nombre de la oportunidad")
    company = models.ForeignKey(
        "contacts.Company", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="opportunities", verbose_name="Empresa"
    )
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="opportunities", verbose_name="Contacto"
    )
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="prospecting", verbose_name="Etapa")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Valor (€)")
    probability = models.IntegerField(default=0, verbose_name="Probabilidad (%)")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="Prioridad")
    expected_close_date = models.DateField(null=True, blank=True, verbose_name="Fecha esperada de cierre")
    closed_date = models.DateField(null=True, blank=True, verbose_name="Fecha de cierre real")
    description = models.TextField(blank=True, verbose_name="Descripción")
    loss_reason = models.TextField(blank=True, verbose_name="Motivo de pérdida")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_opportunities", verbose_name="Asignado a"
    )
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")

    class Meta:
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"

    def __str__(self):
        return f"{self.name} - {self.get_stage_display()} ({self.amount}€)"

    @property
    def weighted_value(self):
        return (self.amount * self.probability) / 100
