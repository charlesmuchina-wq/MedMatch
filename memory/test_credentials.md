# Test Credentials

## Admin (MedMatch portal)
- Email: `admin@medmatch.com`
- Password: `Swampdrainer2026!`
- Notes: hardcoded admin bypass in `routes/auth.py`. Returns a bearer `access_token`.
  Frontend stores token and uses session cookie + `access_token` in localStorage.

## Admin #2 — Unified (works across MedMatch / AI KARAU / ENZI)
- Email: `info@charstan.com`
- Password: `Swampdigger26!`
- Notes: real DB user with `is_admin=True`, seeded idempotently on startup by
  `seed_admin_account()` in `routes/auth.py` from `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `backend/.env`
  (SHA-256+salt hash via existing `hash_password`). All three portals authenticate through the
  shared `/api/auth/login`, so this admin works everywhere. `/api/auth/me` returns `is_admin: true`.

## Login flow for UI tests
- Go to `/login`, fill `[data-testid="email-input"]` + `[data-testid="password-input"]`,
  click `[data-testid="email-submit-btn"]`. After auth, MedMatch app routes are available
  (e.g. `/agents`, `/meeting-notes`).
