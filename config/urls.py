from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Frontend views
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("contacts/", include("apps.contacts.urls")),
    path("leads/", include("apps.leads.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
    path("activities/", include("apps.activities.urls")),
    path("campaigns/", include("apps.campaigns.urls")),
    path("automation/", include("apps.automation.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("tickets/", include("apps.tickets.urls")),
    path("integrations/", include("apps.integrations.urls")),

    # API
    path("api/v1/contacts/", include("apps.contacts.api_urls")),
    path("api/v1/leads/", include("apps.leads.api_urls")),
    path("api/v1/opportunities/", include("apps.opportunities.api_urls")),
    path("api/v1/activities/", include("apps.activities.api_urls")),
    path("api/v1/campaigns/", include("apps.campaigns.api_urls")),
    path("api/v1/tickets/", include("apps.tickets.api_urls")),
    path("api/v1/analytics/", include("apps.analytics.api_urls")),

    # API Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
