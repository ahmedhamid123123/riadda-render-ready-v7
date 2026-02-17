from django.urls import path

from apps.accounts.views.agents import views_agent as _va
from apps.accounts.views.agents import views_agent_web as _vaw
from apps.accounts.views.agents import views_customer as _vcust

# Agent server-rendered views
agent_dashboard = getattr(_va, 'agent_dashboard', None)
agent_transactions = getattr(_va, 'agent_transactions', None)
agent_print_transaction = getattr(_va, 'agent_print_transaction', None)
agent_reissue_receipt = getattr(_va, 'agent_reissue_receipt', None)
agent_reprint_receipt = getattr(_va, 'agent_reprint_receipt', None)
agent_sell_fallback = getattr(_va, 'agent_sell', None)

# Web POS views
agent_dashboard_view = getattr(_vaw, 'agent_dashboard_view', None)
agent_transactions_view = getattr(_vaw, 'agent_transactions_view', None)
agent_confirm_transaction = getattr(_vaw, 'agent_confirm_transaction', None)
agent_reprint_transaction_web = getattr(_vaw, 'agent_reprint_transaction', None)
agent_sell_web = getattr(_vaw, 'agent_sell_view', None)

# Prefer Web POS sell if available, else fallback
agent_sell_handler = agent_sell_web or agent_sell_fallback

# Customer
customer_recharge_view = getattr(_vcust, 'customer_recharge_view', None)
customer_receipt_view = getattr(_va, 'customer_receipt_view', None)

_missing = [name for name, fn in {
    "agent_dashboard": agent_dashboard,
    "agent_transactions": agent_transactions,
    "agent_sell_handler": agent_sell_handler,
}.items() if not callable(fn)]

if _missing:
    raise RuntimeError(f"Missing required agent views: {_missing}")

urlpatterns = [
    path("agent/dashboard/", agent_dashboard, name="agent_dashboard"),
    path("agent/transactions/", agent_transactions, name="agent_transactions"),
    path("agent/print/<int:transaction_id>/", agent_print_transaction, name="agent_print"),
    path("agent/reissue-receipt/<int:transaction_id>/", agent_reissue_receipt, name="agent_reissue_receipt"),
    path("agent/reprint/<int:transaction_id>/", agent_reprint_receipt, name="agent_reprint"),

    # Web POS
    path("agent/web/dashboard/", agent_dashboard_view, name="agent_web_dashboard"),
    path("agent/web/transactions/", agent_transactions_view, name="agent_web_transactions"),
    path("agent/web/transactions/<int:transaction_id>/confirm/", agent_confirm_transaction, name="agent_web_confirm"),
    path("agent/web/transactions/<int:transaction_id>/reprint/", agent_reprint_transaction_web, name="agent_web_reprint"),

    # Unified sell endpoint
    path("agent/sell/", agent_sell_handler, name="agent_sell"),

    # Customer
    path("recharge/", customer_recharge_view, name="customer_recharge"),
    path("receipt/<uuid:token>/", customer_receipt_view, name="customer_receipt"),
]
