from django.urls import path

from .catalog_views import PublicCatalogAPIView, AgentCatalogAPIView
from .sell_views import SellRechargeAPIView
from .agent_transactions_views import AgentTransactionsAPIView
from .confirm_views import ConfirmRechargeAPIView
from .receipt_views import ReceiptAPIView, ReissueReceiptAPIView

urlpatterns = [
    path("catalog/", AgentCatalogAPIView.as_view(), name="app-catalog"),
    path("public/catalog/", PublicCatalogAPIView.as_view(), name="app-public-catalog"),

    path("sell/", SellRechargeAPIView.as_view(), name="app-sell"),
    path("transactions/", AgentTransactionsAPIView.as_view(), name="app-transactions"),

    path("confirm/", ConfirmRechargeAPIView.as_view(), name="app-confirm"),
    path("receipt/", ReceiptAPIView.as_view(), name="app-receipt"),
    path("receipt/preview/", ReissueReceiptAPIView.as_view(), name="app-receipt-preview"),
]
