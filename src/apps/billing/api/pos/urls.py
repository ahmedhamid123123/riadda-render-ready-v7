from django.urls import path

from apps.billing.api.pos.pos_views import PosAgentBalanceAPIView

urlpatterns = [
    path("agent/balance/", PosAgentBalanceAPIView.as_view(), name="pos-billing-agent-balance"),
]
