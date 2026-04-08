from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    """Empresa / Cuenta."""
    INDUSTRY_CHOICES = [
        ("technology", "Tecnología"),
        ("finance", "Finanzas"),
        ("healthcare", "Salud"),
        ("education", "Educación"),
        ("retail", "Comercio"),
        ("manufacturing", "Manufactura"),
        ("services", "Servicios"),
        ("energy", "Energía"),
        ("real_estate", "Inmobiliario"),
        ("other", "Otro"),
    ]
    SIZE_CHOICES = [
        ("1-10", "1-10 empleados"),
        ("11-50", "11-50 empleados"),
        ("51-200", "51-200 empleados"),
        ("201-500", "201-500 empleados"),
        ("501-1000", "501-1000 empleados"),
        ("1000+", "Más de 1000 empleados"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nombre de la empresa")
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, verbose_name="Sector")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True, verbose_name="Tamaño")
    website = models.URLField(blank=True, verbose_name="Sitio web")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email corporativo")
    address = models.TextField(blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Código postal")
    description = models.TextField(blank=True, verbose_name="Descripción")
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Facturación anual")
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True, verbose_name="Logo")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_companies", verbose_name="Asignado a"
    )
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name

    @property
    def contacts_count(self):
        return self.contacts.count()

    @property
    def opportunities_count(self):
        return self.opportunities.count()


class Contact(TimeStampedModel):
    """Contacto / Persona."""
    STATUS_CHOICES = [
        ("active", "Activo"),
        ("inactive", "Inactivo"),
        ("prospect", "Prospecto"),
        ("customer", "Cliente"),
        ("churned", "Perdido"),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    mobile = models.CharField(max_length=20, blank=True, verbose_name="Móvil")
    job_title = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts", verbose_name="Empresa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="prospect", verbose_name="Estado")
    address = models.TextField(blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    description = models.TextField(blank=True, verbose_name="Notas")
    avatar = models.ImageField(upload_to="contact_avatars/", blank=True, null=True, verbose_name="Foto")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_contacts", verbose_name="Asignado a"
    )
    tags = models.ManyToManyField("core.Tag", blank=True, verbose_name="Etiquetas")
    do_not_call = models.BooleanField(default=False, verbose_name="No llamar")
    do_not_email = models.BooleanField(default=False, verbose_name="No enviar emails")
    last_activity_date = models.DateTimeField(null=True, blank=True, verbose_name="Última actividad")

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        unique_together = ["email", "company"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
