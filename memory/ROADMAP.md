# MedMatch-AI KARAU - Implementation Roadmap

## Last Updated: February 25, 2026

---

## Phase 1: Translation Health Monitor (COMPLETED)

### What was built
- **Backend**: `GET /api/translation-qa/health-monitor` endpoint
  - Analyzes all 50 locale files against English master (1,940 keys)
  - Smart filtering of brand names, placeholders, and legitimate cognates
  - Returns coverage %, untranslated counts, alerts per language
- **Frontend**: Health Monitor tab in Translation QA Dashboard
  - Real-time coverage table for all 50 languages
  - Status badges (healthy/warning/critical)
  - Active alerts section
  - One-click refresh

### How to maintain
- When adding new UI strings, add keys to `en.json` first
- Run the Health Monitor to detect which languages need updates
- Use the Auto-Fix button to translate missing keys via AI

---

## Phase 2: Verification Tasks

### 2A. ORCID OAuth Login Verification
**Status**: Implemented, needs E2E verification
**Backend**: `/api/auth/orcid/login`, `/api/auth/orcid/callback`
**Frontend**: Popup-based OAuth flow in `LoginPage.jsx`

**Test Steps:**
1. Go to login page
2. Click "Sign in with ORCID" (yellow-green button)
3. A popup opens to `orcid.org/oauth/authorize`
4. Login with your ORCID account
5. Authorize MedMatch
6. Popup closes, you're logged in

**Known Considerations:**
- Uses popup window (not iframe) due to ORCID security policy
- OAuth state stored in MongoDB for load-balancer compatibility
- Credentials: `ORCID_CLIENT_ID=APP-K9HUYS6GQY2RERX6`

### 2B. AI KARAU Meeting Portal E2E Test
**Status**: Implemented, needs multi-user real-world test
**Backend**: WebRTC signaling, TURN/STUN (Xirsys)
**Frontend**: `KarauMeetPortal.jsx`, `MeetingRoom.jsx`

**Test Steps:**
1. User A creates a meeting from the KARAU portal
2. User A shares the meeting link (copy link or email)
3. User B opens the shared link in a different browser/device
4. User B joins as guest (no account needed)
5. Verify: video/audio works both ways
6. Verify: chat messages work
7. Verify: screen sharing works
8. Verify: AI transcription works (if enabled)
9. Test with 3+ participants if possible

**Known Considerations:**
- Xirsys TURN credentials may expire; fallback to STUN
- WebRTC works best on Chrome/Edge
- Guest join via `/karau-meet/join/{meetingId}`

---

## Phase 3: LinkedIn Profile Sync

### Status: Already Implemented
**Backend**: `/app/backend/routes/linkedin.py` (280 lines)
- `GET /api/linkedin/status` - Check connection status
- `GET /api/linkedin/auth-url` - Get OAuth URL
- `POST /api/linkedin/token` - Exchange code for token
- `POST /api/linkedin/sync` - Sync profile to resume
- `DELETE /api/linkedin/disconnect` - Disconnect

**Frontend**: `/app/frontend/src/components/LinkedInSync.jsx` (274 lines)
- Integrated in `ResumePage.jsx` under "LinkedIn" tab
- Shows connection status, sync button, disconnect option

**Credentials**: Already in `.env`
- `LINKEDIN_CLIENT_ID=77wcvs14tufhyu`
- `LINKEDIN_CLIENT_SECRET=WPL_AP1.1wRrxdl0yr0cMnTN.9xbXZg==`
- `LINKEDIN_REDIRECT_URI=https://liquid-glass-hub-4.preview.emergentagent.com/settings?linkedin_callback=true`

**What may need attention:**
- The redirect URI points to `/settings?linkedin_callback=true` which may need to be updated
- LinkedIn API v2 uses `openid profile email` scopes
- Token exchange uses `https://api.linkedin.com/v2/userinfo` endpoint
- Test the full OAuth flow end-to-end

---

## Phase 4: PayPal Integration

### Status: Already Implemented
**Backend**: `/app/backend/routes/payments.py` (824 lines)
- `POST /api/payments/paypal/create` - Create PayPal payment
- `POST /api/payments/paypal/execute` - Execute after approval
- Uses `paypalrestsdk` (v1.13.3, sandbox mode)

**Frontend**: `MembershipPage.jsx`
- PayPal button alongside Stripe
- Handles PayPal redirect flow (approval URL → execute)

**Credentials**: Already in `.env`
- `PAYPAL_CLIENT_ID=AY0UKmQ-...`
- `PAYPAL_SECRET=EN-lGY-U_5N0p_YEfhgosK1F6wMeNO4ev...`

**What may need attention:**
- `paypalrestsdk` is deprecated; consider migrating to PayPal Checkout SDK v2
- Test sandbox payment flow end-to-end
- Verify webhook handling for payment confirmation

---

## Phase 5: Future/Backlog

### 5A. Enterprise SSO/SAML (P2)
**Approach**: Use `python3-saml` library
- Add SAML metadata endpoint
- Support IdP-initiated and SP-initiated SSO
- Map SAML attributes to MedMatch user profile
- Admin configuration page for SAML settings

### 5B. iOS App Build (P2)
**Approach**: PWA-first, then Capacitor/React Native wrapper
- The app already has PWA support (manifest.json, service worker)
- Use Capacitor to wrap the existing React app for App Store
- Add native capabilities: push notifications, biometric auth
- Apple Developer account required ($99/year)

### 5C. Social Media Sharing (P2)
**Approach**: Add share buttons to key areas
- Meeting sharing: LinkedIn, Twitter/X share buttons in ShareMeetingDialog
- Job sharing: Share job listings to social media
- Profile sharing: Public profile link with OG meta tags
- Use `window.open` with pre-filled share URLs (no API keys needed)

### 5D. MeetingHeader Refactoring (Low Priority)
**Current State**: Duplicate inline header in `MeetingRoom.jsx`
**Fix**: Extract and reuse the `MeetingHeader` component
- Single source of truth for meeting room header
- ~30 minutes of work

---

## Technical Debt & Cleanup
- [ ] Consolidate `MeetingHeader` component
- [ ] Consider migrating from deprecated `paypalrestsdk` to PayPal v2 SDK
- [ ] Clean up unused translation scripts in `/app/scripts/`
- [ ] Add automated health monitor check to Dragon Scheduler (weekly)
