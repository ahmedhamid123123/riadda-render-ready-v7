from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from apps.sales.models import Transaction
from apps.billing.models import AgentBalance
from apps.accounts.models import AuditLog
from apps.accounts.utils import get_system_setting
import uuid
from datetime import timedelta
from django.shortcuts import redirect
from django.contrib import messages

try:
    import qrcode
    import base64
    from io import BytesIO
except ImportError:
    qrcode = None
    base64 = None
    BytesIO = None


@login_required
def agent_dashboard(request):
    agent = request.user

    if agent.role != 'AGENT':
        return render(request, 'errors/403.html')

    balance_obj = AgentBalance.objects.filter(agent=agent).first()
    balance = balance_obj.balance if balance_obj else 0

    transactions_qs = Transaction.objects.filter(
        agent=agent
    ).order_by('-created_at')

    total_transactions = transactions_qs.count()

    total_commission = transactions_qs.filter(
        status='CONFIRMED'
    ).aggregate(
        total=Sum('commission_amount')
    )['total'] or 0

    recent_transactions = transactions_qs[:10]

    return render(request, 'accounts/agent_dashboard.html', {
        'balance': balance,
        'total_transactions': total_transactions,
        'total_commission': total_commission,
        'recent_transactions': recent_transactions,
    })


MAX_RECEIPT_REISSUE = 3


@login_required
def agent_transactions(request):
    agent = request.user

    if agent.role != 'AGENT':
        return render(request, 'errors/403.html')

    status_filter = request.GET.get('status', '')

    transactions_qs = Transaction.objects.filter(
        agent=agent
    ).order_by('-created_at')

    if status_filter in ['CONFIRMED', 'PRINTED']:
        transactions_qs = transactions_qs.filter(status=status_filter)

    paginator = Paginator(transactions_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_commission = transactions_qs.filter(
        status='CONFIRMED'
    ).aggregate(
        total=Sum('commission_amount')
    )['total'] or 0

    remaining_map = {}
    for t in page_obj:
        if t.status == 'CONFIRMED':
            used = AuditLog.objects.filter(
                action='REISSUE_RECEIPT',
                transaction_id=t.public_token
            ).count()
            remaining_map[t.id] = max(0, MAX_RECEIPT_REISSUE - used)

    return render(request, 'accounts/agent_transactions.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_commission': total_commission,
        'remaining_map': remaining_map,
        'max_reissue': MAX_RECEIPT_REISSUE,
    })


@login_required
def agent_print_transaction(request, transaction_id):
    agent = request.user

    if agent.role != 'AGENT':
        return render(request, 'errors/403.html')

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        agent=agent
    )

    return render(request, 'accounts/agent_print.html', {
        'transaction': transaction
    })


def customer_receipt_view(request, token):
    transaction = get_object_or_404(
        Transaction,
        public_token=token,
        status='CONFIRMED'
    )

    if transaction.receipt_expires_at and timezone.now() > transaction.receipt_expires_at:
        return render(request, 'errors/receipt_expired.html')

    receipt_url = request.build_absolute_uri()

    qr = qrcode.make(receipt_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'accounts/customer_receipt.html', {
        'transaction': transaction,
        'qr_code': qr_base64,
    })


@login_required
def agent_reissue_receipt(request, transaction_id):
    agent = request.user

    if agent.role != 'AGENT':
        return render(request, 'errors/403.html')

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        agent=agent,
        status='CONFIRMED'
    )

    if transaction.receipt_expires_at and timezone.now() > transaction.receipt_expires_at:
        return render(
            request,
            'errors/receipt_expired.html'
        )

    max_limit = int(get_system_setting('MAX_RECEIPT_REISSUE', 3))

    reissue_count = AuditLog.objects.filter(
        action='REISSUE_RECEIPT',
        transaction_id=transaction.public_token
    ).count()

    if reissue_count >= max_limit:
        return render(
            request,
            'errors/receipt_reissue_limit.html',
            {
                'max_limit': max_limit
            }
        )

    old_token = transaction.public_token

    transaction.public_token = uuid.uuid4()

    transaction.receipt_expires_at = timezone.now() + timedelta(hours=48)

    transaction.save()

    AuditLog.objects.create(
        actor=agent,
        action='REISSUE_RECEIPT',
        target_user=agent,
        transaction_id=transaction.public_token,
        message=(
            f"إعادة إصدار الإيصال | "
            f"Token قديم: {old_token} | "
            f"Token جديد: {transaction.public_token}"
        )
    )

    return redirect('agent-transactions')


@login_required
def agent_reprint_receipt(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        agent=request.user,
        status='CONFIRMED'
    )

    if transaction.receipt_reissue_count >= transaction.receipt_reissue_limit:
        messages.error(
            request,
            'تم الوصول إلى الحد الأقصى لإعادة طباعة الإيصال'
        )
        return redirect('agent-transactions')

    transaction.receipt_reissue_count += 1
    transaction.save(update_fields=['receipt_reissue_count'])

    AuditLog.objects.create(
        actor=request.user,
        action='REISSUE_RECEIPT',
        transaction_id=transaction.id,
        message=f'إعادة طباعة إيصال العملية رقم {transaction.id}'
    )

    return redirect('receipt-html', token=transaction.public_token)
