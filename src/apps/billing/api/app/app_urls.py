from django.urls import path

from .views import AgentBalanceAPIView

urlpatterns = [
    path("agent/balance/", AgentBalanceAPIView.as_view(), name="app-billing-agent-balance"),
]
