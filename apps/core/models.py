import uuid
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """Modelo base con timestamps automáticos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(class)s_created",
        verbose_name="Creado por",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class AuditLog(models.Model):
    """Registro de auditoría de todas las acciones del sistema."""
    ACTION_CHOICES = [
        ("CREATE", "Creación"),
        ("UPDATE", "Actualización"),
        ("DELETE", "Eliminación"),
        ("VIEW", "Visualización"),
        ("EXPORT", "Exportación"),
        ("LOGIN", "Inicio de sesión"),
        ("LOGOUT", "Cierre de sesión"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, verbose_name="Modelo")
    object_id = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, blank=True, verbose_name="Cambios")

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} ({self.timestamp})"


class Tag(TimeStampedModel):
    """Etiquetas globales reutilizables."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Color")

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"

    def __str__(self):
        return self.name


class Attachment(TimeStampedModel):
    """Archivos adjuntos para cualquier entidad del CRM."""
    file = models.FileField(upload_to="attachments/%Y/%m/", verbose_name="Archivo")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(default=0, verbose_name="Tamaño (bytes)")
    # Generic relation
    related_model = models.CharField(max_length=100, verbose_name="Modelo relacionado")
    related_id = models.UUIDField(verbose_name="ID relacionado")
    description = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Archivo adjunto"
        verbose_name_plural = "Archivos adjuntos"

    def __str__(self):
        return self.name


class Note(TimeStampedModel):
    """Notas asociadas a cualquier entidad."""
    content = models.TextField(verbose_name="Contenido")
    related_model = models.CharField(max_length=100, verbose_name="Modelo relacionado")
    related_id = models.UUIDField(verbose_name="ID relacionado")
    is_pinned = models.BooleanField(default=False, verbose_name="Fijada")

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self):
        return f"Nota: {self.content[:50]}"
