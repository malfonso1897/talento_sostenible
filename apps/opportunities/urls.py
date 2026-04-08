from django.urls import path
from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.opportunity_list, name="opportunity_list"),
    path("pipeline/", views.pipeline_view, name="pipeline"),
    path("create/", views.opportunity_create, name="opportunity_create"),
    path("<uuid:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path("<uuid:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("<uuid:pk>/delete/", views.opportunity_delete, name="opportunity_delete"),
]
