from django.urls import path

from .agent_profile import AgentProfileAPIView
from .balance_views import AgentBalanceAPIView
from .agent_transactions import AgentTransactionsAPIView
from .daily_summary_views import AgentDailySummaryAPIView
from .auth_views import AgentLoginAPIView

urlpatterns = [
    path("agent/login/", AgentLoginAPIView.as_view(), name="app-api-agent-login"),
    path("agent/profile/", AgentProfileAPIView.as_view(), name="app-api-agent-profile"),
    path("agent/balance/", AgentBalanceAPIView.as_view(), name="app-api-agent-balance"),
    path("agent/transactions/", AgentTransactionsAPIView.as_view(), name="app-api-agent-transactions"),
    path("agent/summary/daily/", AgentDailySummaryAPIView.as_view(), name="app-api-agent-daily-summary"),
]
