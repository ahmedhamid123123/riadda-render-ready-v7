from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsPosAgent

from apps.billing.api.views import AgentBalanceAPIView


class PosAgentBalanceAPIView(AgentBalanceAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


__all__ = ["PosAgentBalanceAPIView"]
