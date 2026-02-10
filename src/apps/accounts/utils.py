from apps.accounts.models import SystemSetting


def get_system_setting(key, default=None):
    try:
        return SystemSetting.objects.get(key=key).value
    except SystemSetting.DoesNotExist:
        return default


def set_system_setting(key, value):
    """Create or update a system setting value (stored as string)."""
    obj, _ = SystemSetting.objects.update_or_create(key=key, defaults={"value": str(value)})
    return obj

from apps.accounts.constants import ADMIN_PERMISSION_PRESETS

from apps.accounts.constants import ADMIN_PERMISSION_PRESETS

def apply_admin_preset(admin_permissions, preset_key):
    preset = ADMIN_PERMISSION_PRESETS.get(preset_key)
    if not preset:
        return False

    # ✨ حفظ نوع المشرف
    admin_permissions.preset = preset_key

    for field, value in preset.items():
        setattr(admin_permissions, field, value)

    admin_permissions.save()
    return True
    

