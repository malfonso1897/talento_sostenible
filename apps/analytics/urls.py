from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.analytics_dashboard, name="analytics_dashboard"),
    path("sales/", views.sales_report, name="sales_report"),
    path("leads/", views.leads_report, name="leads_report"),
    path("activities/", views.activities_report, name="activities_report"),
    path("forecast/", views.forecast_view, name="forecast"),
]
