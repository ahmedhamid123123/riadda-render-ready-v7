from django.urls import path

from apps.billing.api.web.web_views import (
    WebAgentBalanceAPIView,
    WebAdjustAgentBalanceAPIView,
    WebAgentBalanceDetailAPIView,
)

urlpatterns = [
    path("agent/balance/", WebAgentBalanceAPIView.as_view(), name="web-billing-agent-balance"),
    path("admin/agents/<int:agent_id>/adjust/", WebAdjustAgentBalanceAPIView.as_view(), name="web-billing-adjust"),
    path("admin/agents/<int:agent_id>/balance/", WebAgentBalanceDetailAPIView.as_view(), name="web-billing-agent-balance-detail"),
]
