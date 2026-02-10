from django import template

register = template.Library()

@register.filter(name='iq_currency')
def iq_currency(value):
    """
    Format number as Iraqi Dinar with thousands separator
    Example: 1250000 -> 1,250,000 IQD
    """
    try:
        value = float(value)
        return f"{value:,.0f} IQD"
    except (TypeError, ValueError):
        return "0 IQD"
