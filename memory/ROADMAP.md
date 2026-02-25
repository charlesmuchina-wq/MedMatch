# Parked Items Implementation Guide
## MedMatch-AI KARAU — February 24, 2026

---

## Overview

This guide covers the 5 parked backlog items, their current state in the codebase, what's needed to ship each one, estimated effort, and step-by-step instructions.

| # | Feature | Priority | Code Exists | Keys Present | Effort |
|---|---------|----------|-------------|--------------|--------|
| 1 | LinkedIn Profile Sync | P1 | Backend + Frontend | Yes | 2-4 hrs (testing/debug) |
| 2 | ORCID OAuth Login | P1 | Backend + Frontend | **No** | 3-5 hrs (keys + testing) |
| 3 | PayPal Integration | P1 | Backend routes | Yes | 2-4 hrs (frontend + testing) |
| 4 | Enterprise SSO/SAML | P2 | Stub only | No | 8-12 hrs (full build) |
| 5 | iOS Build | P2 | None | N/A | 12-20 hrs (full build) |

---

## 1. LinkedIn Profile Sync (P1)

### Current State
- **Backend**: 5 routes fully implemented in `/app/backend/routes/linkedin.py`
  - `GET /api/linkedin/status` — Check connection status
  - `GET /api/linkedin/auth-url` — Get OAuth URL
  - `POST /api/linkedin/token` — Exchange auth code for token
  - `POST /api/linkedin/sync` — Sync profile data
  - `DELETE /api/linkedin/disconnect` — Disconnect account
- **Frontend**: `LinkedInSync.jsx` component exists with full UI (connect, sync, disconnect)
- **Env vars**: Present in `.env`
  ```
  LINKEDIN_CLIENT_ID=77wcvs14tufhyu
  LINKEDIN_CLIENT_SECRET=WPL_AP1.1wRrxdl0yr0cMnTN.9xbXZg==
  LINKEDIN_REDIRECT_URI=https://<domain>/settings?linkedin_callback=true
  ```

### What's Needed to Ship
1. **Update redirect URI** — The `LINKEDIN_REDIRECT_URI` currently points to `i18n-complete-8.preview.emergentagent.com`. When deploying to production, update this to the production domain. Also update it in the LinkedIn Developer Portal.
2. **Test the full OAuth flow** — Click "Connect LinkedIn" → authorize → callback → verify profile data populates (name, headline, profile photo, positions).
3. **Verify sync updates resume** — After connecting, the `/api/linkedin/sync` endpoint should import skills, experience, and education into the user's MedMatch profile.
4. **Test disconnect** — Ensure disconnect removes the LinkedIn connection and clears cached data.

### Where to Find the Code
| What | File |
|------|------|
| Backend routes | `/app/backend/routes/linkedin.py` |
| Frontend component | `/app/frontend/src/components/LinkedInSync.jsx` |
| Used in | Resume page, Settings page |
| DB collection | `linkedin_connections` |

### Required LinkedIn Developer Setup
1. Go to https://www.linkedin.com/developers/apps
2. Verify your app has these scopes: `openid`, `profile`, `email`, `w_member_social`
3. Add your redirect URI to "Authorized redirect URLs"
4. Ensure the app is verified (LinkedIn requires company verification for full API access)

---

## 2. ORCID OAuth Login (P1)

### Current State
- **Backend**: 7 routes in `/app/backend/routes/orcid_oauth.py`
  - `GET /api/orcid/config` — Get ORCID configuration
  - `GET /api/orcid/auth/url` — Generate auth URL
  - `GET /api/orcid/callback` — OAuth callback handler
  - `GET /api/orcid/connection/{user_id}` — Check connection
  - `POST /api/orcid/sync/{user_id}` — Sync ORCID data
  - `DELETE /api/orcid/disconnect/{user_id}` — Disconnect
- **Frontend**: `ORCIDConnect.jsx` component exists with full UI
- **Env vars**: **MISSING** — Needs to be added

### What's Needed to Ship
1. **Register your app with ORCID** — This is free:
   - Sandbox (testing): https://sandbox.orcid.org/developer-tools
   - Production: https://orcid.org/developer-tools
2. **Add env vars** to `/app/backend/.env`:
   ```
   ORCID_CLIENT_ID=APP-XXXXXXXXXXXXXXXX
   ORCID_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ORCID_REDIRECT_URI=https://<your-domain>/api/orcid/callback
   ORCID_ENVIRONMENT=sandbox   # or 'production'
   ```
3. **Test the OAuth flow** — Connect ORCID → Authorize → Callback → Verify researcher data imports (publications, education, employment).
4. **Verify data import** — The sync should populate the user's credentials page with ORCID-verified publications and affiliations.

### Where to Find the Code
| What | File |
|------|------|
| Backend routes | `/app/backend/routes/orcid_oauth.py` |
| Frontend component | `/app/frontend/src/components/ORCIDConnect.jsx` |
| Used in | Credentials page, Settings page |
| DB collection | `orcid_connections` |

### Notes
- ORCID sandbox uses `sandbox.orcid.org`, production uses `orcid.org`
- The backend code handles both environments via `ORCID_ENVIRONMENT`
- ORCID OAuth is completely free, no paid tier needed

---

## 3. PayPal Integration (P1)

### Current State
- **Backend**: 2 PayPal-specific routes in `/app/backend/routes/payments.py`
  - `POST /api/payments/paypal/create` — Create PayPal payment
  - `POST /api/payments/paypal/execute` — Execute/capture payment
  - Stripe routes also exist (create-checkout, webhook, subscription management)
- **Frontend**: `MembershipPage.jsx` and `SubscriptionManager.jsx` exist with Stripe UI
- **Env vars**: Present in `.env`
  ```
  PAYPAL_CLIENT_ID=AY0UKmQ-_Bwdy...
  PAYPAL_SECRET=EN-lGY-U_5N0p...
  STRIPE_API_KEY=sk_test_51SsW1e...
  STRIPE_WEBHOOK_SECRET=whsec_FaS3Za...
  ```

### What's Needed to Ship
1. **Add PayPal button to Membership page** — The frontend currently only shows Stripe checkout. Add a "Pay with PayPal" option alongside the Stripe button.
2. **Test PayPal sandbox flow** — Create payment → redirect to PayPal → authorize → execute → verify membership activates.
3. **Handle PayPal IPN/webhooks** — For subscription renewals and cancellations (if using PayPal subscriptions).
4. **Test the 3 pricing tiers**:
   - Job Seeker: $3 for 3 years
   - Recruiter: $10/mo or $99/yr
   - Enterprise: Custom pricing

### Where to Find the Code
| What | File |
|------|------|
| Backend routes | `/app/backend/routes/payments.py` |
| Membership page | `/app/frontend/src/pages/MembershipPage.jsx` |
| Subscription UI | `/app/frontend/src/components/SubscriptionManager.jsx` |
| DB collections | `payments`, `subscriptions`, `membership_status` |

### Required PayPal Developer Setup
1. Go to https://developer.paypal.com/dashboard
2. The keys in `.env` appear to be sandbox keys already
3. Create sandbox buyer/seller test accounts for testing
4. For production: switch `PAYPAL_CLIENT_ID` and `PAYPAL_SECRET` to live keys

---

## 4. Enterprise SSO/SAML (P2)

### Current State
- **Backend**: Only a stub reference in `enterprise_api.py` (line 830: `"sso": tier == "enterprise"`)
- **Frontend**: No SSO/SAML UI exists
- **Env vars**: None

### What's Needed to Ship (Full Build)
1. **Choose a SAML library** — Recommended: `python3-saml` (OneLogin's library) or `pysaml2`
2. **Backend implementation**:
   - `GET /api/sso/metadata` — SAML metadata XML for the IdP
   - `POST /api/sso/acs` — Assertion Consumer Service (receives SAML response)
   - `GET /api/sso/login/{org_id}` — Initiate SSO login for an organization
   - `POST /api/sso/configure` — Admin endpoint to configure SSO for an org
   - Store org SSO configs in `sso_configurations` collection
3. **Frontend implementation**:
   - SSO login option on login page ("Sign in with SSO")
   - Admin SSO configuration page (upload IdP metadata, configure mappings)
   - Organization selector or email-domain detection
4. **Env vars needed**:
   ```
   SAML_CERT_FILE=/path/to/cert.pem
   SAML_KEY_FILE=/path/to/key.pem
   SAML_SP_ENTITY_ID=https://<domain>/api/sso/metadata
   ```
5. **Test with a SAML IdP** — Use a free test IdP like:
   - https://samltest.id/ (free SAML testing service)
   - Okta Developer (free tier)
   - Azure AD (free tier)

### Architecture Notes
- Each enterprise org would have its own SSO config stored in MongoDB
- Login flow: User enters email → detect org by domain → redirect to IdP → SAML assertion → create/link user → issue JWT
- SAML metadata endpoint allows IdP admins to auto-configure their side

---

## 5. iOS Build (P2)

### Current State
- No native iOS code exists
- The app is a React web app with PWA support (service workers, manifest.json)

### Options
| Approach | Effort | Pros | Cons |
|----------|--------|------|------|
| **PWA (already done)** | 0 hrs | Works now, installable on iOS | Limited native features, no App Store |
| **Capacitor wrapper** | 8-12 hrs | Reuse existing React code, native shell | Needs Xcode, Apple Developer account |
| **React Native rebuild** | 40+ hrs | True native experience | Complete rewrite needed |

### Recommended: Capacitor (Ionic)
1. **Install Capacitor**:
   ```bash
   cd /app/frontend
   yarn add @capacitor/core @capacitor/cli
   npx cap init MedMatch com.medmatch.ai --web-dir=build
   npx cap add ios
   ```
2. **Build the React app**: `yarn build`
3. **Copy to native**: `npx cap copy ios`
4. **Open in Xcode**: `npx cap open ios`
5. **Configure**:
   - Set Bundle ID: `com.medmatch.ai`
   - Add camera/microphone permissions (for KARAU meetings)
   - Configure push notifications
   - Set app icons and splash screens
6. **Test on simulator**: Run from Xcode
7. **Submit to App Store**: Requires Apple Developer Program ($99/yr)

### Prerequisites
- macOS with Xcode installed (required for iOS builds)
- Apple Developer Program membership ($99/year)
- App icons (1024x1024) and screenshots for App Store listing

---

## Implementation Priority Recommendation

```
Phase 1 (Quick wins — existing code, has keys):
  1. LinkedIn Profile Sync  → Test existing code, debug if needed
  3. PayPal Integration      → Add PayPal button to membership page

Phase 2 (Needs external setup):
  2. ORCID OAuth Login       → Register app, add keys, test

Phase 3 (Full builds):
  4. Enterprise SSO/SAML     → Full backend + frontend build
  5. iOS Build               → Capacitor wrapper + App Store submission
```

---

## Quick Reference: File Locations

```
/app/backend/routes/
├── linkedin.py          # LinkedIn OAuth + sync
├── orcid_oauth.py       # ORCID OAuth + data import
├── payments.py          # Stripe + PayPal payments
└── enterprise_api.py    # Enterprise features (SSO stub)

/app/frontend/src/
├── components/
│   ├── LinkedInSync.jsx      # LinkedIn connect/sync UI
│   ├── ORCIDConnect.jsx       # ORCID connect UI
│   └── SubscriptionManager.jsx # Payment/subscription UI
└── pages/
    └── MembershipPage.jsx     # Membership + payment page
```

## Quick Reference: Environment Variables

```bash
# LinkedIn (present)
LINKEDIN_CLIENT_ID=77wcvs14tufhyu
LINKEDIN_CLIENT_SECRET=WPL_AP1.xxxxx
LINKEDIN_REDIRECT_URI=https://<domain>/settings?linkedin_callback=true

# ORCID (MISSING - need to register at orcid.org)
ORCID_CLIENT_ID=
ORCID_CLIENT_SECRET=
ORCID_REDIRECT_URI=https://<domain>/api/orcid/callback
ORCID_ENVIRONMENT=sandbox

# Stripe (present)
STRIPE_API_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# PayPal (present)
PAYPAL_CLIENT_ID=AY0UKmQ-xxxxx
PAYPAL_SECRET=EN-lGY-xxxxx
```
