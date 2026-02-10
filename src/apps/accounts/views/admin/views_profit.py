from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.utils.dateparse import parse_date

from apps.sales.models import Transaction

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def profit_dashboard(request):
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    qs = Transaction.objects.filter(status='CONFIRMED')

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            qs = qs.filter(confirmed_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            qs = qs.filter(confirmed_at__date__lte=to_date)

    total_profit = qs.aggregate(
        total=Sum('commission_amount')
    )['total'] or 0

    return render(request, 'accounts/profit_dashboard.html', {
        'total_profit': total_profit,
        'date_from': date_from,
        'date_to': date_to,
    })

from openpyxl import Workbook
from django.http import HttpResponse

@login_required
@user_passes_test(is_admin)
def export_profit_excel(request):
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    qs = Transaction.objects.filter(status='CONFIRMED')

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            qs = qs.filter(confirmed_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            qs = qs.filter(confirmed_at__date__lte=to_date)

    wb = Workbook()
    ws = wb.active
    ws.title = "Profit Report"

    ws.append(["Date", "Commission (IQD)"])

    for t in qs:
        ws.append([
            t.confirmed_at.strftime("%Y-%m-%d %H:%M"),
            float(t.commission_amount)
        ])

    total_profit = qs.aggregate(total=Sum('commission_amount'))['total'] or 0
    ws.append([])
    ws.append(["TOTAL", float(total_profit)])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="profit_report.xlsx"'

    wb.save(response)
    return response

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

@login_required
@user_passes_test(is_admin)
def export_profit_pdf(request):
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    qs = Transaction.objects.filter(status='CONFIRMED')

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            qs = qs.filter(confirmed_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            qs = qs.filter(confirmed_at__date__lte=to_date)

    total_profit = qs.aggregate(total=Sum('commission_amount'))['total'] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="profit_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Profit Report</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    table_data = [["Date", "Commission (IQD)"]]

    for t in qs:
        table_data.append([
            t.confirmed_at.strftime("%Y-%m-%d %H:%M"),
            f"{int(t.commission_amount):,}"
        ])

    table_data.append(["TOTAL", f"{int(total_profit):,}"])

    table = Table(table_data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
