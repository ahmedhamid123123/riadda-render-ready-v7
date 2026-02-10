from django.shortcuts import render
from django.conf import settings
import traceback


def _build_context(title, default_message, exception=None):
    ctx = {
        "title": title,
        "message": default_message,
        "details": None,
    }
    # In DEBUG show exception details to help debugging
    if settings.DEBUG and exception:
        if isinstance(exception, BaseException):
            ctx["details"] = str(exception)
        else:
            # For server errors capture the current traceback
            ctx["details"] = traceback.format_exc()
    return ctx


def bad_request(request, exception=None):
    ctx = _build_context(
        title="400 - طلب غير صحيح",
        default_message="الطلب الذي أرسلته غير صالح.",
        exception=exception,
    )
    return render(request, "errors/400.html", ctx, status=400)


def permission_denied(request, exception=None):
    ctx = _build_context(
        title="403 - ممنوع",
        default_message="ليس لديك صلاحية الوصول إلى هذه الصفحة.",
        exception=exception,
    )
    return render(request, "errors/403.html", ctx, status=403)


def page_not_found(request, exception=None):
    ctx = _build_context(
        title="404 - الصفحة غير موجودة",
        default_message="الصفحة التي تحاول الوصول إليها غير موجودة.",
        exception=exception,
    )
    return render(request, "errors/404.html", ctx, status=404)


def server_error(request):
    # Django's handler500 doesn't pass exception; show traceback only in DEBUG
    ctx = _build_context(
        title="500 - خطأ داخلي في الخادم",
        default_message="حدث خطأ في الخادم. حاول مرة أخرى لاحقًا.",
        exception=None,
    )
    if settings.DEBUG:
        # populate details with current traceback when DEBUG
        ctx["details"] = traceback.format_exc()
    return render(request, "errors/500.html", ctx, status=500)
