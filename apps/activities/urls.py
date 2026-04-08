from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="activity_list"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("create/", views.activity_create, name="activity_create"),
    path("<uuid:pk>/", views.activity_detail, name="activity_detail"),
    path("<uuid:pk>/edit/", views.activity_edit, name="activity_edit"),
    path("<uuid:pk>/complete/", views.activity_complete, name="activity_complete"),
    path("<uuid:pk>/delete/", views.activity_delete, name="activity_delete"),
]
