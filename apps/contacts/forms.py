from django import forms
from .models import Contact, Company


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "first_name", "last_name", "email", "phone", "mobile",
            "job_title", "company", "status", "address", "city", "country",
            "linkedin", "description", "avatar", "assigned_to", "do_not_call", "do_not_email",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "mobile": forms.TextInput(attrs={"class": "form-input"}),
            "job_title": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name", "industry", "size", "website", "phone", "email",
            "address", "city", "country", "postal_code", "description",
            "annual_revenue", "logo", "assigned_to",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
