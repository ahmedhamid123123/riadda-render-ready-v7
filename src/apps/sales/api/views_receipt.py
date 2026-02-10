from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from apps.sales.models import Transaction


def receipt_html_view(request, token):
    tx = get_object_or_404(
        Transaction,
        public_token=token,
        status="CONFIRMED"
    )

    if tx.receipt_expires_at and timezone.now() > tx.receipt_expires_at:
        return render(request, "errors/receipt_expired.html")

    return render(request, "sales/receipt.html", {
        "tx": tx
    })
