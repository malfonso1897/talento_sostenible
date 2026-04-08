from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="contact_list"),
    path("create/", views.contact_create, name="contact_create"),
    path("<uuid:pk>/", views.contact_detail, name="contact_detail"),
    path("<uuid:pk>/edit/", views.contact_edit, name="contact_edit"),
    path("<uuid:pk>/delete/", views.contact_delete, name="contact_delete"),
    path("companies/", views.company_list, name="company_list"),
    path("companies/create/", views.company_create, name="company_create"),
    path("companies/<uuid:pk>/", views.company_detail, name="company_detail"),
    path("companies/<uuid:pk>/edit/", views.company_edit, name="company_edit"),
]
