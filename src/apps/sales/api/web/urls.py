from django.urls import path

from apps.sales.api.web.web_views import (
    WebSellRechargeAPIView,
    WebConfirmRechargeAPIView,
    WebReceiptAPIView,
    WebReissueReceiptAPIView,
    WebAgentTransactionsAPIView,
    WebAdminReceiptPreviewAPIView,
    WebAgentReceiptPreviewAPIView,
    WebPublicCatalogAPIView,
    WebAgentCatalogAPIView,
)

urlpatterns = [
    path("sell/", WebSellRechargeAPIView.as_view(), name="web-api-sell"),
    path("confirm/<int:transaction_id>/", WebConfirmRechargeAPIView.as_view(), name="web-api-confirm"),

    path("receipt/<uuid:token>/", WebReceiptAPIView.as_view(), name="web-api-receipt"),
    path("receipt/reissue/<int:transaction_id>/", WebReissueReceiptAPIView.as_view(), name="web-api-reissue-receipt"),

    path("agent/transactions/", WebAgentTransactionsAPIView.as_view(), name="web-api-agent-transactions"),

    path("agent/transactions/<int:transaction_id>/receipt-preview/", WebAgentReceiptPreviewAPIView.as_view(), name="web-api-agent-receipt-preview"),
    path("admin/transactions/<int:transaction_id>/receipt-preview/", WebAdminReceiptPreviewAPIView.as_view(), name="web-api-admin-receipt-preview"),

    path("public/catalog/", WebPublicCatalogAPIView.as_view(), name="web-api-public-catalog"),
    path("catalog/", WebAgentCatalogAPIView.as_view(), name="web-api-agent-catalog"),
]
