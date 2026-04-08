from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import OpportunityViewSet

router = DefaultRouter()
router.register("", OpportunityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
