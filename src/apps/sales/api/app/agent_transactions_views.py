from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.paginator import Paginator
from django.utils import timezone

from apps.accounts.permissions import IsAgent
from apps.sales.models import Transaction
from apps.core.api.utils import api_response


class AgentTransactionsAPIView(APIView):
    """
    Agent Transactions API
    - List transactions
    - Filter by status
    - Pagination
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user
        status_filter = request.GET.get("status")  # PRINTED / CONFIRMED

        # Validate pagination params
        try:
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            page = 1

        try:
            per_page = int(request.GET.get("per_page", 20))
        except (TypeError, ValueError):
            per_page = 20

        # Clamp per_page to reasonable bounds
        per_page = max(1, min(per_page, 100))

        qs = Transaction.objects.filter(agent=agent).order_by("-created_at")

        if status_filter in ["PRINTED", "CONFIRMED"]:
            qs = qs.filter(status=status_filter)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        data = {
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "results": [
                {
                    "id": t.id,
                    "company": getattr(t.company, "name_ar", str(t.company)),
                    "denomination": getattr(t.denomination, "value", str(t.denomination)),
                    "status": t.status,
                    "price": str(t.price),
                    "confirmed_at": t.confirmed_at.isoformat() if t.confirmed_at else None,
                    "receipt_token": str(t.public_token) if t.status == "CONFIRMED" else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in page_obj
            ]
        }

        from apps.sales.api.serializers import TransactionListSerializer

        serializer = TransactionListSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return api_response(
            "SUCCESS",
            "تم جلب العمليات بنجاح",
            status.HTTP_200_OK,
            data=serializer.data
        )
