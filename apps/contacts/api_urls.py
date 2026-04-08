from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ContactViewSet, CompanyViewSet

router = DefaultRouter()
router.register("contacts", ContactViewSet)
router.register("companies", CompanyViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
