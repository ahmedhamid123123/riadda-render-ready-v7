from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsPosAgent

# Reuse existing agent endpoints but enforce POS-only permission.
from apps.accounts.api.agent_views import AgentProfileAPIView
from apps.accounts.api.balance_views import AgentBalanceAPIView
from apps.accounts.api.agent_transactions import AgentTransactionsAPIView
from apps.accounts.api.daily_summary_views import AgentDailySummaryAPIView


class PosAgentProfileAPIView(AgentProfileAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosAgentBalanceAPIView(AgentBalanceAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosAgentTransactionsAPIView(AgentTransactionsAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


class PosAgentDailySummaryAPIView(AgentDailySummaryAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]
