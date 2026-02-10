from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction

from apps.accounts.models import User, AuditLog
from apps.accounts.permissions import is_super_admin, is_admin
from apps.accounts.services.permissions import get_admin_ui_permissions
from apps.commissions.models import DefaultCommission, AgentCommission, Company


# ==========================
# 📊 لوحة إدارة العمولات (Admin)
# ==========================
@login_required
@user_passes_test(is_admin)
def commissions_list_view(request):
    default_commissions = (
        DefaultCommission.objects
        .filter(is_active=True)
        .order_by("company", "denomination")
    )

    agent_commissions = (
        AgentCommission.objects
        .select_related("agent")
        .order_by("agent__username", "company", "denomination")
    )

    agents = User.objects.filter(role="AGENT").order_by("username")

    perms = get_admin_ui_permissions(request.user)

    return render(request, "accounts/commissions.html", {
        "default_commissions": default_commissions,
        "agent_commissions": agent_commissions,
        "agents": agents,
        "perms": perms,
    })


# ==========================
# ✏️ تحديث العمولة الافتراضية (Super Admin فقط)
# ==========================
@login_required
@user_passes_test(is_super_admin)
@require_POST
def update_default_commission(request, commission_id):
    commission = get_object_or_404(DefaultCommission, id=commission_id)
    new_amount = request.POST.get("amount")

    try:
        new_amount = float(new_amount)
        if new_amount < 0:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "قيمة العمولة يجب أن تكون رقمًا موجبًا")
        return redirect("commissions_list")

    old_amount = commission.amount
    commission.amount = new_amount
    commission.save(update_fields=["amount"])

    AuditLog.objects.create(
        actor=request.user,
        action="UPDATE_DEFAULT_COMMISSION",
        message=(
            f"تعديل العمولة الافتراضية | "
            f"الشركة: {commission.company} | "
            f"الفئة: {commission.denomination} | "
            f"من {old_amount} إلى {new_amount}"
        ),
    )

    messages.success(request, "تم تحديث العمولة الافتراضية بنجاح")
    return redirect("commissions_list")


# ==========================
# ➕ إضافة عمولة مخصصة لوكيل (Super Admin فقط)
# ==========================
@login_required
@user_passes_test(is_super_admin)
@require_POST
def add_agent_commission(request):
    agent_id = request.POST.get("agent_id")
    company = request.POST.get("company")
    denomination = request.POST.get("denomination")
    amount = request.POST.get("amount")

    if not all([agent_id, company, denomination, amount]):
        messages.error(request, "جميع الحقول مطلوبة")
        return redirect("commissions_list")

    agent = get_object_or_404(User, id=agent_id, role="AGENT")

    # Resolve company code -> Company instance
    try:
        company_obj = Company.objects.get(code=company)
    except Company.DoesNotExist:
        messages.error(request, "الشركة المحددة غير موجودة")
        return redirect("commissions_list")

    # parse denomination
    try:
        denomination = int(denomination)
    except (TypeError, ValueError):
        messages.error(request, "فئة الشحن غير صالحة")
        return redirect("commissions_list")

    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "قيمة العمولة يجب أن تكون رقمًا موجبًا")
        return redirect("commissions_list")

    try:
        with transaction.atomic():
            AgentCommission.objects.create(
                agent=agent,
                company=company_obj,
                denomination=denomination,
                amount=amount,
            )
    except IntegrityError:
        messages.error(
            request,
            "توجد بالفعل عمولة مخصصة لهذا الوكيل على نفس الشركة والفئة"
        )
        return redirect("commissions_list")

    AuditLog.objects.create(
        actor=request.user,
        action="ADD_AGENT_COMMISSION",
        target_user=agent,
        message=(
            f"إضافة عمولة مخصصة | "
            f"الوكيل: {agent.username} | "
            f"الشركة: {company_obj.name} | "
            f"الفئة: {denomination} | "
            f"العمولة: {amount}"
        ),
    )

    messages.success(request, "تمت إضافة العمولة المخصصة بنجاح")
    return redirect("commissions_list")
