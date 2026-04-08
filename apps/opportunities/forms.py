from django import forms
from .models import Opportunity


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            "name", "company", "contact", "stage", "amount", "probability",
            "priority", "expected_close_date", "description", "assigned_to",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "amount": forms.NumberInput(attrs={"class": "form-input"}),
            "probability": forms.NumberInput(attrs={"class": "form-input", "min": 0, "max": 100}),
            "expected_close_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
