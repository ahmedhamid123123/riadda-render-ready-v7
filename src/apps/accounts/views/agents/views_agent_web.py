from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from apps.billing.models import AgentBalance
from apps.sales.models import Transaction
from apps.sales.models import RechargeDenomination
from apps.accounts.models import AuditLog
from apps.commissions.services import get_commission_amount
from apps.sales.services.receipt import build_receipt_payload, sign_receipt_payload
from django.db import transaction as db_transaction
from decimal import Decimal
from django.utils import timezone
import uuid
from apps.sales.models import TelecomCompany


@login_required
def agent_dashboard_view(request):
    agent = request.user

    # agent balance
    balance_obj = AgentBalance.objects.filter(agent=agent).first()
    balance = balance_obj.balance if balance_obj else 0

    # today's summary
    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    summary_qs = Transaction.objects.filter(
        agent=agent,
        created_at__gte=start_of_day
    )

    summary = {
        'date': start_of_day.date(),
        'total_amount': summary_qs.aggregate(total=Sum('price')).get('total') or 0,
        'total_transactions': summary_qs.count(),
        'confirmed_count': summary_qs.filter(status='CONFIRMED').count(),
        'printed_count': summary_qs.filter(status='PRINTED').count(),
    }

    return render(
        request,
        'agent/dashboard.html',
        {
            'balance': balance,
            'summary': summary
        }
    )


@login_required
def agent_transactions_view(request):
    agent = request.user

    transactions = (
        Transaction.objects
        .filter(agent=agent)
        .select_related('company', 'denomination')
        .order_by('-created_at')
    )

    return render(
        request,
        'agent/transactions.html',
        {
            'transactions': transactions
        }
    )


@login_required
def agent_sell_view(request):
    """Render catalog for agent sell page (GET)."""
    agent = request.user

    # Handle POST -> perform sale
    if request.method == 'POST':
        denom_id = request.POST.get('denomination_id')
        if not denom_id:
            messages.error(request, 'لم يتم إرسال فئة الشحن')
            return redirect('agent_sell')

        try:
            denom = RechargeDenomination.objects.select_related('company').get(id=int(denom_id), is_active=True)
        except Exception:
            messages.error(request, 'فئة الشحن غير موجودة')
            return redirect('agent_sell')

        price = Decimal(denom.price_to_agent)

        with db_transaction.atomic():
            try:
                balance = AgentBalance.objects.select_for_update().get(agent=agent)
            except AgentBalance.DoesNotExist:
                messages.error(request, 'رصيدك غير متوفر')
                return redirect('agent_sell')

            if balance.balance < price:
                messages.error(request, 'رصيدك غير كافٍ')
                return redirect('agent_sell')

            balance.balance -= price
            balance.save(update_fields=['balance'])

            recharge_code = f"{denom.company.code}-{uuid.uuid4().hex[:12]}"

            tx = Transaction.objects.create(
                agent=agent,
                company=denom.company,
                denomination=denom,
                price=price,
                code=recharge_code,
                status='PRINTED',
                commission_amount=Decimal('0.00')
            )

            payload = build_receipt_payload(tx)
            tx.receipt_payload = payload
            tx.receipt_hmac = sign_receipt_payload(tx, payload)
            tx.receipt_hmac_created_at = timezone.now()
            tx.save(update_fields=['receipt_payload', 'receipt_hmac', 'receipt_hmac_created_at'])

            AuditLog.objects.create(
                actor=agent,
                action='SELL',
                transaction_id=tx.id,
                message=f"تم بيع {denom.company.name_ar} فئة {denom.value}"
            )

        messages.success(request, 'تمت عملية البيع')
        return redirect('agent_transactions')

    companies = (
        TelecomCompany.objects
        .filter(is_active=True)
        .prefetch_related('denominations')
        .order_by('display_order', 'name_ar')
    )

    catalog = []
    for company in companies:
        denoms = []
        for d in company.denominations.all():
            if not d.is_active:
                continue
            denoms.append({
                'id': d.id,
                'value': d.value,
                'price_to_agent': d.price_to_agent,
            })

        if not denoms:
            continue

        catalog.append({
            'company_id': company.id,
            'company_name': company.name_ar,
            'logo': company.logo.url if company.logo else None,
            'denominations': denoms,
        })

    return render(request, 'agent/sell.html', {'catalog': catalog})


@login_required
def agent_confirm_transaction(request, transaction_id):
    agent = request.user

    try:
        tx = Transaction.objects.get(id=transaction_id, agent=agent)
    except Transaction.DoesNotExist:
        messages.error(request, "العملية غير موجودة")
        return redirect('agent-transactions')

    if tx.status != 'PRINTED':
        messages.error(request, 'لا يمكن تأكيد هذه العملية')
        return redirect('agent-transactions')

    commission = get_commission_amount(
        agent=agent,
        company=tx.company,
        denomination=tx.denomination,
    )

    tx.commission_amount = commission
    tx.status = 'CONFIRMED'
    tx.confirmed_at = timezone.now()
    tx.save()

    AuditLog.objects.create(
        actor=agent,
        action='CONFIRM',
        transaction_id=tx.id,
        message='تم تأكيد العملية عبر واجهة الويب'
    )

    messages.success(request, 'تم تأكيد العملية بنجاح')
    return redirect('agent-transactions')


@login_required
def agent_reprint_transaction(request, transaction_id):
    agent = request.user

    tx = get_object_or_404(Transaction, id=transaction_id, agent=agent, status='CONFIRMED')

    if tx.receipt_reissue_count >= tx.receipt_reissue_limit:
        messages.error(request, 'تم الوصول إلى الحد الأقصى لإعادة طباعة الإيصال')
        return redirect('agent-transactions')

    tx.receipt_reissue_count += 1
    tx.save(update_fields=['receipt_reissue_count'])

    AuditLog.objects.create(
        actor=agent,
        action='REISSUE_RECEIPT',
        transaction_id=tx.id,
        message=f'إعادة طباعة عبر واجهة الويب للمعاملة {tx.id}'
    )

    messages.success(request, 'تمت إعادة إصدار الإيصال')
    return redirect('receipt-html', token=tx.public_token)
