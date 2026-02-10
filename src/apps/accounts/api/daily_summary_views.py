from django.utils import timezone
from django.db.models import Sum, Count

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.sales.models import Transaction
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class AgentDailySummaryAPIView(APIView):
    """
    Daily Summary API (Agent)
    - Total sales today
    - Total transactions today
    - Breakdown by status
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user

        # بداية اليوم (حسب توقيت السيرفر)
        today = timezone.localdate()

        qs = Transaction.objects.filter(
            agent=agent,
            created_at__date=today
        )

        total_amount = (
            qs.filter(status="CONFIRMED")
            .aggregate(total=Sum("price"))
            .get("total") or 0
        )

        counts = qs.values("status").annotate(count=Count("id"))
        counts_map = {row["status"]: row["count"] for row in counts}

        data = {
            "date": str(today),
            "total_amount": str(total_amount),
            "total_transactions": qs.count(),
            "confirmed_count": counts_map.get("CONFIRMED", 0),
            "printed_count": counts_map.get("PRINTED", 0),
        }

        return api_response(
            "SUCCESS",
            MESSAGES.get("SUCCESS", "تم بنجاح"),
            status.HTTP_200_OK,
            data=data
        )
