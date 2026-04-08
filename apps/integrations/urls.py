from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [
    path("", views.integrations_dashboard, name="dashboard"),
    path("calendar/sync/", views.sync_calendar, name="sync_calendar"),
    path("contacts/sync/", views.sync_contacts, name="sync_contacts"),
    path("phone/call/<str:phone_number>/", views.make_call, name="make_call"),
    path("files/<str:entity_type>/<uuid:entity_id>/", views.entity_files, name="entity_files"),
    path("files/<str:entity_type>/<uuid:entity_id>/upload/", views.upload_file, name="upload_file"),
    path("files/<str:entity_type>/<uuid:entity_id>/open-finder/", views.open_finder, name="open_finder"),
    path("open-finder/", views.open_finder_root, name="open_finder_root"),
]
