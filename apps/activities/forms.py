from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "activity_type", "subject", "description", "due_date",
            "duration_minutes", "priority", "contact", "company",
            "lead", "opportunity", "assigned_to",
        ]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-input"}),
        }
