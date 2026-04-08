from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("create/", views.ticket_create, name="ticket_create"),
    path("<uuid:pk>/", views.ticket_detail, name="ticket_detail"),
    path("<uuid:pk>/edit/", views.ticket_edit, name="ticket_edit"),
    path("<uuid:pk>/comment/", views.ticket_add_comment, name="ticket_add_comment"),
    path("<uuid:pk>/delete/", views.ticket_delete, name="ticket_delete"),
]
