from django.urls import path

# ===== Auth =====
from .views import LoginAPIView, LogoutAPIView
from .auth_views import AgentLoginAPIView

# ===== Admin =====
from .admin_views import AdminAgentsListAPIView, ToggleAgentStatusAPIView
from .reports_views import (
    DailyReportAPIView,
    MonthlyReportAPIView,
    YearlyReportAPIView,
)

# ===== Agent =====
from .agent_views import AgentProfileAPIView
from .agent_transactions import AgentTransactionsAPIView
from .balance_views import AgentBalanceAPIView
from .daily_summary_views import AgentDailySummaryAPIView

# ===== System =====
from .system_health import SystemHealthAPIView


urlpatterns = [

    # =========================
    # Authentication
    # =========================
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("agent/login/", AgentLoginAPIView.as_view(), name="api-agent-login"),

    # =========================
    # Admin APIs
    # =========================
    path(
        "admin/agents/",
        AdminAgentsListAPIView.as_view(),
        name="api-admin-agents"
    ),
    path(
        "admin/agents/<int:agent_id>/toggle/",
        ToggleAgentStatusAPIView.as_view(),
        name="api-admin-agent-toggle"
    ),

    path(
        "admin/reports/daily/",
        DailyReportAPIView.as_view(),
        name="api-admin-report-daily"
    ),
    path(
        "admin/reports/monthly/",
        MonthlyReportAPIView.as_view(),
        name="api-admin-report-monthly"
    ),
    path(
        "admin/reports/yearly/",
        YearlyReportAPIView.as_view(),
        name="api-admin-report-yearly"
    ),

    # =========================
    # Agent APIs (POS)
    # =========================
    path(
        "agent/profile/",
        AgentProfileAPIView.as_view(),
        name="api-agent-profile"
    ),
    path(
        "agent/balance/",
        AgentBalanceAPIView.as_view(),
        name="api-agent-balance"
    ),
    path(
        "agent/transactions/",
        AgentTransactionsAPIView.as_view(),
        name="api-agent-transactions"
    ),
    path(
        "agent/summary/daily/",
        AgentDailySummaryAPIView.as_view(),
        name="api-agent-daily-summary"
    ),

    # =========================
    # System / Health
    # =========================
    path(
        "system/ping/",
        SystemHealthAPIView.as_view(),
        name="api-system-health"
    ),
]
