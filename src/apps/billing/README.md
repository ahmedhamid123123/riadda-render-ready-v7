Billing app structure
=====================

- `views/` package: UI views for billing features.
- `api/` package: API endpoints used by billing.

Guidelines:
- When adding views, prefer `views/` package and keep top-level `views.py` as compatibility shim until imports are updated.
