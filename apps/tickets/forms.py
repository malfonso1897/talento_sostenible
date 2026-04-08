from django import forms
from .models import Ticket, TicketComment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "subject", "description", "status", "priority", "channel",
            "contact", "company", "assigned_to", "sla_deadline",
        ]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "sla_deadline": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["content", "is_internal"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Escribe un comentario..."}),
        }
