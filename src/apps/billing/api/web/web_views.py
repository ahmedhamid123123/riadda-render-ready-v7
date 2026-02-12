from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAgent

from apps.billing.api.views import AgentBalanceAPIView
from apps.billing.api.admin_views import AdjustAgentBalanceAPIView, AgentBalanceDetailAPIView


class WebAgentBalanceAPIView(AgentBalanceAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAdjustAgentBalanceAPIView(AdjustAgentBalanceAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentBalanceDetailAPIView(AgentBalanceDetailAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


__all__ = [
    "WebAgentBalanceAPIView",
    "WebAdjustAgentBalanceAPIView",
    "WebAgentBalanceDetailAPIView",
]
