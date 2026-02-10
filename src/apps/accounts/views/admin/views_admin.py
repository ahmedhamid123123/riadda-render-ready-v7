"""
Admin views (moved from top-level `views_admin.py`).
"""

# (file content copied from original views_admin.py)

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string

from apps.accounts.models import User, AuditLog, AdminPermission
from apps.accounts.permissions import is_admin, is_super_admin
from apps.accounts.services.permissions import get_admin_ui_permissions
from apps.billing.models import AgentBalance
from apps.accounts.utils import get_system_setting, set_system_setting
from django.contrib import messages


# =====================================================
# =============== إدارة الوكلاء =======================
# =====================================================


@login_required
@user_passes_test(is_admin)
def agents_list_view(request):
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")

    qs = User.objects.filter(role="AGENT").order_by("username")

    if search:
        qs = qs.filter(username__icontains=search)

    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "suspended":
        qs = qs.filter(is_active=False)

    balances = (
        AgentBalance.objects
        .filter(agent__in=qs)
        .select_related("agent")
    )

    data = [{"agent": b.agent, "balance": b.balance} for b in balances]

    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    perms = get_admin_ui_permissions(request.user)

    return render(request, "accounts/agents.html", {
        "agents": page_obj,
        "perms": perms,
        "search": search,
        "status_filter": status,
        "page_obj": page_obj,
    })



@login_required
@user_passes_test(is_admin)
@require_POST
def add_agent(request):
    if not request.user.is_super_admin:
        perms = getattr(request.user, "permissions", None)
        if not perms or not perms.can_add_agents:
            messages.error(request, "❌ ليس لديك صلاحية إضافة وكلاء")
            return redirect("agents_list")

    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password")

    if not username or not password:
        messages.error(request, "يرجى إدخال اسم المستخدم وكلمة المرور")
        return redirect("agents_list")

    if User.objects.filter(username=username).exists():
        messages.error(request, "اسم المستخدم موجود مسبقًا")
        return redirect("agents_list")

    User.objects.create_user(
        username=username,
        password=password,
        role="AGENT",
        is_active=True,
    )

    messages.success(request, "تمت إضافة الوكيل بنجاح")
    return redirect("agents_list")


@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_agent_status(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role="AGENT")

    if not request.user.is_super_admin:
        perms = getattr(request.user, "permissions", None)
        if not perms or not perms.can_edit_agents:
            messages.error(request, "❌ ليس لديك صلاحية تعديل حالة الوكلاء")
            return redirect("admin_agent_detail", agent_id=agent.id)

    agent.is_active = not agent.is_active
    agent.save(update_fields=["is_active"])

    AuditLog.objects.create(
        actor=request.user,
        action="ACTIVATE_AGENT" if agent.is_active else "SUSPEND_AGENT",
        target_user=agent,
        message=f"{'تفعيل' if agent.is_active else 'تعطيل'} الوكيل: {agent.username}",
    )

    messages.success(request, "تم تحديث حالة الوكيل")
    return redirect("admin_agent_detail", agent_id=agent.id)


@login_required
@user_passes_test(is_admin)
@require_POST
def adjust_agent_balance(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role="AGENT")

    if not request.user.is_super_admin:
        perms = getattr(request.user, "permissions", None)
        if not perms or not perms.can_edit_agents:
            messages.error(request, "❌ ليس لديك صلاحية تعديل رصيد الوكلاء")
            return redirect("admin_agent_detail", agent_id=agent.id)

    raw_amount = request.POST.get("amount")

    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        messages.error(request, "قيمة غير صالحة")
        return redirect("admin_agent_detail", agent_id=agent.id)

    balance_obj, _ = AgentBalance.objects.get_or_create(agent=agent)

    old_balance = balance_obj.balance
    balance_obj.balance += amount
    balance_obj.save(update_fields=["balance"])

    AuditLog.objects.create(
        actor=request.user,
        action="ADJUST_BALANCE",
        target_user=agent,
        message=f"تعديل رصيد الوكيل {agent.username} من {old_balance} إلى {balance_obj.balance}",
    )

    messages.success(request, "تم تعديل الرصيد بنجاح")
    return redirect("admin_agent_detail", agent_id=agent.id)


@login_required
@user_passes_test(is_admin)
def agent_detail(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, role="AGENT")
    balance_obj, _ = AgentBalance.objects.get_or_create(agent=agent)
    perms = get_admin_ui_permissions(request.user)

    return render(request, "accounts/agent_detail.html", {
        "agent": agent,
        "balance": balance_obj.balance,
        "perms": perms,
    })


@login_required
@user_passes_test(is_super_admin)
def admins_list(request):
    admins = User.objects.filter(role="ADMIN").order_by("username")
    return render(request, "accounts/admins.html", {"admins": admins})


@login_required
@user_passes_test(is_super_admin)
@require_POST
def toggle_profit_visibility(request):
    """Toggle the global SHOW_PROFIT system setting (stored as '1' or '0')."""
    cur = get_system_setting("SHOW_PROFIT", "1") or "1"
    new = "0" if str(cur) == "1" else "1"
    set_system_setting("SHOW_PROFIT", new)

    AuditLog.objects.create(
        actor=request.user,
        action="TOGGLE_SHOW_PROFIT",
        message=f"Toggle show profit to {new}",
    )

    messages.success(request, "تم تحديث إعداد عرض الأرباح")
    return redirect("admin_admins")


@login_required
@user_passes_test(is_super_admin)
@require_POST
def toggle_allow_agent_username_edit(request):
    """Toggle the ALLOW_AGENT_USERNAME_EDIT system setting (stored as '1' or '0')."""
    cur = get_system_setting("ALLOW_AGENT_USERNAME_EDIT", "1") or "1"
    new = "0" if str(cur) == "1" else "1"
    set_system_setting("ALLOW_AGENT_USERNAME_EDIT", new)

    AuditLog.objects.create(
        actor=request.user,
        action="TOGGLE_ALLOW_AGENT_USERNAME_EDIT",
        message=f"Toggle allow agent username edit to {new}",
    )

    messages.success(request, "تم تحديث إعداد تعديل أسماء الوكلاء")
    return redirect("admin_admins")


@login_required
@user_passes_test(is_super_admin)
@require_POST
def add_admin(request):
    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password")
    make_super = request.POST.get("is_super_admin") == "on"
    preset = (request.POST.get("preset") or "MANAGER").strip().upper()

    if not username or not password:
        messages.error(request, "يرجى إدخال اسم المستخدم وكلمة المرور")
        return redirect("admin_admins")

    if User.objects.filter(username=username).exists():
        messages.error(request, "اسم المستخدم موجود مسبقًا")
        return redirect("admin_admins")

    admin = User.objects.create_user(
        username=username,
        password=password,
        role="ADMIN",
        is_super_admin=make_super,
        is_active=True,
    )

    if not make_super:
        perms, _ = AdminPermission.objects.get_or_create(admin=admin)
        perms.apply_preset(preset)
        perms.save()

    AuditLog.objects.create(
        actor=request.user,
        action="ADD_ADMIN",
        target_user=admin,
        message=f"إضافة مشرف جديد: {admin.username} | Super Admin: {'نعم' if make_super else 'لا'}",
    )

    messages.success(request, "تمت إضافة المشرف بنجاح")
    return redirect("admin_admins")


@login_required
@user_passes_test(is_super_admin)
def admin_detail(request, admin_id):
    admin_obj = get_object_or_404(User, id=admin_id)
    if admin_obj.role != User.Role.ADMIN:
        from django.http import Http404
        raise Http404("المستخدم المطلوب ليس من نوع مشرف")

    perms, _ = AdminPermission.objects.get_or_create(admin=admin_obj)
    logs = AuditLog.objects.filter(target_user=admin_obj).order_by("-created_at")[:20]

    return render(request, "accounts/admin_detail.html", {
        "admin_obj": admin_obj,
        "perms": perms,
        "logs": logs,
    })



@login_required
@user_passes_test(is_super_admin)
def admin_permissions(request, admin_id):
    """View and update detailed AdminPermission for a given admin."""
    admin_obj = get_object_or_404(User, id=admin_id)
    if admin_obj.role != User.Role.ADMIN:
        from django.http import Http404
        raise Http404("المستخدم المطلوب ليس من نوع مشرف")

    perms, _ = AdminPermission.objects.get_or_create(admin=admin_obj)

    if request.method == "POST":
        # Read preset if provided
        preset = (request.POST.get("preset") or "").strip().upper()
        if preset:
            perms.apply_preset(preset)

        # Read boolean checkboxes
        perms.can_view_agents = request.POST.get("can_view_agents") == "on"
        perms.can_add_agents = request.POST.get("can_add_agents") == "on"
        perms.can_edit_agents = request.POST.get("can_edit_agents") == "on"

        perms.can_view_commissions = request.POST.get("can_view_commissions") == "on"
        perms.can_edit_commissions = request.POST.get("can_edit_commissions") == "on"

        perms.can_view_reports = request.POST.get("can_view_reports") == "on"
        perms.can_view_profit = request.POST.get("can_view_profit") == "on"
        perms.can_view_audit_logs = request.POST.get("can_view_audit_logs") == "on"

        perms.save()

        AuditLog.objects.create(
            actor=request.user,
            action="UPDATE_ADMIN_PERMISSIONS",
            target_user=admin_obj,
            message=f"Updated permissions for {admin_obj.username}",
        )

        messages.success(request, "تم حفظ صلاحيات المشرف")
        return redirect("admin_admin_detail", admin_id=admin_obj.id)

    return render(request, "accounts/admin_permissions.html", {
        "admin_obj": admin_obj,
        "perms": perms,
        "presets": AdminPermission.Preset.choices,
    })
