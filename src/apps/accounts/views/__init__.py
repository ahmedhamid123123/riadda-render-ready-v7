from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count

from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from apps.accounts.models import User
from apps.billing.models import AgentBalance
from apps.sales.models import Transaction
from apps.core.ui.messages import ui_message


# ===================== Helpers =====================

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


def filter_transactions(agent, status_filter, date_from, date_to):
    qs = Transaction.objects.filter(agent=agent).order_by('-created_at')

    if status_filter in ['CONFIRMED', 'PRINTED']:
        qs = qs.filter(status=status_filter)

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)

    return qs


# ===================== Dashboard =====================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Sales stats
    sales_stats = Transaction.objects.filter(
        status='CONFIRMED'
    ).aggregate(
        total_sales=Sum('price'),
        total_transactions=Count('id')
    )

    # Agents stats
    total_agents = User.objects.filter(role='AGENT').count()
    suspended_agents = User.objects.filter(role='AGENT', is_active=False).count()

    # Recent transactions
    recent_transactions = Transaction.objects.select_related(
        'agent'
    ).order_by('-created_at')[:10]

    return render(request, 'accounts/dashboard.html', {
        'total_sales': sales_stats['total_sales'] or 0,
        'total_transactions': sales_stats['total_transactions'] or 0,
        'total_agents': total_agents,
        'suspended_agents': suspended_agents,
        'recent_transactions': recent_transactions,
    })



# ===================== Agents List =====================

@login_required
@user_passes_test(is_admin)
def agents_list(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    agents_qs = User.objects.filter(role='AGENT')

    if search:
        agents_qs = agents_qs.filter(username__icontains=search)

    if status_filter == 'active':
        agents_qs = agents_qs.filter(is_active=True)
    elif status_filter == 'suspended':
        agents_qs = agents_qs.filter(is_active=False)

    paginator = Paginator(agents_qs.order_by('username'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    data = []
    for agent in page_obj:
        balance = AgentBalance.objects.filter(agent=agent).first()
        data.append({
            'agent': agent,
            'balance': balance.balance if balance else 0
        })

    return render(request, 'accounts/agents.html', {
        'agents': data,
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter
    })


# ===================== Agent Detail =====================

@login_required
@user_passes_test(is_admin)
def agent_detail(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role='AGENT')
    balance_obj = AgentBalance.objects.filter(agent=agent).first()

    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    transactions_qs = filter_transactions(agent, status_filter, date_from, date_to)

    total_amount = transactions_qs.aggregate(total=Sum('price'))['total'] or 0

    paginator = Paginator(transactions_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    # ===== Monthly Comparison =====
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0)

    last_month_end = current_month_start - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)

    current_qs = Transaction.objects.filter(
        agent=agent,
        status='CONFIRMED',
        created_at__gte=current_month_start
    )

    last_qs = Transaction.objects.filter(
        agent=agent,
        status='CONFIRMED',
        created_at__gte=last_month_start,
        created_at__lte=last_month_end
    )

    current_amount = current_qs.aggregate(total=Sum('price'))['total'] or 0
    current_count = current_qs.count()

    last_amount = last_qs.aggregate(total=Sum('price'))['total'] or 0
    last_count = last_qs.count()

    if last_amount > 0:
        change_percentage = ((current_amount - last_amount) / last_amount) * 100
    else:
        change_percentage = None

    return render(request, 'accounts/agent_detail.html', {
        'agent': agent,
        'balance': balance_obj.balance if balance_obj else 0,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_amount': total_amount,

        # Monthly comparison
        'current_amount': current_amount,
        'current_count': current_count,
        'last_amount': last_amount,
        'last_count': last_count,
        'change_percentage': change_percentage,
    })


# ===================== Actions =====================


@login_required
@user_passes_test(is_admin)
def adjust_agent_balance(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role='AGENT')

    try:
        amount = Decimal(request.POST.get('amount'))
    except Exception:
        ui_message(request, 'INVALID_AMOUNT', 'error')
        return redirect('admin-agents')

    if amount == 0:
        ui_message(request, 'INVALID_AMOUNT', 'error')
        return redirect('admin-agents')

    balance_obj, _ = AgentBalance.objects.get_or_create(agent=agent)
    new_balance = balance_obj.balance + amount

    if new_balance < 0:
        ui_message(request, 'NEGATIVE_BALANCE_NOT_ALLOWED', 'error')
        return redirect('admin-agents')

    balance_obj.balance = new_balance
    balance_obj.save()

    ui_message(request, 'BALANCE_UPDATED', 'success')
    return redirect('admin-agents')
# ===================== Export Excel =====================

@login_required
@user_passes_test(is_admin)
def export_agent_transactions_excel(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role='AGENT')

    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    transactions_qs = filter_transactions(agent, status_filter, date_from, date_to)

    wb = Workbook()
    ws = wb.active
    ws.title = "Agent Transactions"

    ws.append(["Username", "Date", "Amount", "Status"])

    for t in transactions_qs:
        ws.append([
            agent.username,
            t.created_at.strftime("%Y-%m-%d %H:%M"),
            float(t.price),
            t.status
        ])

    total_amount = transactions_qs.aggregate(total=Sum('price'))['total'] or 0
    ws.append([])
    ws.append(["", "TOTAL", float(total_amount), ""])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="agent_{agent.username}_report.xlsx"'

    wb.save(response)
    return response


# ===================== Export PDF =====================

@login_required
@user_passes_test(is_admin)
def export_agent_transactions_pdf(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role='AGENT')

    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    transactions_qs = filter_transactions(agent, status_filter, date_from, date_to)
    total_amount = transactions_qs.aggregate(total=Sum('price'))['total'] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="agent_{agent.username}_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        f"<b>Agent Transactions Report</b><br/>Agent: {agent.username}",
        styles['Title']
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Status: {status_filter or 'All'}<br/>From: {date_from or '-'} &nbsp;&nbsp; To: {date_to or '-'}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))

    table_data = [["Date", "Amount (IQD)", "Status"]]

    for t in transactions_qs:
        table_data.append([
            t.created_at.strftime("%Y-%m-%d %H:%M"),
            f"{int(t.price):,}",
            t.status
        ])

    table_data.append(["", "TOTAL", f"{int(total_amount):,}"])

    table = Table(table_data, colWidths=[180, 120, 120])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    doc.build(elements)

    return response

@login_required
@user_passes_test(is_admin)
def export_all_agents_excel(request):
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    agents = User.objects.filter(role='AGENT')

    wb = Workbook()
    ws = wb.active
    ws.title = "Agents Summary"

    # Header
    ws.append([
        "Agent Username",
        "Total Transactions",
        "Total Amount (IQD)"
    ])

    for agent in agents:
        qs = filter_transactions(agent, status_filter, date_from, date_to)

        total_amount = qs.aggregate(total=Sum('price'))['total'] or 0
        total_count = qs.count()

        ws.append([
            agent.username,
            total_count,
            float(total_amount)
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="agents_summary_report.xlsx"'

    wb.save(response)
    return response


@login_required
@user_passes_test(is_admin)
def export_all_agents_pdf(request):
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    agents = User.objects.filter(role='AGENT')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agents_summary_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "<b>Agents Summary Report</b>",
        styles['Title']
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Status: {status_filter or 'All'}<br/>"
        f"From: {date_from or '-'} &nbsp;&nbsp; To: {date_to or '-'}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Agent", "Transactions", "Total Amount (IQD)"]
    ]

    for agent in agents:
        qs = filter_transactions(agent, status_filter, date_from, date_to)
        total_amount = qs.aggregate(total=Sum('price'))['total'] or 0
        total_count = qs.count()

        table_data.append([
            agent.username,
            total_count,
            f"{int(total_amount):,}"
        ])

    table = Table(table_data, colWidths=[180, 120, 120])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    doc.build(elements)

    return response

@login_required
def customer_receipt_view(request, receipt_id):
    # ساده stub لتجنب ImportError — استبدل بمنطق حقيقي عند الحاجة
    return HttpResponse(f"Customer receipt: {receipt_id}")
