from django.urls import path
from . import views

app_name = "automation"

urlpatterns = [
    path("", views.workflow_list, name="workflow_list"),
    path("create/", views.workflow_create, name="workflow_create"),
    path("<uuid:pk>/", views.workflow_detail, name="workflow_detail"),
    path("<uuid:pk>/edit/", views.workflow_edit, name="workflow_edit"),
    path("<uuid:pk>/toggle/", views.workflow_toggle, name="workflow_toggle"),
    path("<uuid:pk>/delete/", views.workflow_delete, name="workflow_delete"),
]
