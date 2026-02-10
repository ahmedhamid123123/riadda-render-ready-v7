def get_admin_permissions_for_ui(user):
    if not user.is_authenticated:
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
        }

    perms = getattr(user, "admin_permissions", None)
    return {
        "can_view_agents": bool(perms and perms.can_view_agents),
        "can_add_agents": bool(perms and perms.can_add_agents),
        "can_edit_agents": bool(perms and perms.can_edit_agents),
        "can_view_commissions": bool(perms and perms.can_view_commissions),
        "can_edit_commissions": bool(perms and perms.can_edit_commissions),
        "can_view_reports": bool(perms and perms.can_view_reports),
        "can_view_audit_logs": bool(perms and perms.can_view_audit_logs),
    }
def get_admin_ui_permissions(user):
    if not user.is_authenticated:
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
        }

    perms = getattr(user, "admin_permissions", None)
    return {
        "can_view_agents": bool(perms and perms.can_view_agents),
        "can_add_agents": bool(perms and perms.can_add_agents),
        "can_edit_agents": bool(perms and perms.can_edit_agents),
        "can_view_commissions": bool(perms and perms.can_view_commissions),
        "can_edit_commissions": bool(perms and perms.can_edit_commissions),
        "can_view_reports": bool(perms and perms.can_view_reports),
        "can_view_audit_logs": bool(perms and perms.can_view_audit_logs),
    }