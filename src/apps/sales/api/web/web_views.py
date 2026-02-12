from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAgent

from apps.sales.api.views import (
    SellRechargeAPIView,
    ConfirmRechargeAPIView,
)
from apps.sales.api.receipt_views import ReceiptAPIView
from apps.sales.api.reissue_views import ReissueReceiptAPIView
from apps.sales.api.agent_transactions_views import AgentTransactionsAPIView
from apps.sales.api.catalog_views import PublicCatalogAPIView, AgentCatalogAPIView
from apps.sales.api.receipt_preview_views import AdminReceiptPreviewAPIView, AgentReceiptPreviewAPIView


class WebSellRechargeAPIView(SellRechargeAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebConfirmRechargeAPIView(ConfirmRechargeAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebReceiptAPIView(ReceiptAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebReissueReceiptAPIView(ReissueReceiptAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentTransactionsAPIView(AgentTransactionsAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAdminReceiptPreviewAPIView(AdminReceiptPreviewAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentReceiptPreviewAPIView(AgentReceiptPreviewAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebPublicCatalogAPIView(PublicCatalogAPIView):
    permission_classes = []  # public


class WebAgentCatalogAPIView(AgentCatalogAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]

__all__ = [
    "WebSellRechargeAPIView",
    "WebConfirmRechargeAPIView",
    "WebReceiptAPIView",
    "WebReissueReceiptAPIView",
    "WebAgentTransactionsAPIView",
    "WebAdminReceiptPreviewAPIView",
    "WebAgentReceiptPreviewAPIView",
    "WebPublicCatalogAPIView",
    "WebAgentCatalogAPIView",
]
