from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.sales.api import catalog_urls
from apps.sales.api.views_receipt import receipt_html_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home -> admin dashboard
    path("", lambda request: redirect("/accounts/admin/dashboard/")),

    # Web apps
    path("accounts/", include("apps.accounts.urls")),
    path("billing/", include("apps.billing.urls")),
    path("sales/", include("apps.sales.urls")),

    # APIs
    path("api/accounts/", include("apps.accounts.api.urls")),
    path("api/sales/", include("apps.sales.api.urls")),
    path("api/catalog/", include(catalog_urls)),
    path("api/public/", include("apps.sales.api.catalog_urls")),

    # Receipts
    path("receipt/<uuid:token>/", receipt_html_view, name="receipt-html"),

    # OpenAPI (✅ keep private in production)
]

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (render friendly messages and optional details in DEBUG)
handler400 = "config.error_views.bad_request"
handler403 = "config.error_views.permission_denied"
handler404 = "config.error_views.page_not_found"
handler500 = "config.error_views.server_error"
