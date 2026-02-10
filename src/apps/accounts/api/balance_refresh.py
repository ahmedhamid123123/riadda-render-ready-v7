from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.billing.models import AgentBalance
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class AgentBalanceRefreshAPIView(APIView):
    """
    Agent Balance Refresh API (POS)
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        balance_obj = AgentBalance.objects.filter(agent=request.user).first()
        balance = balance_obj.balance if balance_obj else 0

        return api_response(
            'SUCCESS',
            MESSAGES.get('SUCCESS', 'تم تحديث الرصيد'),
            status.HTTP_200_OK,
            data={
                'balance': float(balance)
            }
        )
