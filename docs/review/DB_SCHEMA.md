# DB Schema Update: Transaction + Receipt Payload Snapshot

## Goal
Store **exactly what the agent printed/saw** on the POS so Admin can review/audit it later.

## Changes (apps.sales.models.Transaction)
Added:
- `receipt_payload` (JSONField, null/blank): stores thermal receipt snapshot payload
- `receipt_payload_version` (PositiveIntegerField): versioning for forward compatibility

### Example payload
```json
{
  "version": 1,
  "printer_profile": "SUNMI_58",
  "width": 32,
  "lines": [
    "RIADDA POS",
    "--------------------------------",
    "Company: آسيا سيل",
    "Value: 5000",
    "Price: 4800.00",
    "Code: ASIA-12ab34cd56ef",
    "--------------------------------",
    "Agent: agent1",
    "TxnID: 123",
    "Date: 2026-02-08 20:10:00",
    "--------------------------------",
    "Thank you"
  ],
  "meta": { "transaction_id": 123, "status": "PRINTED", "public_token": "..." }
}
```

References:
- Django JSONField: https://docs.djangoproject.com/en/5.2/ref/models/fields/#jsonfield
