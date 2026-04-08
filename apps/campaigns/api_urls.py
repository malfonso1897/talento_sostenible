from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CampaignViewSet

router = DefaultRouter()
router.register("", CampaignViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
