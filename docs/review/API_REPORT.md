# API Review (JWT + DRF)

## Global DRF Settings (OK)
- DEFAULT_AUTHENTICATION_CLASSES includes `JWTAuthentication`
- DEFAULT_PERMISSION_CLASSES defaults to `IsAuthenticated`
- Throttling enabled (Anon + User)

Reference:
- DRF Authentication: https://www.django-rest-framework.org/api-guide/authentication/
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/

## Issues found
1) Mixed auth styles in accounts API:
- `LoginAPIView` / `LogoutAPIView` are session-based, but the project defaults to JWT auth.
- Recommendation: use JWT for both Agent and Admin logins, and keep session logins only for the web UI.

2) Sale flow receipt snapshot was missing:
- Fixed by adding `Transaction.receipt_payload` and storing it at sell time.

## Implemented endpoints (added)
- `POST /api/accounts/admin/login/` (JWT)
- `GET  /api/sales/admin/transactions/<id>/receipt-preview/` (Admin)
- `GET  /api/sales/agent/transactions/<id>/receipt-preview/` (Agent)

## Implemented web preview (added)
- `GET /sales/admin/transactions/<id>/receipt-preview/`
Thermal-like HTML/CSS preview to match Sunmi 58mm receipts.

Reference:
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
- OWASP BOLA/IDOR: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
