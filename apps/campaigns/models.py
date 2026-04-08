from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Campaign(TimeStampedModel):
    """Campaña de marketing."""
    TYPE_CHOICES = [
        ("email", "Email"),
        ("social", "Redes Sociales"),
        ("event", "Evento"),
        ("advertising", "Publicidad"),
        ("referral", "Referencia"),
        ("other", "Otro"),
    ]
    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("active", "Activa"),
        ("paused", "Pausada"),
        ("completed", "Completada"),
        ("cancelled", "Cancelada"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nombre")
    campaign_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    description = models.TextField(blank=True, verbose_name="Descripción")
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha fin")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Presupuesto (€)")
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Coste real (€)")
    expected_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ingreso esperado (€)")
    target_audience = models.TextField(blank=True, verbose_name="Público objetivo")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_campaigns", verbose_name="Responsable"
    )
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")

    class Meta:
        verbose_name = "Campaña"
        verbose_name_plural = "Campañas"

    def __str__(self):
        return self.name

    @property
    def roi(self):
        if self.actual_cost > 0:
            return ((self.expected_revenue - self.actual_cost) / self.actual_cost) * 100
        return 0

    @property
    def leads_count(self):
        return self.leads.count()


class CampaignMember(TimeStampedModel):
    """Miembros/destinatarios de una campaña."""
    STATUS_CHOICES = [
        ("sent", "Enviado"),
        ("opened", "Abierto"),
        ("clicked", "Click"),
        ("responded", "Respondido"),
        ("converted", "Convertido"),
        ("bounced", "Rebotado"),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="members", verbose_name="Campaña")
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="campaign_memberships", verbose_name="Contacto"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sent", verbose_name="Estado")
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha envío")
    opened_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha apertura")
    clicked_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha click")

    class Meta:
        verbose_name = "Miembro de campaña"
        verbose_name_plural = "Miembros de campaña"
        unique_together = ["campaign", "contact"]

    def __str__(self):
        return f"{self.contact} - {self.campaign}"
