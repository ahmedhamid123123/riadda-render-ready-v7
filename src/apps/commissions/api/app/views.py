from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.commissions.services import get_commission_amount
from apps.commissions.models import Company
from apps.core.api.utils import api_response


class AppEffectiveCommissionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        company_code = request.GET.get("company_code")
        denomination = request.GET.get("denomination")

        if not company_code or not denomination:
            return api_response("INVALID_INPUT", "company_code and denomination required", status.HTTP_400_BAD_REQUEST)

        try:
            denom_value = int(denomination)
        except (TypeError, ValueError):
            return api_response("INVALID_INPUT", "denomination must be integer", status.HTTP_400_BAD_REQUEST)

        agent = request.user

        # Resolve company code to Company record used by commissions app
        company, _ = Company.objects.get_or_create(code=company_code)

        amount = get_commission_amount(agent, company, denom_value)

        return api_response("SUCCESS", "OK", status.HTTP_200_OK, data={"amount": str(amount)})
