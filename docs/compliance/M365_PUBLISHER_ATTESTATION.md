# Microsoft 365 Publisher Attestation — Evidence Package (P1)

**Program:** Microsoft 365 App Compliance — **Publisher Attestation** (tier 1 of the
Microsoft Cloud App Security / Microsoft 365 App Compliance Program).
**Identity platform:** Microsoft Entra ID (Azure AD) OAuth 2.0.
**Date:** 2026-06-22 · **Status:** Draft for submission · **Owner:** Security/Compliance.

> Publisher Attestation is a **self-attested** questionnaire surfaced in the
> Microsoft 365 admin center / app marketplace. It does not require an audit
> (that is the higher "Microsoft 365 Certification" tier), but every answer must
> be truthful and backed by the evidence linked here.

---

## 0. Inputs still required before submission (ACTION)
Most of the package is now drafted; only the org-identity fields remain. Provide to finalize:
1. **Publisher (Partner) ID** from Microsoft Partner Center (publisher must be verified).
2. ~~Privacy Policy URL~~ ✅ **Drafted & hosted in-app** at `{APP_ORIGIN}/legal/privacy`
   (content derived from actual data handling; replace the `[Legal Entity Name]`,
   `[Hosting Region]`, and `[privacy@/security@your-domain]` placeholders in
   `frontend/src/pages/legal/PrivacyPolicyPage.jsx`).
3. ~~Terms of Use URL~~ ✅ **Drafted & hosted in-app** at `{APP_ORIGIN}/legal/terms`
   (replace placeholders in `frontend/src/pages/legal/TermsPage.jsx`).
4. **Support URL / support email** (e.g. `support@aikarau.com`).
5. **Company legal entity**, HQ address, primary contact, security contact email
   (these fill the `[Legal Entity Name]` / `[security@...]` placeholders in the legal pages too).
6. Hosting region(s) / data residency commitment (Azure/other, which regions).
7. The production **Entra App (client) ID** + redirect URIs registered.
   (Codebase currently has `AZURE_CLIENT_ID` in `backend/.env` — confirm it is the production app.)

---

## 1. App Identity & Registration

| Field | Value |
|------|-------|
| App name | AI KARAU / ENZI / MedMatch AI Suite |
| Auth protocol | OAuth 2.0 Authorization Code (Microsoft Entra ID) |
| Token endpoint | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token` |
| Redirect URI | `{REACT_APP_BACKEND_URL}/api/auth/microsoft/callback` |
| Implementation | `backend/routes/auth.py` → `microsoft_sso_placeholder`, `microsoft_sso_callback` |
| Config (secrets) | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` (env only, never in code) |

## 2. Requested Permissions (delegated) & Justification

| Scope | Type | Why it is needed | Least-privilege note |
|-------|------|------------------|----------------------|
| `openid` | Sign-in | Authenticate the user | Required for OIDC |
| `profile` | Sign-in | Display name on profile | Read-only, minimal |
| `email` | Sign-in | Account identity / matching existing user by email | Read-only |
| `User.Read` | Graph (delegated) | Read the signed-in user's basic profile (`/me`: displayName, mail/UPN, id) | **Delegated**, signed-in user only; no `User.Read.All` |
| `Calendars.Read` | Graph (delegated) | Surface the user's meeting schedule inside AI KARAU scheduling | **Read-only**; no write; can be made optional/incremental consent |

- **No application (app-only) permissions** are requested.
- **No write scopes** to mail, files, or directory.
- Calendar access is **read-only** and used solely to display the user's own
  upcoming meetings; data is not shared with third parties.

## 3. Data Handling (attestation answers)

| Question | Answer / Evidence |
|----------|-------------------|
| What Microsoft data is accessed? | Signed-in user profile (`User.Read`) and the user's own calendar events (`Calendars.Read`). |
| Is data stored? | User profile (email, name, MS id, auth method) stored in MongoDB `users`; MS access token stored to call Graph (`ms_access_token`). Calendar events are **not** persisted — read on demand. |
| Encryption in transit | TLS 1.2+ for all endpoints (HTTPS); Graph + token calls over HTTPS. |
| Encryption at rest | Database/disk encryption at the hosting provider; secrets in environment (not source). |
| Token storage | Access token stored server-side per user; not exposed to the browser for Graph. |
| Data sharing with third parties | None for Microsoft data. (LLM features operate on app content the user submits, not on MS calendar/profile data.) |
| Data retention | Account data retained while the account is active; deletion on request (see §6). |
| Data location | See §0 item 6 (region commitment). |
| PII categories | Name, email, organizational user id. |
| Sub-processors | Hosting provider; (LLM provider only for user-submitted app content, not MS data). |

## 4. Security Practices (attestation answers)
- **SDLC / SAST/DAST:** Bandit (Python SAST), ESLint security plugin (JS), CI gates.
  Evidence: `/app/docs/security/G5_CISO_EVIDENCE_PACK.md`, `SEC003_DEPENDENCY_AUDIT.md`.
- **Dependency management:** `pip-audit` / `yarn audit`; 65+ CVEs remediated (SEC-003).
- **CI/CD quality gates:** functional (G1), regression (G3), accessibility WCAG 2.2 AA
  (Phase 4) in `.github/workflows/test.yml`.
- **Authentication:** OAuth 2.0 Authorization Code; server-side session tokens with
  expiry (`db.user_sessions`, 7-day expiry).
- **Access control:** least-privilege Graph scopes; admin RBAC in app.
- **Secrets management:** environment variables only; no secrets in repo (verified by
  SAST + deployment checks).
- **Vulnerability disclosure:** security contact email (see §0 item 5).
- **Logging/monitoring:** application + audit logging (`audit_reports`, `production_metrics`).
- **Accessibility:** WCAG 2.2 AA gate (axe-core), evidence in `/app/docs/security/WCAG_*`.

## 5. Compliance Posture
- **Frameworks referenced:** GDPR, SOC 2 control alignment, HIPAA-aware handling for
  life-sciences customers (see in-app `ai_compliance`, `global_compliance` modules).
- **DPA:** Microsoft DPA + our customer DPA (link in §0).
- **Data subject rights:** consent capture (`backend/routes/privacy.py`,
  `db.user_consents`) and deletion flow (§6).

## 6. Data Subject Rights / Deletion
- **Consent:** captured at first use (`/api/privacy/consent`, status via
  `/api/privacy/consent/status`).
- **Export/Delete:** account deletion removes `users` + `user_sessions` and revokes
  the stored Graph token. Document the user-facing path and SLA for completion.

## 7. Manifest / App Validation (checklist)
- [ ] Entra app registration: redirect URI matches `{BACKEND}/api/auth/microsoft/callback`.
- [ ] Publisher domain **verified** in Entra (publisher verification → "verified" badge).
- [ ] Branding: logo, name, **Privacy URL**, **Terms URL** set on the Entra app.
- [ ] Only the 5 delegated scopes in §2 are requested (no over-provisioned permissions).
- [ ] (If Teams app) `manifest.json` validated with the Teams **Developer Portal /
      `teamsapp` validate**; `validDomains`, `webApplicationInfo.id` = client id,
      `webApplicationInfo.resource` set; privacy/terms URLs present.
- [ ] PWA `frontend/public/manifest.json` reviewed (name/icons) — distinct from Teams manifest.

## 8. Submission Steps
1. Verify publisher in **Partner Center** (one-time).
2. In **Microsoft 365 admin center → Settings → Org settings → (App compliance)**
   or **Partner Center → Microsoft 365 App Compliance**, open the app's
   **Publisher Attestation** form.
3. Fill sections mapping to §1–§6 above; attach/link this document's evidence.
4. Provide Privacy, Terms, Support URLs (§0).
5. Submit; the attestation appears on the app's listing once Microsoft processes it.
6. Re-attest annually or on material change.

## 9. Evidence Index
| Topic | Artifact |
|------|----------|
| Security program | `/app/docs/security/G5_CISO_EVIDENCE_PACK.md` |
| Dependency/CVE | `/app/docs/security/SEC003_DEPENDENCY_AUDIT.md`, `SEC003_SPRINT1_DELTA.md` |
| Accessibility | `/app/docs/security/WCAG_REMEDIATION_TRACKER_DAY1.md`, `DAY2.md` |
| CI/CD gates | `.github/workflows/test.yml` |
| Auth implementation | `backend/routes/auth.py` (Microsoft SSO + callback) |
| Consent/privacy | `backend/routes/privacy.py` |
