import uuid
from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsAgent
from apps.accounts.models import AuditLog
from apps.billing.models import AgentBalance
from apps.sales.models import Transaction, TelecomCompany, RechargeDenomination
from apps.sales.services.receipt import build_receipt_payload, sign_receipt_payload
from apps.commissions.services import get_commission_amount

from apps.core.api.messages import MESSAGES
from apps.core.api.utils import api_response
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse



class SellRechargeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        agent = request.user

        if not agent.is_active:
            return api_response(
                'AGENT_SUSPENDED',
                MESSAGES['AGENT_SUSPENDED'],
                status.HTTP_403_FORBIDDEN
            )

        # ✅ New sales models flow:
        # company_code + product_type + value -> RechargeDenomination (with agent price)
        company_code = (request.data.get("company_code") or request.data.get("company") or "").strip()
        product_type = (request.data.get("product_type") or "MOBILE").strip().upper()

        try:
            value = int(request.data.get("value") or request.data.get("denomination"))
        except (TypeError, ValueError):
            return api_response(
                "INVALID_DENOMINATION_FORMAT",
                MESSAGES["INVALID_DENOMINATION_FORMAT"],
                status.HTTP_400_BAD_REQUEST,
            )

        if not company_code:
            return api_response(
                "COMPANY_REQUIRED",
                "يرجى إرسال company_code",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = TelecomCompany.objects.get(code=company_code, is_active=True)
        except TelecomCompany.DoesNotExist:
            return api_response(
                "COMPANY_NOT_FOUND",
                "شركة غير موجودة أو غير مفعّلة",
                status.HTTP_404_NOT_FOUND,
            )

        try:
            denom = RechargeDenomination.objects.get(
                company=company,
                product_type=product_type,
                value=value,
                is_active=True,
            )
        except RechargeDenomination.DoesNotExist:
            return api_response(
                "DENOMINATION_NOT_FOUND",
                "فئة غير موجودة أو غير مفعّلة",
                status.HTTP_404_NOT_FOUND,
            )

        price = Decimal(denom.price_to_agent)

        with db_transaction.atomic():
            try:
                agent_balance = AgentBalance.objects.select_for_update().get(agent=agent)
            except AgentBalance.DoesNotExist:
                return api_response(
                    'BALANCE_NOT_FOUND',
                    MESSAGES['BALANCE_NOT_FOUND'],
                    status.HTTP_404_NOT_FOUND
                )

            if agent_balance.balance < price:
                return api_response(
                    'INSUFFICIENT_BALANCE',
                    MESSAGES['INSUFFICIENT_BALANCE'],
                    status.HTTP_400_BAD_REQUEST
                )

            agent_balance.balance -= price
            agent_balance.save()

            # NOTE: replace this with a real inventory code pull.
            recharge_code = f"{company.code}-{uuid.uuid4().hex[:12]}"

            transaction_obj = Transaction.objects.create(
                agent=agent,
                company=company,
                denomination=denom,
                price=price,
                code=recharge_code,
                status='PRINTED',
                commission_amount=0
            )

            # Snapshot what was printed/shown on the POS for later admin review
            payload = build_receipt_payload(transaction_obj)
            transaction_obj.receipt_payload = payload
            transaction_obj.receipt_hmac = sign_receipt_payload(transaction_obj, payload)
            transaction_obj.receipt_hmac_created_at = timezone.now()
            transaction_obj.save(update_fields=["receipt_payload", "receipt_hmac", "receipt_hmac_created_at"])

            AuditLog.objects.create(
                actor=agent,
                action='SELL',
                transaction_id=transaction_obj.id,
                message=f"تم بيع {company.name_ar} فئة {value} ({product_type})"
            )

        return api_response(
            'SALE_CREATED',
            MESSAGES['SALE_CREATED'],
            status.HTTP_201_CREATED,
            data={
                'transaction_id': transaction_obj.id,
                'company_code': company.code,
                'company_name': company.name_ar,
                'product_type': product_type,
                'value': value,
                'price': str(price),
                'code': recharge_code,
                'status': 'تمت الطباعة'
            }
        )


from django.urls import reverse

class ConfirmRechargeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request, transaction_id):
        agent = request.user

        try:
            transaction_obj = Transaction.objects.get(
                id=transaction_id,
                agent=agent
            )
        except Transaction.DoesNotExist:
            return api_response(
                'TRANSACTION_NOT_FOUND',
                MESSAGES['TRANSACTION_NOT_FOUND'],
                status.HTTP_404_NOT_FOUND
            )

        if transaction_obj.status != 'PRINTED':
            return api_response(
                'INVALID_TRANSACTION_STATUS',
                MESSAGES['INVALID_TRANSACTION_STATUS'],
                status.HTTP_400_BAD_REQUEST
            )

        commission = get_commission_amount(
            agent=agent,
            company=transaction_obj.company,
            denomination=transaction_obj.denomination,
        )

        transaction_obj.commission_amount = commission
        transaction_obj.status = 'CONFIRMED'
        transaction_obj.confirmed_at = timezone.now()
        transaction_obj.save()

        # 🔗 رابط الإيصال العام
        receipt_url = request.build_absolute_uri(
            reverse(
                'customer-receipt',
                args=[transaction_obj.public_token]
            )
        )

        AuditLog.objects.create(
            actor=agent,
            action='CONFIRM',
            transaction_id=transaction_obj.id,
            message="تم تأكيد العملية وإصدار رابط الإيصال"
        )

        return api_response(
            'CONFIRM_SUCCESS',
            MESSAGES['CONFIRM_SUCCESS'],
            status.HTTP_200_OK,
            data={
                'transaction_id': transaction_obj.id,
                'commission_amount': str(commission),
                'receipt_url': receipt_url
            }
        )