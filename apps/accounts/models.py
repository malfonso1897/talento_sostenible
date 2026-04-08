import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario personalizado del CRM."""
    ROLE_CHOICES = [
        ("admin", "Administrador"),
        ("crm_manager", "CRM Manager"),
        ("sales_manager", "Sales Manager"),
        ("sales_rep", "Comercial"),
        ("marketing_manager", "Marketing Manager"),
        ("support_agent", "Agente de Soporte"),
        ("viewer", "Solo Lectura"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="sales_rep", verbose_name="Rol")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Avatar")
    department = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    timezone = models.CharField(max_length=50, default="Europe/Madrid", verbose_name="Zona horaria")
    language = models.CharField(max_length=10, default="es", verbose_name="Idioma")

    # Notifications
    email_notifications = models.BooleanField(default=True, verbose_name="Notificaciones por email")
    browser_notifications = models.BooleanField(default=True, verbose_name="Notificaciones del navegador")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_manager(self):
        return self.role in ("admin", "crm_manager", "sales_manager", "marketing_manager")


class Team(models.Model):
    """Equipos de trabajo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="led_teams", verbose_name="Líder")
    members = models.ManyToManyField(User, blank=True, related_name="teams", verbose_name="Miembros")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return self.name
