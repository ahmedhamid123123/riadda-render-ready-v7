from django.urls import path

from apps.sales.api.pos.pos_views import (
    PosAgentCatalogAPIView,
    PosSellRechargeAPIView,
    PosAgentSalesTransactionsAPIView,
    PosConfirmRechargeAPIView,
    PosReceiptAPIView,
    PosReceiptPreviewAPIView,
)

urlpatterns = [
    path("catalog/", PosAgentCatalogAPIView.as_view(), name="pos-catalog"),
    path("sell/", PosSellRechargeAPIView.as_view(), name="pos-sell"),
    path("transactions/", PosAgentSalesTransactionsAPIView.as_view(), name="pos-transactions"),

    # Optional flow endpoints used by POS UI
    path("confirm/", PosConfirmRechargeAPIView.as_view(), name="pos-confirm"),
    path("receipt/", PosReceiptAPIView.as_view(), name="pos-receipt"),
    path("receipt/preview/", PosReceiptPreviewAPIView.as_view(), name="pos-receipt-preview"),
]
