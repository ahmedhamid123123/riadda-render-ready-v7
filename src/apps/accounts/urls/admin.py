from django.urls import path

# Import specific admin view modules directly rather than relying on package re-exports.
from apps.accounts.views.admin import (
    views_admin as _va,
    views_admin_dashboard as _vad,
    views_admin_catalog as _vac,
    views_commissions as _vc,
    views_profit as _vp,
    views_audit as _vau,
)

urlpatterns = []


def _find(attr_name):
    """Return the first attribute matching attr_name from known admin submodules."""
    for m in (_va, _vad, _vac, _vc, _vp, _vau):
        if hasattr(m, attr_name):
            return getattr(m, attr_name)
    return None


# Helper to append a path only if the view exists
def _add(pattern, view, name=None):
    if view:
        urlpatterns.append(path(pattern, view, name=name))


# ADMIN DASHBOARD
_add("admin/dashboard/", _find('admin_dashboard_view'), name="admin_dashboard")

# ADMIN – AGENTS
_add("admin/agents/", _find('agents_list_view'), name="agents_list")
_add("admin/agents/add/", _find('add_agent'), name="admin_add_agent")
_add("admin/agents/<int:agent_id>/", _find('agent_detail'), name="admin_agent_detail")
_add("admin/agents/<int:agent_id>/toggle/", _find('toggle_agent_status'), name="admin_agent_toggle")
_add("admin/agents/<int:agent_id>/adjust-balance/", _find('adjust_agent_balance'), name="admin_agent_adjust_balance")
_add("admin/agents/<int:agent_id>/edit-username/", _find('edit_agent_username'), name="admin_agent_edit_username")
_add("admin/agents/<int:agent_id>/reset-password/", _find('reset_agent_password'), name="admin_reset_agent_password")

# ADMIN – COMMISSIONS
_add("admin/commissions/", _find('commissions_list_view'), name="commissions_list")
_add("admin/commissions/default/<int:commission_id>/update/", _find('update_default_commission'), name="commissions_update_default")
_add("admin/commissions/agent/add/", _find('add_agent_commission'), name="commissions_add_agent")

# ADMIN – PROFIT
_add("admin/profit/", _find('profit_dashboard'), name="profit_dashboard")
_add("admin/profit/export-excel/", _find('export_profit_excel'), name="admin_profit_export_excel")
_add("admin/profit/export-pdf/", _find('export_profit_pdf'), name="admin_profit_export_pdf")

# ADMIN – AUDIT
_add("admin/audit-logs/", _find('audit_logs_list'), name="admin_audit_logs")
_add("admin/audit-logs/export-excel/", _find('export_audit_logs_excel'), name="admin_audit_logs_export_excel")
_add("admin/audit-logs/export-pdf/", _find('export_audit_logs_pdf'), name="admin_audit_logs_export_pdf")

# ADMIN – ADMINS
_add("admin/admins/", _find('admins_list'), name="admin_admins")
_add("admin/admins/add/", _find('add_admin'), name="admin_add_admin")
_add("admin/admins/<int:admin_id>/", _find('admin_detail'), name="admin_admin_detail")
_add("admin/admins/<int:admin_id>/toggle-super/", _find('toggle_super_admin'), name="admin_toggle_super_admin")
_add("admin/admins/<int:admin_id>/toggle-status/", _find('toggle_admin_status'), name="admin_toggle_admin_status")
_add("admin/admins/<int:admin_id>/reset-password/", _find('reset_admin_password'), name="admin_reset_admin_password")
_add("admin/admins/<int:admin_id>/delete/", _find('delete_admin'), name="admin_delete_admin")
_add("admin/admins/<int:admin_id>/permissions/", _find('admin_permissions'), name="admin_admin_permissions")

# Super-admin settings
_add("admin/settings/toggle-profit/", _find('toggle_profit_visibility'), name="admin_toggle_profit")
_add("admin/settings/toggle-agent-username-edit/", _find('toggle_allow_agent_username_edit'), name="admin_toggle_agent_username_edit")

# ADMIN – CATALOG
_add("admin/companies/", _find('admin_companies_list'), name="admin_companies")
_add("admin/companies/add/", _find('admin_company_create'), name="admin_company_add")
_add("admin/companies/<int:company_id>/edit/", _find('admin_company_edit'), name="admin_company_edit")

_add("admin/denominations/", _find('admin_denominations_list'), name="admin_denominations")
_add("admin/denominations/add/", _find('admin_denomination_create'), name="admin_denomination_add")
_add("admin/denominations/<int:denom_id>/edit/", _find('admin_denomination_edit'), name="admin_denomination_edit")
