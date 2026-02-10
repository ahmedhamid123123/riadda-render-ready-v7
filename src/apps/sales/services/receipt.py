from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.utils import timezone
from django.conf import settings
import json
import hmac
import hashlib


def _fmt_money(amount) -> str:
    try:
        return f"{amount:.2f}"
    except Exception:
        return str(amount)


def build_receipt_payload(tx, *, printer_profile: str = "SUNMI_58", include_code: bool = True) -> Dict[str, Any]:
    """Build a POS/thermal receipt snapshot payload.

    This is stored on the Transaction so Admin can preview exactly what the Agent saw/printed.
    Keep it deterministic and versioned.
    """
    width = 32 if printer_profile == "SUNMI_58" else 42  # rough defaults (58mm vs 80mm)
    now = timezone.localtime(tx.created_at) if getattr(tx, "created_at", None) else timezone.localtime()

    company_name = getattr(getattr(tx, "company", None), "name_ar", None) or str(getattr(tx, "company", ""))
    denom_value = getattr(getattr(tx, "denomination", None), "value", None) or str(getattr(tx, "denomination", ""))
    agent_username = getattr(getattr(tx, "agent", None), "username", None) or ""

    lines: List[str] = []
    lines.append("RIADDA POS")
    lines.append("-" * width)
    lines.append(f"Company: {company_name}")
    lines.append(f"Value: {denom_value}")
    lines.append(f"Price: {_fmt_money(getattr(tx, 'price', ''))}")
    if include_code:
        lines.append(f"Code: {getattr(tx, 'code', '')}")
    lines.append("-" * width)
    lines.append(f"Agent: {agent_username}")
    lines.append(f"TxnID: {getattr(tx, 'id', '')}")
    lines.append(now.strftime("Date: %Y-%m-%d %H:%M:%S"))
    lines.append("-" * width)
    lines.append("Thank you")

    return {
        "version": 1,
        "printer_profile": printer_profile,
        "width": width,
        "lines": lines,
        "meta": {
            "transaction_id": getattr(tx, "id", None),
            "status": getattr(tx, "status", None),
            "public_token": str(getattr(tx, "public_token", "")),
        },
    }


def _canonical_dumps(obj: Any) -> bytes:
    """Canonical JSON bytes (stable ordering) used for HMAC signing."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_receipt_payload(tx, payload: Dict[str, Any]) -> str:
    """Return hex HMAC signature for the receipt payload, bound to the transaction."""
    key = (getattr(settings, "RECEIPT_HMAC_KEY", "") or "").encode("utf-8")
    # Bind signature to key transaction identifiers to prevent payload reuse across txs.
    bound = {
        "tx": {
            "id": getattr(tx, "id", None),
            "public_token": str(getattr(tx, "public_token", "")),
            "created_at": (getattr(tx, "created_at", None).isoformat() if getattr(tx, "created_at", None) else None),
        },
        "payload": payload,
    }
    msg = _canonical_dumps(bound)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_receipt_payload(tx) -> bool:
    """Verify stored receipt_hmac matches computed signature."""
    if not getattr(tx, "receipt_payload", None) or not getattr(tx, "receipt_hmac", None):
        return False
    computed = sign_receipt_payload(tx, tx.receipt_payload)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(str(tx.receipt_hmac), computed)