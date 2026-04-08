from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ActivityViewSet

router = DefaultRouter()
router.register("", ActivityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
