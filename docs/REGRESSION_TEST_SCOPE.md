# Regression Test Scope Plan
## Post-Dependency-Upgrade Validation · AI KARAU + ENZI + MedMatch AI

**Run:** testing_agent_v3_fork · **Est. effort:** 1 hour · **Must pass before any P0 sprint work**
**Trigger:** SEC-003 Sprint-1 dependency upgrades (aiohttp 3.13.5, cryptography 46.0.7, PyJWT 2.12.0, pymongo 4.6.3, lxml 6.1.0, pillow 12.2.0, python-multipart 0.0.27, litellm 1.83.7, axios 1.16.0, jspdf 4.2.1, react-router-dom 7.15.0)

## Why This Run Matters

| Change | Risk Surface |
|---|---|
| `python-multipart` 0.0.21 → 0.0.27 | All file upload endpoints |
| `aiohttp` 3.13.3 → 3.13.5 | HTTP client calls (LLM, job APIs) |
| `cryptography` 46.0.3 → 46.0.7 | TLS, JWT signing, encryption at rest |
| `PyJWT` 2.10.1 → 2.12.0 | All token validation paths |
| `pymongo` 4.5.0 → 4.6.3 | All DB read/write |
| `pillow` 11.3.0 → 12.2.0 | Image upload, avatar processing |
| `axios` ^1.8.4 → 1.16.0 | All frontend API calls |
| `jspdf` ^4.0.0 → 4.2.1 | Frontend PDF generation |

## Test Scope — 3 Priority Flows

### Priority 1 — Authentication (12 tests)
Tokens / cookies / OAuth round-trips touching PyJWT + cryptography + python-multipart upgrades.

### Priority 2 — File Upload (10 tests)
Multipart parsing through python-multipart 0.0.27. **Highest regression probability.**

### Priority 3 — PDF Export (7 tests)
Backend reportlab pipeline + frontend jsPDF 4.2.1.

### Extended Scope (6 tests)
WebSocket, ML inference, translation, WebRTC signaling, scheduler, push notifications.

## Pass / Fail Criteria

| Outcome | Action |
|---|---|
| All P1+P2+P3 pass | Proceed to WCAG sprint |
| Any P1 failure | **Stop.** Auth regression blocks everything |
| Any P2 failure | python-multipart 0.0.27 regression — investigate boundary parsing |
| Any P3 failure | jsPDF 4.2.1 or reportlab regression — isolate |

## Credentials
- Admin: `admin@medmatch.com` / `Swampdrainer2026!`
- Test: `test@medmatch.io` / `TestPassword123!`

**Run before:** WCAG accessibility sprint · LiveKit SFU spike · any further dependency changes
