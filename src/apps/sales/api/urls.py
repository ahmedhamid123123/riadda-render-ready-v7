from django.urls import path

from .views import SellRechargeAPIView, ConfirmRechargeAPIView
from .receipt_views import ReceiptAPIView
from .reissue_views import ReissueReceiptAPIView
from .agent_transactions_views import AgentTransactionsAPIView
from .catalog_views import PublicCatalogAPIView, AgentCatalogAPIView
from .receipt_preview_views import AdminReceiptPreviewAPIView, AgentReceiptPreviewAPIView


urlpatterns = [
    # Core sale flow
    path("sell/", SellRechargeAPIView.as_view(), name="api-sell"),
    path("confirm/<int:transaction_id>/", ConfirmRechargeAPIView.as_view(), name="api-confirm"),

    # Receipt API
    path("receipt/<uuid:token>/", ReceiptAPIView.as_view(), name="api-receipt"),
    path("receipt/reissue/<int:transaction_id>/", ReissueReceiptAPIView.as_view(), name="api-reissue-receipt"),

    # Agent history
    path("agent/transactions/", AgentTransactionsAPIView.as_view(), name="api-agent-transactions"),

    # Receipt preview
    path("agent/transactions/<int:transaction_id>/receipt-preview/", AgentReceiptPreviewAPIView.as_view(), name="api-agent-receipt-preview"),
    path("admin/transactions/<int:transaction_id>/receipt-preview/", AdminReceiptPreviewAPIView.as_view(), name="api-admin-receipt-preview"),

    # Catalog
    path("public/catalog/", PublicCatalogAPIView.as_view(), name="api-public-catalog"),
    path("catalog/", AgentCatalogAPIView.as_view(), name="api-agent-catalog"),
]
