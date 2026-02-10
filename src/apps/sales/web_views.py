from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from apps.accounts.permissions import is_admin
from apps.sales.models import Transaction
from apps.sales.services.receipt import build_receipt_payload, sign_receipt_payload, verify_receipt_payload


def receipt_html_view(request, token):
    # Backwards-compatible import used by existing URLs
    tx = get_object_or_404(Transaction, public_token=token, status="CONFIRMED")
    return render(request, "sales/receipt.html", {"tx": tx})


@login_required
@user_passes_test(is_admin)
def admin_receipt_preview_view(request, transaction_id: int):
    """Web UI that shows exactly what the agent printed (thermal-style preview)."""
    tx = get_object_or_404(Transaction.objects.select_related("agent", "company", "denomination"), id=transaction_id)

    payload = tx.receipt_payload or build_receipt_payload(tx)
    # If payload was missing, store it so future previews are stable.
    if not tx.receipt_payload:
        tx.receipt_payload = payload
        tx.receipt_hmac = sign_receipt_payload(tx, payload)
        from django.utils import timezone
        tx.receipt_hmac_created_at = timezone.now()
        tx.save(update_fields=["receipt_payload", "receipt_hmac", "receipt_hmac_created_at"])

    return render(request, "sales/receipt_preview_thermal.html", {"tx": tx, "receipt": payload, "receipt_verified": verify_receipt_payload(tx)})