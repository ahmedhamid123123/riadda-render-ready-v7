from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAgent

from apps.accounts.api.views import LoginAPIView, LogoutAPIView
from apps.accounts.api.admin_views import AdminAgentsListAPIView, ToggleAgentStatusAPIView
from apps.accounts.api.reports_views import DailyReportAPIView, MonthlyReportAPIView, YearlyReportAPIView
from apps.accounts.api.agent_views import AgentProfileAPIView
from apps.accounts.api.agent_transactions import AgentTransactionsAPIView
from apps.accounts.api.balance_views import AgentBalanceAPIView
from apps.accounts.api.daily_summary_views import AgentDailySummaryAPIView
from apps.accounts.api.system_health import SystemHealthAPIView


class WebAgentProfileAPIView(AgentProfileAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentTransactionsAPIView(AgentTransactionsAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentBalanceAPIView(AgentBalanceAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebAgentDailySummaryAPIView(AgentDailySummaryAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]


class WebSystemHealthAPIView(SystemHealthAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAgent]

__all__ = [
    "WebAgentProfileAPIView",
    "WebAgentTransactionsAPIView",
    "WebAgentBalanceAPIView",
    "WebAgentDailySummaryAPIView",
    "WebSystemHealthAPIView",
]
