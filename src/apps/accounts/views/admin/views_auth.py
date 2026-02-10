from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from apps.core.ui.messages import ui_message


def login_view(request):
    """
    تسجيل الدخول مع إعادة توجيه حسب نوع المستخدم
    (Admin / Super Admin / Agent)
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # ======================
        # Validation
        # ======================
        if not username or not password:
            ui_message(request, 'EMPTY_CREDENTIALS', 'error')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)

        if not user:
            ui_message(request, 'INVALID_CREDENTIALS', 'error')
            return render(request, 'accounts/login.html')

        # ======================
        # Check Active Status
        # ======================
        if not user.is_active:
            ui_message(request, 'ACCOUNT_SUSPENDED', 'error')
            return render(request, 'accounts/login.html')

        # ======================
        # Login
        # ======================
        login(request, user)
        ui_message(request, 'LOGIN_SUCCESS', 'success')

        # ======================
        # Safe Next URL
        # ======================
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()
        ):
            return redirect(next_url)

        # ======================
        # Redirect by Role
        # ======================
        if user.role == 'ADMIN':
            return redirect('/accounts/admin/dashboard/')
        elif user.role == 'AGENT':
            return redirect('/accounts/agent/dashboard/')

        # Fallback (احتياطي)
        return redirect('/accounts/login/')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    تسجيل الخروج
    """
    logout(request)
    ui_message(request, 'LOGOUT_SUCCESS', 'info')
    return redirect('/accounts/login/')

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def post_login_redirect(request):
    """
    صفحة وسيطة بعد تسجيل الدخول:
    - تُحدّث CSRF
    - تعرض رسالة
    - ثم redirect تلقائي
    """
    if request.user.role == 'ADMIN':
        target = '/accounts/admin/dashboard/'
    elif request.user.role == 'AGENT':
        target = '/accounts/agent/dashboard/'
    else:
        target = '/'

    return render(request, 'accounts/post_login.html', {
        'target_url': target
    })
