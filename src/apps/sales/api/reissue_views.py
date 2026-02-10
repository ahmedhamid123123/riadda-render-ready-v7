import uuid
from datetime import timedelta

from django.db import transaction as db_transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.accounts.models import AuditLog
from apps.sales.models import Transaction
from apps.core.api.utils import api_response


class ReissueReceiptAPIView(APIView):
    """
    Reissue Receipt API
    - Agent only
    - Limited attempts
    - New token
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request, transaction_id):
        agent = request.user

        # ======================
        # Fetch Transaction
        # ======================
        try:
            tx = Transaction.objects.select_for_update().get(
                id=transaction_id,
                agent=agent,
                status="CONFIRMED"
            )
        except Transaction.DoesNotExist:
            return api_response(
                "TRANSACTION_NOT_FOUND",
                "العملية غير موجودة أو غير مؤكدة",
                status.HTTP_404_NOT_FOUND
            )

        # ======================
        # Check Limit
        # ======================
        if tx.receipt_reissue_count >= tx.receipt_reissue_limit:
            return api_response(
                "REISSUE_LIMIT_REACHED",
                "تم تجاوز الحد المسموح لإعادة الإصدار",
                status.HTTP_403_FORBIDDEN
            )

        # ======================
        # Atomic Reissue
        # ======================
        with db_transaction.atomic():

            tx.public_token = uuid.uuid4()
            tx.receipt_reissue_count += 1
            tx.receipt_expires_at = timezone.now() + timedelta(hours=24)

            tx.save(
                update_fields=[
                    "public_token",
                    "receipt_reissue_count",
                    "receipt_expires_at"
                ]
            )

            # ======================
            # Audit Log
            # ======================
            AuditLog.objects.create(
                actor=agent,
                action="REISSUE_RECEIPT",
                transaction_id=tx.id,
                message=(
                    f"إعادة إصدار إيصال "
                    f"(محاولة {tx.receipt_reissue_count}/"
                    f"{tx.receipt_reissue_limit})"
                )
            )

        # ======================
        # Build Receipt URL
        # ======================
        receipt_url = request.build_absolute_uri(
            f"/receipt/{tx.public_token}/"
        )
        from apps.sales.api.serializers import ReissueResponseSerializer

        data = {
            "transaction_id": tx.id,
            "receipt_token": str(tx.public_token),
            "receipt_url": receipt_url,
            "reissue_count": tx.receipt_reissue_count,
            "reissue_limit": tx.receipt_reissue_limit,
        }

        serializer = ReissueResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return api_response(
            "REISSUE_SUCCESS",
            "تمت إعادة إصدار الإيصال بنجاح",
            status.HTTP_200_OK,
            data=serializer.data
        )
