from .models import AuditLog


class AuditMiddleware:
    """Middleware para registrar acciones de auditoría."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def log_action(user, action, model_name, object_id="", description="", ip_address=None, changes=None):
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            description=description,
            ip_address=ip_address,
            changes=changes or {},
        )
