from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    path("", views.campaign_list, name="campaign_list"),
    path("create/", views.campaign_create, name="campaign_create"),
    path("<uuid:pk>/", views.campaign_detail, name="campaign_detail"),
    path("<uuid:pk>/edit/", views.campaign_edit, name="campaign_edit"),
    path("<uuid:pk>/delete/", views.campaign_delete, name="campaign_delete"),
]
