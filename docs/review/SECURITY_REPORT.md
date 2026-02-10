# Security / Secrets Scan Report (Riadda_refactored_clean v2)

## Summary
**Status: NEEDS CLEANUP** (not a breach by itself, but the repo bundle contains secret-like files and high-risk artifacts).

## High-risk artifacts found in the ZIP
1) `.env` is included in the ZIP.
- Even if values are "dev", people often forget and later put real keys there.
- Action: keep `.env` only locally, ship `.env.example` only.

2) `.venv/` is included in the ZIP (very large).
- Action: remove `.venv` from the repo bundle; install from `requirements.txt`.

3) `db.sqlite3` is included.
- If it contains real data, this is a data leak risk.
- Action: do not ship DB files; use migrations + seed scripts.

4) `data.json` fixture contains **password hashes** and user records.
- Not plaintext passwords, but still sensitive for distribution.
- Action: ensure fixtures are synthetic or remove from public bundles.

## What to rotate if ever leaked (production)
- `DJANGO_SECRET_KEY`
- DB credentials (`DJANGO_DB_USER`, `DJANGO_DB_PASS`)
- Any payment/SMS/email provider API keys

## Recommendations
- Ensure `.env` is in `.gitignore` (already present) and also excluded from release zips.
- Add a pre-commit secret scan (e.g., trufflehog) and CI check.
- Use per-environment secrets management.

References:
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Django deployment checklist (SECRET_KEY): https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
