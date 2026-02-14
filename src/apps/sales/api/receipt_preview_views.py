from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.core.api.utils import api_response
from apps.accounts.permissions import IsAdmin, IsAgent
from apps.sales.models import Transaction
from apps.sales.services.receipt import verify_receipt_payload


class AdminReceiptPreviewAPIView(APIView):
    """Admin preview of exactly what the agent printed (receipt_payload)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, transaction_id: int):
        try:
            tx = Transaction.objects.select_related("agent", "company", "denomination").get(id=transaction_id)
        except Transaction.DoesNotExist:
            return api_response("NOT_FOUND", "العملية غير موجودة", status.HTTP_404_NOT_FOUND)

        payload = tx.receipt_payload
        if not payload:
            return api_response("NO_RECEIPT_PAYLOAD", "لا يوجد Snapshot للوصل لهذه العملية", status.HTTP_404_NOT_FOUND)

        return api_response("SUCCESS", "تم جلب معاينة الوصل", status.HTTP_200_OK, data={
            "transaction_id": tx.id,
            "agent": tx.agent.username,
            "status": tx.status,
            "receipt": payload,
            "integrity": {
                "verified": verify_receipt_payload(tx),
                "algo": getattr(tx, "receipt_hmac_algo", None),
            },
        })


class AgentReceiptPreviewAPIView(APIView):
    """Agent can preview their own receipt payload."""
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request, transaction_id: int):
        try:
            tx = Transaction.objects.select_related("agent").get(id=transaction_id, agent=request.user)
        except Transaction.DoesNotExist:
            return api_response("NOT_FOUND", "العملية غير موجودة", status.HTTP_404_NOT_FOUND)

        payload = tx.receipt_payload
        if not payload:
            return api_response("NO_RECEIPT_PAYLOAD", "لا يوجد Snapshot للوصل لهذه العملية", status.HTTP_404_NOT_FOUND)

        return api_response("SUCCESS", "تم جلب معاينة الوصل", status.HTTP_200_OK, data={
            "transaction_id": tx.id,
            "status": tx.status,
            "receipt": payload,
            "integrity": {
                "verified": verify_receipt_payload(tx),
                "algo": getattr(tx, "receipt_hmac_algo", None),
            },
        })