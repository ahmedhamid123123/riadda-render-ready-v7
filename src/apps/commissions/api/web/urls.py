from django.urls import path

from apps.commissions.api.web.web_views import (
    WebDefaultCommissionsListAPIView,
    WebAgentCommissionsListAPIView,
    WebEffectiveCommissionAPIView,
)

urlpatterns = [
    path("default/", WebDefaultCommissionsListAPIView.as_view(), name="web-commissions-default-list"),
    path("agent/", WebAgentCommissionsListAPIView.as_view(), name="web-commissions-agent-list"),
    path("effective/", WebEffectiveCommissionAPIView.as_view(), name="web-commissions-effective"),
]
