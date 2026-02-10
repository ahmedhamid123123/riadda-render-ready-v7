from decimal import Decimal
from datetime import timedelta

from django.db import transaction as db_transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.accounts.models import AuditLog
from apps.billing.models import CommissionRule
from apps.sales.models import Transaction
from apps.core.api.utils import api_response


class ConfirmRechargeAPIView(APIView):
    """
    Confirm Recharge API
    - CONFIRMED
    - Calculate commission
    - Set receipt expiry
    - Return receipt_token + receipt_url
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request, transaction_id):
        agent = request.user

        # ======================
        # Fetch Transaction
        # ======================
        try:
            transaction_obj = Transaction.objects.select_for_update().get(
                id=transaction_id,
                agent=agent,
                status="PRINTED"
            )
        except Transaction.DoesNotExist:
            return api_response(
                "TRANSACTION_NOT_FOUND",
                "العملية غير موجودة أو مؤكدة مسبقًا",
                status.HTTP_404_NOT_FOUND
            )

        # ======================
        # Atomic Confirm
        # ======================
        with db_transaction.atomic():

            # ======================
            # Calculate Commission
            # ======================
            commission_amount = Decimal("0")

            rule = (
                CommissionRule.objects
                .filter(
                    company=transaction_obj.company,
                    denomination=transaction_obj.denomination,
                    agent=agent
                )
                .first()
            )

            if not rule:
                rule = (
                    CommissionRule.objects
                    .filter(
                        company=transaction_obj.company,
                        denomination=transaction_obj.denomination,
                        agent__isnull=True
                    )
                    .first()
                )

            if rule:
                commission_amount = Decimal(rule.amount)

            # ======================
            # Update Transaction
            # ======================
            transaction_obj.status = "CONFIRMED"
            transaction_obj.confirmed_at = timezone.now()
            transaction_obj.commission_amount = commission_amount
            transaction_obj.receipt_expires_at = (
                timezone.now() + timedelta(hours=24)
            )

            transaction_obj.save(
                update_fields=[
                    "status",
                    "confirmed_at",
                    "commission_amount",
                    "receipt_expires_at"
                ]
            )

            # ======================
            # Audit Log
            # ======================
            AuditLog.objects.create(
                actor=agent,
                action="CONFIRM",
                transaction_id=transaction_obj.id,
                message=f"تم تأكيد عملية الشحن رقم {transaction_obj.id}"
            )

        # ======================
        # Build Receipt URL
        # ======================
        receipt_token = transaction_obj.public_token
        receipt_url = request.build_absolute_uri(
            f"/receipt/{receipt_token}/"
        )

        # ======================
        # Response
        # ======================
        return api_response(
            "CONFIRM_SUCCESS",
            "تم تأكيد العملية بنجاح",
            status.HTTP_200_OK,
            data={
                "transaction_id": transaction_obj.id,
                "status": transaction_obj.status,
                "commission": str(transaction_obj.commission_amount),
                "receipt_token": str(receipt_token),     # 👈 الجديد
                "receipt_url": receipt_url               # 👈 الجديد
            }
        )
