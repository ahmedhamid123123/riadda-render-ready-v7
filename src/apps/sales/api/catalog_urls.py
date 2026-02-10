# sales/api/catalog_urls.py
from django.urls import path
from .catalog_views import PublicCatalogAPIView, AgentCatalogAPIView

urlpatterns = [
    path("recharge/", AgentCatalogAPIView.as_view(), name="api-recharge-catalog"),
    path('catalog/', PublicCatalogAPIView.as_view(), name='catalog-api')
]
