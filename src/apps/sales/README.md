Sales app structure
===================

- `views/` package: UI-facing views (receipt HTML, etc.).
- `api/` package: API endpoints for sales operations.

Guidelines:
- Add new UI views inside `views/` and import from `apps.sales.views` to preserve compatibility.
- API views belong in `apps.sales.api`.
