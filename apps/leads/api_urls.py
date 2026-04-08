from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import LeadViewSet

router = DefaultRouter()
router.register("", LeadViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
