from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from apps.sales.models import Transaction
from apps.core.api.utils import api_response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsAgent
from apps.accounts.models import AuditLog
from apps.core.api.messages import MESSAGES
# ============================================================
# 2️⃣ Receipt API Views

class ReceiptAPIView(APIView):
    """
    Receipt API (JSON)
    - Public
    - Token based
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, token):
        try:
            tx = Transaction.objects.get(
                public_token=token,
                status="CONFIRMED"
            )
        except Transaction.DoesNotExist:
            return api_response(
                "NOT_FOUND",
                "الإيصال غير موجود",
                status.HTTP_404_NOT_FOUND
            )

        if tx.receipt_expires_at and timezone.now() > tx.receipt_expires_at:
            return api_response(
                "EXPIRED",
                "انتهت صلاحية الإيصال",
                status.HTTP_410_GONE
            )

        # Serialize minimal, safe receipt fields via serializer
        from apps.sales.api.serializers import ReceiptSerializer

        data = {
            "transaction_id": tx.id,
            "company": getattr(tx.company, "name_ar", str(tx.company)),
            "denomination": getattr(tx.denomination, "value", str(tx.denomination)),
            "confirmed_at": tx.confirmed_at.isoformat() if tx.confirmed_at else None,
        }

        serializer = ReceiptSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return api_response(
            "SUCCESS",
            "تم جلب الإيصال",
            status.HTTP_200_OK,
            data=serializer.data
        )


class ReissueReceiptAPIView(APIView):
    """
    Reissue Receipt API (POS)
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                agent=request.user,
                status='CONFIRMED'
            )
        except Transaction.DoesNotExist:
            return api_response(
                'TRANSACTION_NOT_FOUND',
                MESSAGES.get('TRANSACTION_NOT_FOUND', 'العملية غير موجودة'),
                status.HTTP_404_NOT_FOUND
            )

        # التحقق من عدد الإعادات
        if transaction.receipt_reissue_count >= transaction.receipt_reissue_limit:
            return api_response(
                'REISSUE_LIMIT_REACHED',
                'تم الوصول إلى الحد الأقصى لإعادة الطباعة',
                status.HTTP_403_FORBIDDEN
            )

        # زيادة العداد
        transaction.receipt_reissue_count += 1
        transaction.save(update_fields=['receipt_reissue_count'])

        # Audit Log
        AuditLog.objects.create(
            actor=request.user,
            action='REISSUE_RECEIPT',
            transaction_id=transaction.id,
            message=f'Reissue receipt for transaction {transaction.id}'
        )

        receipt_url = request.build_absolute_uri(
            f'/receipt/{transaction.public_token}/'
        )

        return api_response(
            'SUCCESS',
            MESSAGES.get('SUCCESS', 'تمت إعادة إصدار الإيصال'),
            status.HTTP_200_OK,
            data={
                'transaction_id': transaction.id,
                'receipt_token': str(transaction.public_token),
                'receipt_url': receipt_url,
                'reissue_count': transaction.receipt_reissue_count,
                'reissue_remaining': (
                    transaction.receipt_reissue_limit -
                    transaction.receipt_reissue_count
                )
            }
        )
