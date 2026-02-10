ADMIN_PERMISSION_PRESETS = {
    'READ_ONLY': {
        'can_view_agents': True,
        'can_edit_agents': False,
        'can_view_commissions': False,
        'can_edit_commissions': False,
        'can_view_reports': False,
        'can_view_audit_logs': False,
    },
    'MANAGER': {
        'can_view_agents': True,
        'can_edit_agents': True,
        'can_view_commissions': True,
        'can_edit_commissions': True,
        'can_view_reports': False,
        'can_view_audit_logs': True,
    },
    'ACCOUNTANT': {
        'can_view_agents': True,
        'can_edit_agents': False,
        'can_view_commissions': False,
        'can_edit_commissions': False,
        'can_view_reports': True,
        'can_view_audit_logs': True,
    },
}
