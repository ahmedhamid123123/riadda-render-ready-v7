# apps.core/accounts/api/agent_views.py

from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.core.api.messages import MESSAGES
from apps.core.api.utils import api_response

from apps.billing.models import AgentBalance
from apps.sales.models import Transaction


class AgentProfileAPIView(APIView):
    """
    API: معلومات الوكيل (Profile)
    يرجّع:
    - بيانات المستخدم
    - الرصيد
    - إحصائيات مختصرة عن العمليات
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        user = request.user

        # ✅ الرصيد (إذا ما موجود، ننشئه تلقائياً)
        balance_obj, _ = AgentBalance.objects.get_or_create(
            agent=user,
            defaults={"balance": Decimal("0.00")}
        )

        # ✅ إحصائيات سريعة (اختياري) - بدون تعقيد
        qs = Transaction.objects.filter(agent=user)
        total_count = qs.count()
        confirmed_count = qs.filter(status="CONFIRMED").count()
        printed_count = qs.filter(status="PRINTED").count()

        data = {
            "agent": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
            },
            "balance": str(balance_obj.balance),
            "stats": {
                "total_transactions": total_count,
                "confirmed": confirmed_count,
                "printed": printed_count,
            }
        }

        return api_response(
            "SUCCESS",
            MESSAGES["SUCCESS"],
            status.HTTP_200_OK,
            data=data
        )
