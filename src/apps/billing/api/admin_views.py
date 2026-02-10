from decimal import Decimal
from apps.billing.api.serializers import AdjustBalanceSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.billing.models import AgentBalance
from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin

from apps.core.api.messages import MESSAGES
from apps.core.api.utils import api_response


class AdjustAgentBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, agent_id):
        # Validate input
        serializer_in = AdjustBalanceSerializer(data=request.data)
        if not serializer_in.is_valid():
            return api_response(
                'INVALID_AMOUNT',
                MESSAGES['INVALID_AMOUNT'],
                status.HTTP_400_BAD_REQUEST
            )

        amount = serializer_in.validated_data['amount']

        if amount == Decimal('0'):
            return api_response(
                'INVALID_AMOUNT',
                MESSAGES['INVALID_AMOUNT'],
                status.HTTP_400_BAD_REQUEST
            )

        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
        except User.DoesNotExist:
            return api_response(
                'AGENT_NOT_FOUND',
                MESSAGES['AGENT_NOT_FOUND'],
                status.HTTP_404_NOT_FOUND
            )

        balance_obj, _ = AgentBalance.objects.get_or_create(agent=agent)
        new_balance = balance_obj.balance + amount

        if new_balance < 0:
            return api_response(
                'NEGATIVE_BALANCE_NOT_ALLOWED',
                MESSAGES['NEGATIVE_BALANCE_NOT_ALLOWED'],
                status.HTTP_400_BAD_REQUEST
            )

        balance_obj.balance = new_balance
        balance_obj.save()

        return api_response(
            'BALANCE_UPDATED',
            MESSAGES['BALANCE_UPDATED'],
            status.HTTP_200_OK,
            data={
                'agent': agent.username,
                'new_balance': str(balance_obj.balance)
            }
        )
class AgentBalanceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, agent_id):
        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
        except User.DoesNotExist:
            return api_response(
                'AGENT_NOT_FOUND',
                MESSAGES['AGENT_NOT_FOUND'],
                status.HTTP_404_NOT_FOUND
            )

        try:
            balance = AgentBalance.objects.get(agent=agent)
        except AgentBalance.DoesNotExist:
            return api_response(
                'BALANCE_NOT_FOUND',
                MESSAGES['BALANCE_NOT_FOUND'],
                status.HTTP_404_NOT_FOUND
            )

        return api_response(
            'BALANCE_FETCH_SUCCESS',
            MESSAGES['BALANCE_FETCH_SUCCESS'],
            status.HTTP_200_OK,
            data={
                'agent': agent.username,
                'balance': str(balance.balance)
            }
        )
