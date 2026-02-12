from django.urls import path

from apps.accounts.api.pos.pos_auth_views import PosAgentLoginAPIView
from apps.accounts.api.pos.pos_views import (
    PosAgentProfileAPIView,
    PosAgentBalanceAPIView,
    PosAgentTransactionsAPIView,
    PosAgentDailySummaryAPIView,
)

urlpatterns = [
    path("login/", PosAgentLoginAPIView.as_view(), name="pos-agent-login"),
    path("agent/profile/", PosAgentProfileAPIView.as_view(), name="pos-agent-profile"),
    path("agent/balance/", PosAgentBalanceAPIView.as_view(), name="pos-agent-balance"),
    path("agent/transactions/", PosAgentTransactionsAPIView.as_view(), name="pos-agent-transactions"),
    path("agent/summary/daily/", PosAgentDailySummaryAPIView.as_view(), name="pos-agent-daily-summary"),
]
