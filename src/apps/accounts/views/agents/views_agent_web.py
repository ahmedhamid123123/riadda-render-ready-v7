import requests
import logging
from requests.exceptions import RequestException
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

API_BASE = "http://127.0.0.1:8000/api"

@login_required
def agent_dashboard_view(request):
    token = request.session.get("agent_jwt")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    balance = "0"
    summary = {}

    try:
        res_balance = requests.get(
            f"{API_BASE}/accounts/agent/balance/",
            headers=headers,
            timeout=5
        )
        if res_balance.status_code == 200:
            balance = res_balance.json().get("data", {}).get("balance", "0")
    except RequestException as exc:
        logging.getLogger(__name__).warning("Failed to fetch agent balance: %s", exc)

    try:
        res_summary = requests.get(
            f"{API_BASE}/accounts/agent/summary/daily/",
            headers=headers,
            timeout=5
        )
        if res_summary.status_code == 200:
            summary = res_summary.json().get("data", {})
    except RequestException as exc:
        logging.getLogger(__name__).warning("Failed to fetch agent summary: %s", exc)

    return render(
        request,
        "agent/dashboard.html",
        {
            "balance": balance,
            "summary": summary
        }
    )


@login_required
def agent_transactions_view(request):
    token = request.session.get("agent_jwt")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    transactions = []

    try:
        res = requests.get(
            f"{API_BASE}/sales/agent/transactions/",
            headers=headers,
            timeout=5
        )
        if res.status_code == 200:
            transactions = res.json().get("data", {}).get("results", [])
    except RequestException as exc:
        logging.getLogger(__name__).warning("Failed to fetch agent transactions: %s", exc)
        transactions = []

    return render(
        request,
        "agent/transactions.html",
        {
            "transactions": transactions
        }
    )


@login_required
def agent_confirm_transaction(request, transaction_id):
    token = request.session.get("agent_jwt")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        res = requests.post(
            f"{API_BASE}/sales/confirm/{transaction_id}/",
            headers=headers,
            timeout=5
        )
        if res.status_code == 200:
            messages.success(request, "تم تأكيد العملية بنجاح")
        else:
            messages.error(request, "تعذر تأكيد العملية")
    except RequestException as exc:
        logging.getLogger(__name__).warning("Confirm transaction request failed: %s", exc)
        messages.error(request, "خطأ في الاتصال بالسيرفر")

    return redirect("agent-transactions")


@login_required
def agent_reprint_transaction(request, transaction_id):
    token = request.session.get("agent_jwt")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        res = requests.post(
            f"{API_BASE}/sales/receipt/reissue/{transaction_id}/",
            headers=headers,
            timeout=5
        )
        if res.status_code == 200:
            messages.success(request, "تمت إعادة إصدار الإيصال")
        else:
            messages.error(request, "تعذر إعادة الطباعة")
    except RequestException as exc:
        logging.getLogger(__name__).warning("Reprint transaction request failed: %s", exc)
        messages.error(request, "خطأ في الاتصال بالسيرفر")

    return redirect("agent-transactions")
