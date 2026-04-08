from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    path("", views.lead_list, name="lead_list"),
    path("create/", views.lead_create, name="lead_create"),
    path("<uuid:pk>/", views.lead_detail, name="lead_detail"),
    path("<uuid:pk>/edit/", views.lead_edit, name="lead_edit"),
    path("<uuid:pk>/convert/", views.lead_convert, name="lead_convert"),
    path("<uuid:pk>/delete/", views.lead_delete, name="lead_delete"),
]
