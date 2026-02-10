from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponseForbidden

from apps.accounts.services.permissions import get_admin_ui_permissions
from apps.accounts.permissions import is_admin


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """
    لوحة تحكم المشرف.
    - متاحة فقط للمستخدمين من نوع ADMIN.
    - يتم تمرير صلاحيات الواجهة بشكل آمن للقالب.
    """

    perms = get_admin_ui_permissions(request.user) or {}

    # ضمان وجود جميع المفاتيح حتى لا ينكسر القالب
    default_perms = {
        "can_view_agents": False,
        "can_add_agents": False,
        "can_edit_agents": False,
        "can_view_commissions": False,
        "can_view_reports": False,
        "can_view_audit_logs": False,
    }

    # دمج القيم القادمة مع القيم الافتراضية
    ui_perms = {**default_perms, **perms}

    context = {
        "perms": ui_perms,
        "user": request.user,
    }

    return render(request, "accounts/admin/dashboard.html", context)
