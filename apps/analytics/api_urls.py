from django.urls import path
from .api_views import SalesSummaryAPIView

urlpatterns = [
    path("sales-summary/", SalesSummaryAPIView.as_view(), name="sales_summary_api"),
]
