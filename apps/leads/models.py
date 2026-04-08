from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Lead(TimeStampedModel):
    """Lead / Prospecto - entrada al pipeline comercial."""
    STATUS_CHOICES = [
        ("new", "Nuevo"),
        ("contacted", "Contactado"),
        ("qualified", "Cualificado"),
        ("unqualified", "No cualificado"),
        ("converted", "Convertido"),
        ("lost", "Perdido"),
    ]
    SOURCE_CHOICES = [
        ("website", "Sitio web"),
        ("referral", "Referencia"),
        ("social_media", "Redes sociales"),
        ("email_campaign", "Campaña de email"),
        ("cold_call", "Llamada en frío"),
        ("event", "Evento"),
        ("advertising", "Publicidad"),
        ("partner", "Partner"),
        ("other", "Otro"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
        ("urgent", "Urgente"),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    company_name = models.CharField(max_length=255, blank=True, verbose_name="Empresa")
    job_title = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    website = models.URLField(blank=True, verbose_name="Web")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Estado")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, verbose_name="Origen")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="Prioridad")

    # AI Scoring
    score = models.IntegerField(default=0, verbose_name="Puntuación (0-100)")
    score_reasons = models.JSONField(default=list, blank=True, verbose_name="Razones del scoring")

    description = models.TextField(blank=True, verbose_name="Descripción")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_leads", verbose_name="Asignado a"
    )
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads", verbose_name="Campaña"
    )
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")

    # Conversión
    converted_contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="from_lead", verbose_name="Contacto convertido"
    )
    converted_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de conversión")

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def convert_to_contact(self, user=None):
        """Convierte el lead en contacto + empresa + oportunidad."""
        from apps.contacts.models import Contact, Company
        from django.utils import timezone

        company = None
        if self.company_name:
            company, _ = Company.objects.get_or_create(
                name=self.company_name,
                defaults={"created_by": user, "phone": self.phone}
            )

        contact = Contact.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            job_title=self.job_title,
            company=company,
            status="prospect",
            created_by=user,
            assigned_to=self.assigned_to,
        )

        self.status = "converted"
        self.converted_contact = contact
        self.converted_date = timezone.now()
        self.save()

        return contact, company
