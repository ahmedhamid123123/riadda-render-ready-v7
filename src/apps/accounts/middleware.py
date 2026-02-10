# accounts/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class AdminPermissionMiddleware:
    """
    Middleware مركزي للتحكم بصلاحيات الأدمن
    - يمنع الوكلاء من دخول صفحات الأدمن
    - يسمح للسوبر أدمن بكل شيء
    - يقيّد الأدمن العادي حسب AdminPermission
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        path = request.path

        # نطبق فقط على صفحات الأدمن المخصصة
        if path.startswith('/accounts/admin/'):

            # غير مسجل دخول
            if not user.is_authenticated:
                return redirect(reverse('login'))

            # =========================
            # Agent ❌
            # =========================
            if user.role == 'AGENT':
                messages.error(request, 'غير مسموح لك بالدخول إلى لوحة الإدارة')
                return redirect(reverse('agent-dashboard'))

            # =========================
            # Super Admin ✅ (يمر دائمًا)
            # =========================
            if user.role == 'ADMIN' and user.is_super_admin:
                return self.get_response(request)

            # =========================
            # Admin عادي → فحص الصلاحيات
            # =========================
            perms = getattr(user, 'permissions', None)

            if not perms:
                messages.error(request, 'لا تملك صلاحيات إدارية')
                return redirect(reverse('login'))

            # ---- ربط المسارات بالصلاحيات ----
            if path.startswith('/accounts/admin/agents/') and not perms.can_view_agents:
                return self._deny(request)

            if path.startswith('/accounts/admin/commissions/') and not perms.can_view_commissions:
                return self._deny(request)

            if path.startswith('/accounts/admin/profit/') and not perms.can_view_reports:
                return self._deny(request)

            if path.startswith('/accounts/admin/audit-logs/') and not perms.can_view_audit_logs:
                return self._deny(request)

        return self.get_response(request)

    def _deny(self, request):
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(reverse('admin-dashboard'))
