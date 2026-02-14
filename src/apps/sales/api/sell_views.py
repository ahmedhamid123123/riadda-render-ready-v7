from decimal import Decimal
from django.db import transaction as db_transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.sales.models import Transaction, RechargeDenomination
from apps.core.api.utils import api_response
from apps.sales.api.serializers import SellResponseSerializer, SellInputSerializer


class SellRechargeAPIView(APIView):
    """
    Sell API (FK-based)
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        agent = request.user
        # Validate input with serializer
        serializer_in = SellInputSerializer(data=request.data)
        serializer_in.is_valid(raise_exception=True)
        denomination_id = serializer_in.validated_data["denomination_id"]

        try:
            denom = RechargeDenomination.objects.select_related("company").get(
                id=denomination_id,
                is_active=True
            )
        except RechargeDenomination.DoesNotExist:
            return api_response(
                "NOT_FOUND",
                "فئة الشحن غير موجودة",
                status.HTTP_404_NOT_FOUND
            )

        price = denom.price_to_agent

        with db_transaction.atomic():
            balance = agent.agent_balance

            if balance.balance < price:
                return api_response(
                    "INSUFFICIENT_BALANCE",
                    "رصيدك غير كافٍ",
                    status.HTTP_400_BAD_REQUEST
                )

            balance.balance -= price
            balance.save(update_fields=["balance"])

            tx = Transaction.objects.create(
                agent=agent,
                company=denom.company,
                denomination=denom,
                price=price,
                commission_amount=Decimal("0.00"),
                code="PENDING",      # لاحقًا: كود حقيقي
                source="POS"
            )

        data = {
            "transaction_id": tx.id,
            "company": tx.company.name_ar,
            "denomination": tx.denomination.value,
            "price": str(tx.price),
        }

        serializer = SellResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return api_response(
            "SUCCESS",
            "تمت عملية البيع",
            status.HTTP_201_CREATED,
            data=serializer.data
        )
