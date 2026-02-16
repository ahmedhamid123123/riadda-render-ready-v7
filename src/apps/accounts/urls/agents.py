from django.urls import path

# Import agent-facing view modules explicitly instead of wildcard re-exports
from apps.accounts.views.agents import views_agent as _va
from apps.accounts.views.agents import views_agent_web as _vaw
from apps.accounts.views.agents import views_customer as _vcust

# Safely resolve attributes (preserve behavior if a callable is missing)
agent_dashboard = getattr(_va, 'agent_dashboard', None)
agent_transactions = getattr(_va, 'agent_transactions', None)
agent_print_transaction = getattr(_va, 'agent_print_transaction', None)
agent_reissue_receipt = getattr(_va, 'agent_reissue_receipt', None)

# Web POS views
agent_dashboard_view = getattr(_vaw, 'agent_dashboard_view', None)
agent_transactions_view = getattr(_vaw, 'agent_transactions_view', None)
agent_confirm_transaction = getattr(_vaw, 'agent_confirm_transaction', None)
agent_reprint_transaction = getattr(_vaw, 'agent_reprint_transaction', None)
agent_sell_view = getattr(_vaw, 'agent_sell_view', None)

# Also expose the non-web (server-rendered) sell view from views_agent
agent_sell = getattr(_va, 'agent_sell', None)

# CUSTOMER
customer_recharge_view = getattr(_vcust, 'customer_recharge_view', None)
customer_receipt_view = getattr(_va, 'customer_receipt_view', None)


urlpatterns = [
    # AGENT
    path("agent/dashboard/", agent_dashboard, name="agent_dashboard"),
    path("agent/transactions/", agent_transactions, name="agent_transactions"),
    path("agent/print/<int:transaction_id>/", agent_print_transaction, name="agent_print"),
    path("agent/reissue-receipt/<int:transaction_id>/", agent_reissue_receipt, name="agent_reissue_receipt"),

    # AGENT (WEB POS)
    path("agent/web/dashboard/", agent_dashboard_view, name="agent_web_dashboard"),
    path("agent/web/transactions/", agent_transactions_view, name="agent_web_transactions"),
    path("agent/web/transactions/<int:transaction_id>/confirm/", agent_confirm_transaction, name="agent_web_confirm"),
    path("agent/web/transactions/<int:transaction_id>/reprint/", agent_reprint_transaction, name="agent_web_reprint"),

    # Agent sell (web + fallback)
    # prefer the web-specific handler if present, otherwise use server-side `agent_sell`
    path("agent/sell/", agent_sell_view, name="agent_sell"),
    # CUSTOMER
    path("recharge/", customer_recharge_view, name="customer_recharge"),
    path("receipt/<uuid:token>/", customer_receipt_view, name="customer_receipt"),
]
