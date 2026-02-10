from apps.accounts.utils import get_system_setting


def system_settings(request):
    """Inject lightweight system settings into templates.

    Returns:
        dict with `SHOW_PROFIT` and `ALLOW_AGENT_USERNAME_EDIT` boolean keys.
    """
    val = get_system_setting("SHOW_PROFIT", "1")
    show_profit = str(val).lower() in ("1", "true", "yes", "on")

    val2 = get_system_setting("ALLOW_AGENT_USERNAME_EDIT", "1")
    allow_edit_username = str(val2).lower() in ("1", "true", "yes", "on")

    return {
        "SHOW_PROFIT": show_profit,
        "ALLOW_AGENT_USERNAME_EDIT": allow_edit_username,
    }
