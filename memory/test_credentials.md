# Test Credentials

## Admin (MedMatch portal)
- Email: `admin@medmatch.com`
- Password: `Swampdrainer2026!`
- Notes: hardcoded admin bypass in `routes/auth.py`. Returns a bearer `access_token`.
  Frontend stores token and uses session cookie + `access_token` in localStorage.

## Login flow for UI tests
- Go to `/login`, fill `[data-testid="email-input"]` + `[data-testid="password-input"]`,
  click `[data-testid="email-submit-btn"]`. After auth, MedMatch app routes are available
  (e.g. `/agents`, `/meeting-notes`).
