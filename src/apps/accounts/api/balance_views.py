from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.billing.models import AgentBalance
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class AgentBalanceAPIView(APIView):
    """
    Balance Refresh API
    - Returns agent balance only
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user

        balance_obj, _ = AgentBalance.objects.get_or_create(
            agent=agent,
            defaults={"balance": Decimal("0.00")}
        )

        return api_response(
            "SUCCESS",
            MESSAGES.get("SUCCESS", "تم بنجاح"),
            status.HTTP_200_OK,
            data={
                "balance": str(balance_obj.balance)
            }
        )
