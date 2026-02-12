from django.urls import path

from apps.accounts.api.views import LoginAPIView, LogoutAPIView
from apps.accounts.api.auth_views import AgentLoginAPIView
from apps.accounts.api.admin_views import AdminAgentsListAPIView, ToggleAgentStatusAPIView
from apps.accounts.api.reports_views import DailyReportAPIView, MonthlyReportAPIView, YearlyReportAPIView

from apps.accounts.api.web.web_views import (
    WebAgentProfileAPIView,
    WebAgentTransactionsAPIView,
    WebAgentBalanceAPIView,
    WebAgentDailySummaryAPIView,
    WebSystemHealthAPIView,
)

urlpatterns = [
    # Auth (keep defaults)
    path("login/", LoginAPIView.as_view(), name="web-api-login"),
    path("logout/", LogoutAPIView.as_view(), name="web-api-logout"),
    path("agent/login/", AgentLoginAPIView.as_view(), name="web-api-agent-login"),

    # Admin APIs (reuse admin-only views)
    path("admin/agents/", AdminAgentsListAPIView.as_view(), name="web-api-admin-agents"),
    path("admin/agents/<int:agent_id>/toggle/", ToggleAgentStatusAPIView.as_view(), name="web-api-admin-agent-toggle"),

    path("admin/reports/daily/", DailyReportAPIView.as_view(), name="web-api-admin-report-daily"),
    path("admin/reports/monthly/", MonthlyReportAPIView.as_view(), name="web-api-admin-report-monthly"),
    path("admin/reports/yearly/", YearlyReportAPIView.as_view(), name="web-api-admin-report-yearly"),

    # Agent APIs (wrapped to allow admin OR agent)
    path("agent/profile/", WebAgentProfileAPIView.as_view(), name="web-api-agent-profile"),
    path("agent/balance/", WebAgentBalanceAPIView.as_view(), name="web-api-agent-balance"),
    path("agent/transactions/", WebAgentTransactionsAPIView.as_view(), name="web-api-agent-transactions"),
    path("agent/summary/daily/", WebAgentDailySummaryAPIView.as_view(), name="web-api-agent-daily-summary"),

    # System
    path("system/ping/", WebSystemHealthAPIView.as_view(), name="web-api-system-health"),
]
