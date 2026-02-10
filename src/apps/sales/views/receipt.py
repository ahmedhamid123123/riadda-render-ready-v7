import requests
from django.conf import settings
from django.shortcuts import render
from django.http import Http404


def receipt_html_view(request, token):
    """
    HTML View
    - لا منطق
    - لا حساب
    - يعتمد 100% على Receipt API
    """

    api_url = f"{settings.BASE_URL}/api/sales/receipt/{token}/?include_qr=1"

    try:
        resp = requests.get(api_url, timeout=5)
    except requests.RequestException:
        raise Http404("Receipt service unavailable")

    if resp.status_code != 200:
        raise Http404("Receipt not found or expired")

    payload = resp.json()
    data = payload.get("data")

    if not data:
        raise Http404("Invalid receipt data")

    return render(
        request,
        "sales/receipt.html",
        {"receipt": data}
    )
