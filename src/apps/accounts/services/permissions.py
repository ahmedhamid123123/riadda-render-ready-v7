from apps.accounts.models import AdminPermission


def get_admin_ui_permissions(user):
    """Return a dict of UI permission flags for the given user.

    Always return a mapping (not a model instance) so callers can safely
    merge it with defaults or read boolean flags in templates.
    """
    # If the user is not authenticated or not active, return empty mapping.
    # This prevents creating related AdminPermission objects for inactive
    # users (for example when someone disables their own account but the
    # session remains active and browser requests continue like /favicon.ico).
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", True):
        return {}

    if getattr(user, "is_super_admin", False):
        return {
            "can_view_agents": True,
            "can_add_agents": True,
            "can_edit_agents": True,
            "can_view_commissions": True,
            "can_edit_commissions": True,
            "can_view_reports": True,
            "can_view_audit_logs": True,
            "is_super_admin": True,
        }

    perms, _ = AdminPermission.objects.get_or_create(admin=user)
    return {
        "can_view_agents": bool(perms.can_view_agents),
        "can_add_agents": bool(perms.can_add_agents),
        "can_edit_agents": bool(perms.can_edit_agents),
        "can_view_commissions": bool(perms.can_view_commissions),
        "can_edit_commissions": bool(perms.can_edit_commissions),
        "can_view_reports": bool(perms.can_view_reports),
        "can_view_profit": bool(getattr(perms, "can_view_profit", True)),
        "can_view_audit_logs": bool(perms.can_view_audit_logs),
        "is_super_admin": False,
    }
