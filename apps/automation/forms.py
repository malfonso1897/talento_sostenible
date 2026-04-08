from django import forms
from .models import Workflow


class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ["name", "description", "trigger", "action", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
