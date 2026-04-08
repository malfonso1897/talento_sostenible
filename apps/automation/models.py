from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Workflow(TimeStampedModel):
    """Workflow automatizado."""
    TRIGGER_CHOICES = [
        ("lead_created", "Nuevo lead creado"),
        ("lead_status_changed", "Lead cambia de estado"),
        ("opportunity_created", "Nueva oportunidad creada"),
        ("opportunity_stage_changed", "Oportunidad cambia de etapa"),
        ("contact_created", "Nuevo contacto creado"),
        ("activity_completed", "Actividad completada"),
        ("ticket_created", "Nuevo ticket creado"),
        ("scheduled", "Programado (cron)"),
    ]
    ACTION_CHOICES = [
        ("send_email", "Enviar email"),
        ("create_activity", "Crear actividad"),
        ("assign_user", "Asignar usuario"),
        ("update_field", "Actualizar campo"),
        ("create_notification", "Crear notificación"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES, verbose_name="Disparador")
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name="Acción")
    action_config = models.JSONField(default=dict, blank=True, verbose_name="Configuración de acción")
    conditions = models.JSONField(default=dict, blank=True, verbose_name="Condiciones")
    execution_count = models.PositiveIntegerField(default=0, verbose_name="Veces ejecutado")
    last_executed = models.DateTimeField(null=True, blank=True, verbose_name="Última ejecución")

    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"

    def __str__(self):
        return f"{self.name} ({self.get_trigger_display()})"


class WorkflowLog(models.Model):
    """Registro de ejecuciones de workflows."""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="logs")
    executed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True)
    affected_object_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Log de workflow"
        verbose_name_plural = "Logs de workflows"
        ordering = ["-executed_at"]

    def __str__(self):
        return f"{self.workflow.name} - {'OK' if self.success else 'ERROR'} ({self.executed_at})"
