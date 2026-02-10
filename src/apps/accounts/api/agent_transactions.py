from django.core.paginator import Paginator
from django.utils.dateparse import parse_date

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.sales.models import Transaction
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class AgentTransactionsAPIView(APIView):
    """
    Agent Transactions API (POS)
    - List agent transactions
    - Filters: status, from, to
    - Pagination
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        agent = request.user

        # ======================
        # Query Params
        # ======================
        status_filter = request.GET.get("status")  # PRINTED / CONFIRMED
        from_date = parse_date(request.GET.get("from"))
        to_date = parse_date(request.GET.get("to"))

        page = int(request.GET.get("page", 1))
        page_size = min(int(request.GET.get("page_size", 20)), 50)

        # ======================
        # Base Query (Optimized)
        # ======================
        qs = (
            Transaction.objects
            .filter(agent=agent)
            .select_related("company", "denomination")
            .order_by("-created_at")
        )

        # ======================
        # Filters
        # ======================
        if status_filter in ("PRINTED", "CONFIRMED"):
            qs = qs.filter(status=status_filter)

        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)

        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)

        # ======================
        # Pagination
        # ======================
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        # ======================
        # Serialize (POS-friendly)
        # ======================
        items = []
        for t in page_obj.object_list:
            can_reprint = (
                t.status == "CONFIRMED" and
                t.receipt_reissue_count < t.receipt_reissue_limit
            )

            items.append({
                "transaction_id": t.id,
                "company": {
                    "id": t.company.id,
                    "name": t.company.name_ar,
                    "code": t.company.code,
                },
                "denomination": {
                    "id": t.denomination.id,
                    "value": t.denomination.value,
                },
                "status": t.status,
                "price": float(t.price),
                "created_at": t.created_at.isoformat(),
                "confirmed_at": (
                    t.confirmed_at.isoformat()
                    if t.confirmed_at else None
                ),
                "receipt_token": (
                    str(t.public_token)
                    if t.status == "CONFIRMED" else None
                ),
                "receipt_url": (
                    request.build_absolute_uri(
                        f"/receipt/{t.public_token}/"
                    )
                    if t.status == "CONFIRMED" else None
                ),
                "can_print": t.status == "CONFIRMED",
                "can_reprint": can_reprint,
                "reissue_count": t.receipt_reissue_count,
                "reissue_limit": t.receipt_reissue_limit,
                "reissue_remaining": (
                    t.receipt_reissue_limit - t.receipt_reissue_count
                ),
            })

        data = {
            "items": items,
            "pagination": {
                "page": page_obj.number,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            }
        }

        return api_response(
            "SUCCESS",
            MESSAGES.get("SUCCESS", "تم جلب العمليات"),
            status.HTTP_200_OK,
            data=data
        )
