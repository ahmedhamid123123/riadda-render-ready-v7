from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date

from apps.accounts.models import AuditLog, User
from django.http import HttpResponse
from openpyxl import Workbook
from django.utils.dateparse import parse_date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# Arabic labels for audit action codes (keeps stored values unchanged)
ACTION_LABELS = {
    'SELL': 'بيع شحن',
    'CONFIRM': 'تأكيد',
    'REISSUE_RECEIPT': 'إعادة إصدار الإيصال',

    'ADD_AGENT': 'إضافة وكيل',
    'RESET_AGENT_PASSWORD': 'إعادة تعيين كلمة مرور الوكيل',
    'SUSPEND_AGENT': 'إيقاف الوكيل',
    'ACTIVATE_AGENT': 'تفعيل الوكيل',
    'DELETE_AGENT': 'حذف وكيل',
    'ADJUST_BALANCE': 'تعديل الرصيد',

    'UPDATE_DEFAULT_COMMISSION': 'تحديث العمولة الافتراضية',
    'ADD_AGENT_COMMISSION': 'إضافة عمولة لوكيل',

    'ADD_ADMIN': 'إضافة مشرف',
    'RESET_ADMIN_PASSWORD': 'إعادة تعيين كلمة مرور المشرف',
    'DISABLE_ADMIN': 'تعطيل المشرف',
    'DELETE_ADMIN': 'حذف المشرف',
    'TOGGLE_SUPER_ADMIN': 'تبديل سوبر أدمن',
    'UPDATE_ADMIN_PERMISSIONS': 'تحديث صلاحيات المشرف',
    'UPDATE_AGENT_USERNAME': 'تحديث اسم وكيل',
    'TOGGLE_SHOW_PROFIT': 'تبديل إظهار الأرباح',
    'TOGGLE_ALLOW_AGENT_USERNAME_EDIT': 'تبديل صلاحية تعديل أسماء الوكلاء',
}


def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def audit_logs_list(request):
    action_filter = (request.GET.get('action') or '').strip()
    user_filter = (request.GET.get('user') or '').strip()
    date_from = (request.GET.get('from') or '').strip()
    date_to = (request.GET.get('to') or '').strip()

    logs_qs = AuditLog.objects.select_related(
        'actor', 'target_user'
    ).order_by('-created_at')

    # 🔹 فلترة حسب نوع العملية
    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)

    # 🔹 فلترة حسب المستخدم (نتأكد من أن القيمة رقمية)
    if user_filter and user_filter.isdigit():
        logs_qs = logs_qs.filter(actor__id=int(user_filter))

    # 🔹 فلترة حسب التاريخ (من)
    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            logs_qs = logs_qs.filter(created_at__date__gte=from_date)

    # 🔹 فلترة حسب التاريخ (إلى)
    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            logs_qs = logs_qs.filter(created_at__date__lte=to_date)

    paginator = Paginator(logs_qs, 20)
    page_number = (request.GET.get('page') or '').strip()
    page_obj = paginator.get_page(page_number)

    # Build actions list for filter select using Arabic labels
    actions_list = [
        (code, ACTION_LABELS.get(code, label))
        for code, label in getattr(AuditLog, 'Action').choices
    ]

    # Attach arabic label to each log in the current page for template rendering
    for log in page_obj:
        try:
            log.arabic_action = ACTION_LABELS.get(log.action, log.get_action_display())
        except Exception:
            log.arabic_action = log.get_action_display()

    return render(request, 'accounts/audit_logs.html', {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'actions': actions_list,
        'action_labels': ACTION_LABELS,
        'users': User.objects.all().order_by('username'),
    })





@login_required
@user_passes_test(is_admin)
def export_audit_logs_excel(request):
    action_filter = (request.GET.get('action') or '').strip()
    user_filter = (request.GET.get('user') or '').strip()
    date_from = (request.GET.get('from') or '').strip()
    date_to = (request.GET.get('to') or '').strip()

    logs_qs = AuditLog.objects.select_related(
        'actor', 'target_user'
    ).order_by('-created_at')

    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)

    if user_filter and user_filter.isdigit():
        logs_qs = logs_qs.filter(actor__id=int(user_filter))

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            logs_qs = logs_qs.filter(created_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            logs_qs = logs_qs.filter(created_at__date__lte=to_date)

    wb = Workbook()
    ws = wb.active
    ws.title = "Audit Logs"

    ws.append([
        "التاريخ",
        "المستخدم",
        "العملية",
        "المستهدف",
        "العملية المرتبطة",
        "التفاصيل"
    ])

    for log in logs_qs:
        ws.append([
            log.created_at.strftime("%Y-%m-%d %H:%M"),
            str(log.actor) if log.actor else "-",
            ACTION_LABELS.get(log.action, log.get_action_display()),
            str(log.target_user) if log.target_user else "-",
            str(log.transaction_id) if log.transaction_id else "-",
            log.message
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="audit_logs.xlsx"'
    wb.save(response)

    return response




@login_required
@user_passes_test(is_admin)
def export_audit_logs_pdf(request):
    action_filter = (request.GET.get('action') or '').strip()
    user_filter = (request.GET.get('user') or '').strip()
    date_from = (request.GET.get('from') or '').strip()
    date_to = (request.GET.get('to') or '').strip()

    logs_qs = AuditLog.objects.select_related(
        'actor', 'target_user'
    ).order_by('-created_at')

    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)

    if user_filter and user_filter.isdigit():
        logs_qs = logs_qs.filter(actor__id=int(user_filter))

    if date_from:
        from_date = parse_date(date_from)
        if from_date:
            logs_qs = logs_qs.filter(created_at__date__gte=from_date)

    if date_to:
        to_date = parse_date(date_to)
        if to_date:
            logs_qs = logs_qs.filter(created_at__date__lte=to_date)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("<b>سجل العمليات (Audit Log)</b>", styles['Title']))

    table_data = [[
        "التاريخ",
        "المستخدم",
        "العملية",
        "المستهدف",
        "العملية المرتبطة",
        "التفاصيل"
    ]]

    for log in logs_qs:
        table_data.append([
            log.created_at.strftime("%Y-%m-%d %H:%M"),
            str(log.actor) if log.actor else "-",
            ACTION_LABELS.get(log.action, log.get_action_display()),
            str(log.target_user) if log.target_user else "-",
            str(log.transaction_id) if log.transaction_id else "-",
            log.message
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
