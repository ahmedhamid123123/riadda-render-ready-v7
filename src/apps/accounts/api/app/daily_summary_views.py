from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.sales.models import Transaction
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES
from django.utils.dateparse import parse_date


class AgentDailySummaryAPIView(APIView):
    """
    Agent daily summary
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user
        date = parse_date(request.GET.get('date'))

        qs = Transaction.objects.filter(agent=agent)
        if date:
            qs = qs.filter(created_at__date=date)

        total = qs.count()

        return api_response(
            'SUCCESS',
            MESSAGES.get('SUCCESS', 'تم'),
            status.HTTP_200_OK,
            data={'total': total}
        )
