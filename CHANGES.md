# CHANGES

## API Reorganization (2026-02-13)

- Split API surface per app into `api/web` (web/admin + agents) and `api/pos` (POS/app-only).
- Moved endpoint implementations for `accounts`, `sales`, `billing`, and `commissions` into their respective `api/web` and `api/pos` packages.
- Removed compatibility shim modules that previously re-exported or delegated to the new packages.
- Updated `src/config/urls.py` to mount the structured endpoints:
  - `api/web/<app>/...` and `api/pos/<app>/...` (legacy mounts kept where appropriate).
- Added device-bound POS login at `src/apps/accounts/api/pos/pos_auth_views.py`.

## Verification
- Ran project migrations and smoke tests (`scripts/smoke_test_api.py`) — login, commissions effective, and billing balance checks passed.
- Ran `python manage.py test` — no tests discovered in this repository.

## Linting
- Installed `flake8` and `bandit` and ran checks. `flake8` reported many style issues (long lines, blank-line rules, unused imports) across the codebase including in `src/` and migration files. Bandit also ran (security findings are in the tool output).

## Notes & Next Steps
- Consider adding a narrow flake8 config to exclude migration files and the virtual environment, or incrementally fix style issues by priority.
- Add meaningful unit tests for critical API endpoints (POS login, commissions, billing) to prevent regressions.
- If you'd like, I can open a PR branch, run CI, and/or start fixing high-priority linter/security issues.
