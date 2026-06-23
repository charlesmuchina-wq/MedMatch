# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool), "ENZI" (professional-grade AI messenger), and "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus -- a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React 19 + Tailwind CSS 3.4 + Shadcn/UI + react-markdown
- Backend: FastAPI 0.110.1 + MongoDB 7.0 + emergentintegrations
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (LiteLLM multi-provider routing)
- Payments: Stripe + PayPal (both in test/sandbox mode)
- Auth: Email/password, Google SSO, Microsoft SSO, Apple, GitHub, ORCID, Passkeys/WebAuthn
- Desktop: Electron (Win/Mac/Linux)
- Mobile: Expo SDK 54 + React Native 0.81 (iOS/Android)
- Microsoft: Teams App + Outlook Add-in (pending Azure AD)
- CI/CD: GitHub Actions + Local runner (Phase 1 + Phase 3 gates)

## Codebase Metrics
- Backend: 228 Python files, 96,680 LOC, 131 route modules, 71 services
- Frontend: 324 source files, 89,801 LOC, 92 pages, 161 components
- Database: 173 MongoDB collections
- Dependencies: 212 backend packages, 71 frontend packages

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| Phase 1 (iteration_216) | Functional Testing - Gate G1 | 59/59 PASS |
| Phase 2 (iteration_217) | Reliability Testing - Gate G2 | 31/31 PASS |
| Phase 3 (iteration_218) | Post-Reliability Regression - Gate G3 | 41/41 PASS |
| Phase 4 (iteration_219) | Deployment Readiness - Gate G4 | 54/54 PASS |
| Iteration 220 | CI/CD + Email + Refactoring + Triggers | 19/19 PASS |
| **Grand Total** | | **204/204 PASS** |

## Functional Assessment — Iteration 222 (June 23, 2026)
Scope: core flows of all three portals + last-shipped webinar speaker queue. Report: `/app/test_reports/iteration_222.json`.
- **Backend: 100% (10/10 PASS)** — admin auth, karau-meet meeting CRUD, LiveKit token mint, /api/livekit/token + /status, ENZI /api/lumi/channels, observability error list+stats.
- **Frontend: ~85% → improved** — Portal selector renders all 3 apps; admin login OK; MedMatch (/resume, /agents, /meeting-notes) load clean; KARAU /webinars (WebinarManagementPage) + /karau-meet load; ENZI /lumi has its own separate "Sign in to ENZI" auth (by design); /admin/errors observability works end-to-end.
- **Findings & fixes:**
  - FIXED: `/karau-meet/webinar/{id}/live` was unreachable for guests — the `!user` login gate in `KarauMeetPortal.jsx` ran before the webinar-live check, bouncing lobby-routed guests to KARAU login. Adjusted gate to allow `isWebinarLiveRoom`. This also unblocks in-app verification of the speaker-queue feature.
  - NOTE (by design): KARAU and ENZI use their own portal auth, separate from MedMatch `access_token`. Tester's "fallback to landing" was the KARAU login page, not a routing defect.
  - Speaker queue (raise hand → host queue → Promote next) is code-complete and now reachable; full live 2-participant LiveKit verification still pending a real livekit-mode webinar room.
  - LOW/cosmetic (open): Google Identity Services bootstrap console error on /resume (page renders fine); webinar card description overflow already mitigated with line-clamp-2.

## All Features (Implemented & Tested)
1-29: See CHANGELOG.md for complete list

## Completed This Session (March 22, 2026 + Feb 8, 2026)
- CI/CD Pipeline Fix v2: Resolved `numpy` version conflict (scipy vs python-jobspy), fixed shell escaping in seed script (heredoc), added system dependencies and diagnostic output
- **CI/CD Pipeline Fix v3 (Feb 8) — VALIDATED GREEN ✅**: Added `/app` symlink-to-workspace step in both Phase 1 and Phase 3 jobs of `.github/workflows/test.yml` to fix `PermissionError: '/app'` from hardcoded paths in `capa_service.py`, `ai_qa/*`, `video_*.py`, and `server.py`. User confirmed run #11 passing.
- **G5 CISO Security Evidence Pack (Feb 8)** — under `/app/docs/security/`:
  - `G5_CISO_EVIDENCE_PACK.md` — SAST/DAST baseline (Bandit + ESLint Security)
  - `G5_DELTA_REPORT.md` — Post-remediation: 0 HIGH (Bandit), 0 ERROR (ESLint security)
  - `SEC003_DEPENDENCY_AUDIT.md` — pip-audit + yarn audit (242 CVEs identified)
  - `SEC003_SPRINT1_DELTA.md` — Post-Sprint-1: 1 CRITICAL → 0, 65 CVEs eliminated
- **Security Patches Applied**:
  - SEC-001: `usedforsecurity=False` on 10× hashlib calls (digest, dragon_automator, server, edge_tts, job_sources, video_asset_manager, web_job_crawler)
  - SEC-002: ReDoS hardening — bounded regexes in `KarauDragonAI.jsx` (lines 211, 269)
  - SEC-003 Sprint-1: Backend pkgs aiohttp 3.13.5 / cryptography 46.0.7 / PyJWT 2.12.0 / pymongo 4.6.3 / lxml 6.1.0 / python-multipart 0.0.27 / pillow 12.2.0 / litellm 1.83.7. Frontend pkgs jspdf 4.2.1 / axios 1.16.0 / react-router-dom 7.15.0 (+ transitive dompurify 3.4.2)
- **Regression Validation (Feb 8) — 104/104 PASS ✅** via `testing_agent_v3_fork`: existing baselines (`test_phase1_functional.py` 59/59, `test_phase3_regression.py` 41/41) + multipart spot-check 4/4. Zero regressions from SEC-003. Bonus fix: `routes/resume.py:279` malformed-PDF now returns HTTP 400 (was 500). Full report at `/app/test_reports/iteration_regression_post_sec003.json`.
- **WCAG 2.2 AA Sprint-1 Day 1 (Feb 8) — Public-route in-codebase findings: 0 critical, 0 serious ✅**:
  - Plan canonicalized at `/app/docs/WCAG_AUDIT_REMEDIATION_PLAN.md` (12 items + 5 G1 tests)
  - axe-core 4.11 + Playwright scanner: `/app/frontend/scripts/wcag_audit.cjs` + `wcag_audit_auth.cjs`
  - Public scan: 13C/6S → **0C/0S** (in-codebase). Remaining 12 critical = single external Emergent platform badge `<img>` (production-deploy removes it).
  - Authenticated scan: token-injection bypass via API login (admin@medmatch.com)
  - **Fixes applied**: WCAG-02 SkipNav (`/components/a11y/SkipNav.jsx` + `App.js` `<main id="main-content" tabIndex={-1}>`), WCAG-01 LoginPage password-toggle aria-label/aria-pressed/24px target, WCAG-06 contrast (Tabs `text-slate-700` inactive, Submit `bg-teal-700`, Sign Up `text-teal-700`)
  - Populated tracker at `/app/docs/security/WCAG_REMEDIATION_TRACKER_DAY1.md`
  - **Score estimate: ~25/100 → ~70/100** (target 85+/100 in remaining sprint)
- **WCAG 2.2 AA Sprint-1 Day 2 (Feb 8) — All sprint exit criteria met ✅**:
  - **Phase 4 accessibility CI gate** added to `.github/workflows/test.yml` (Node 20 + Playwright Chromium, fails build on critical/serious, posts PR comment, uploads artifact)
  - `wcag_audit.cjs` upgraded with CLI single-URL mode + permanent `#emergent-badge` exclude (documented inline)
  - **WCAG-08 Live region announcer** infrastructure: `frontend/src/utils/announcer.js` + global `<div id="toast-announcer" role="status" aria-live="polite" aria-atomic="true" className="sr-only" />` mounted at App root
  - **WCAG-10 KARAU controls**: `MeetingRoom.jsx` controls bar wrapped in `role="toolbar"` with `aria-pressed` toggle states + `aria-label` on mute/video/screen/leave, all icons `aria-hidden`
  - **WCAG-11 ENZI messenger**: `EnziChatView.jsx` thread wrapped in `role="log" aria-live="polite" aria-relevant="additions"`, compose is now real `<form>` with hidden `<label htmlFor>` + `aria-describedby` Enter-to-send hint
  - **WCAG-04 Skipped** — Shadcn Dialog uses Radix Primitive which natively provides focus trap; adding `focus-trap-react` would be redundant. Documented rationale.
  - **ACC-01..05 G1 gate tests** added to `test_phase1_functional.py` — all 5 PASS. **G1 = 64/64 ✅**
  - Final tracker at `/app/docs/security/WCAG_REMEDIATION_TRACKER_DAY2.md`. **Score estimate: ~85/100** ✅
- System Requirements / File Inventory / SWOT / Execution Framework / RICE Cadence audit docs (March 22)

## Next Action Items (Detailed playbook: /app/docs/PRODUCTION_LAUNCH_PLAYBOOK.md)

### P0 — CI/CD Pipeline Verification
- User must "Save to GitHub" to trigger the fixed pipeline
- Pipeline includes system deps, sed-based numpy conflict resolution, heredoc seed script, diagnostic output

### Task 2 — Register Azure AD for Teams/Outlook
Prerequisites: Azure sub with Global Admin role, redirect URIs, tenant ID
- User status: "No to Azure / not sure"

### Task 3 — Obtain CISO Security Sign-Off (Gate G5)
Prerequisites: threat model, pen test report, SAST/DAST results, data flow diagrams, incident response plan

### Task 1 — Submit Platform Builds (blocked by Tasks 2 & 3)
Prerequisites: release branch, signing certs, store access

## Future/Backlog
- P1: Real-time Deployment Dashboard
- P2: Production Monitoring & CRS Dashboard
- P2: Chrome Extension
- P3: Enterprise Customer Onboarding

## Deployment Gate Status
| Gate | Status |
|------|--------|
| G1 Functional | PASSED |
| G2 Reliability | PASSED |
| G3 Regression | PASSED |
| G4 Platform Cert | Prerequisites Met (store submissions pending) |
| G5 Security | **Conditional GO** — SAST/DAST clean (0 HIGH, 0 ERROR), CRITICAL CVE closed, 23 backend + 153 frontend low/transitive CVEs in Sprint-2 backlog |

## Audit Documents
| Document | Path |
|----------|------|
| System Requirements | `/app/docs/SYSTEM_REQUIREMENTS_AUDIT.md` |
| File Inventory | `/app/docs/FILE_INVENTORY_AUDIT.md` |
| Technical SWOT Audit | `/app/docs/TECHNICAL_SWOT_AUDIT_22_03_2026.md` |
| Execution Framework | `/app/docs/EXECUTION_FRAMEWORK_22_03_2026.md` |
| RICE Cadence Roadmap | `/app/docs/CADENCE_ROADMAP_22_03_2026.md` |
| Development Analyst Report | `/app/docs/DEVELOPMENT_ANALYST_REPORT_22_03_2026.md` |
| Production Launch Playbook | `/app/docs/PRODUCTION_LAUNCH_PLAYBOOK.md` |
| Gap Assessment | `/app/docs/GAP_ASSESSMENT.md` |
| Testing Strategy | `/app/docs/TESTING_STRATEGY_RESULTS.md` |
| Deployment Readiness | `/app/docs/DEPLOYMENT_READINESS.md` |
