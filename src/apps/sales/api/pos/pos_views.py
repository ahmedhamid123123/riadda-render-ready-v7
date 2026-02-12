from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsPosAgent

# Reuse existing sales endpoints but enforce POS-only permission.
from apps.sales.api.catalog_views import AgentCatalogAPIView
from apps.sales.api.sell_views import SellRechargeAPIView
from apps.sales.api.agent_transactions_views import AgentTransactionsAPIView
from apps.sales.api.confirm_views import ConfirmRechargeAPIView
from apps.sales.api.receipt_views import ReceiptAPIView
from apps.sales.api.receipt_preview_views import AgentReceiptPreviewAPIView


class PosAgentCatalogAPIView(AgentCatalogAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosSellRechargeAPIView(SellRechargeAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosAgentSalesTransactionsAPIView(AgentTransactionsAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosConfirmRechargeAPIView(ConfirmRechargeAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosReceiptAPIView(ReceiptAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosReceiptPreviewAPIView(AgentReceiptPreviewAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]

__all__ = [
    "PosAgentCatalogAPIView",
    "PosSellRechargeAPIView",
    "PosAgentSalesTransactionsAPIView",
    "PosConfirmRechargeAPIView",
    "PosReceiptAPIView",
    "PosReceiptPreviewAPIView",
]
