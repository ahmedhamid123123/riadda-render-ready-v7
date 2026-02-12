from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAdmin, IsAdminOrAgent
from apps.commissions.models import DefaultCommission, AgentCommission, Company
from apps.core.api.utils import api_response


class WebDefaultCommissionsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        items = list(DefaultCommission.objects.filter(is_active=True).values(
            "id", "company__code", "company__name", "denomination", "amount"
        ))
        return api_response("SUCCESS", "OK", status.HTTP_200_OK, data={"items": items})


class WebAgentCommissionsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        items = list(AgentCommission.objects.filter(is_active=True).values(
            "id", "agent_id", "company__code", "denomination", "amount"
        ))
        return api_response("SUCCESS", "OK", status.HTTP_200_OK, data={"items": items})


class WebEffectiveCommissionAPIView(APIView):
    """Return effective commission — usable by admins and agents via web clients."""
    permission_classes = [IsAuthenticated, IsAdminOrAgent]

    def get(self, request):
        company_code = request.GET.get("company_code")
        denomination = request.GET.get("denomination")

        if not company_code or not denomination:
            return api_response("INVALID_INPUT", "company_code and denomination required", status.HTTP_400_BAD_REQUEST)

        try:
            denom_value = int(denomination)
        except (TypeError, ValueError):
            return api_response("INVALID_INPUT", "denomination must be integer", status.HTTP_400_BAD_REQUEST)

        company, _ = Company.objects.get_or_create(code=company_code)

        # Find agent-specific first
        agent = request.user if getattr(request.user, "is_authenticated", False) and getattr(request.user, "role", None) == "AGENT" else None

        # Try agent override
        if agent:
            ac = AgentCommission.objects.filter(agent=agent, company=company, denomination=denom_value, is_active=True).first()
            if ac:
                return api_response("SUCCESS", "OK", status.HTTP_200_OK, data={"amount": str(ac.amount)})

        dc = DefaultCommission.objects.filter(company=company, denomination=denom_value, is_active=True).first()
        if dc:
            return api_response("SUCCESS", "OK", status.HTTP_200_OK, data={"amount": str(dc.amount)})

        return api_response("NOT_FOUND", "No commission found", status.HTTP_404_NOT_FOUND)


__all__ = [
    "WebDefaultCommissionsListAPIView",
    "WebAgentCommissionsListAPIView",
    "WebEffectiveCommissionAPIView",
]
