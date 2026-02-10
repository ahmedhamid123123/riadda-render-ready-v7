from django.contrib import messages

UI_MESSAGES = {
    "LOGIN_SUCCESS": "تم تسجيل الدخول بنجاح",
    "LOGIN_FAILED": "بيانات الدخول غير صحيحة",
    "LOGOUT_SUCCESS": "تم تسجيل الخروج بنجاح",
    "UNAUTHORIZED": "غير مخوّل بالدخول",
}

def ui_message(request, key: str, level: str = "info"):
    """
    عرض رسالة للمستخدم باستخدام Django messages framework.

    الاستخدام:
        ui_message(request, "LOGIN_FAILED", "error")
        ui_message(request, "LOGIN_SUCCESS", "success")
    """
    text = UI_MESSAGES.get(key, key)

    level = (level or "info").lower()

    if level == "success":
        messages.success(request, text)
    elif level in ("error", "danger"):
        messages.error(request, text)
    elif level == "warning":
        messages.warning(request, text)
    else:
        messages.info(request, text)
