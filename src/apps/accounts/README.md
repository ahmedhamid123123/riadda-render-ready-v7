Accounts app structure
======================

- `views/` package: holds admin- and agent-specific view modules.
  - `views/admin/` — admin-facing views (dashboard, agents, audits, commissions, profit, catalog).
  - `views/agents/` — agent-facing views (dashboard, transactions, web POS, customer receipts).

Guidelines:
- Prefer adding new view modules under `views/admin` or `views/agents`.
- Keep top-level imports referencing `apps.accounts.views.admin` or `apps.accounts.views.agents`.
- If a permanent rename/move is needed, ask the maintainer to run the repo-wide import refactor.
