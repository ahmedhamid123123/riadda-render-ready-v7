from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.billing.models import AgentBalance
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class AgentProfileAPIView(APIView):
    """
    Agent Profile API (POS)
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user

        balance_obj = AgentBalance.objects.filter(agent=agent).first()
        balance = balance_obj.balance if balance_obj else 0

        return api_response(
            'SUCCESS',
            MESSAGES.get('SUCCESS', 'تم بنجاح'),
            status.HTTP_200_OK,
            data={
                'agent_id': agent.id,
                'username': agent.username,
                'is_active': agent.is_active,
                'balance': float(balance)
            }
        )
