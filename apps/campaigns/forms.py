from django import forms
from .models import Campaign


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            "name", "campaign_type", "status", "description",
            "start_date", "end_date", "budget", "expected_revenue",
            "target_audience", "assigned_to",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "target_audience": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "budget": forms.NumberInput(attrs={"class": "form-input"}),
            "expected_revenue": forms.NumberInput(attrs={"class": "form-input"}),
        }
