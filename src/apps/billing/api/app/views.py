from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.billing.models import AgentBalance
from apps.accounts.permissions import IsAgent

from apps.core.api.messages import MESSAGES
from apps.core.api.utils import api_response


class AgentBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user

        try:
            balance = AgentBalance.objects.get(agent=agent)
        except AgentBalance.DoesNotExist:
            return api_response(
                'BALANCE_NOT_FOUND',
                MESSAGES.get('BALANCE_NOT_FOUND', 'Balance not found'),
                status.HTTP_404_NOT_FOUND
            )

        return api_response(
            'BALANCE_FETCH_SUCCESS',
            MESSAGES.get('BALANCE_FETCH_SUCCESS', 'Balance fetched'),
            status.HTTP_200_OK,
            data={
                'balance': str(balance.balance)
            }
        )
