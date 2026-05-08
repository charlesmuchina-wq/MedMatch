# AI Suite — Autonomous Project Architect Execution Framework
## Master Task Board | Session: MEDMATCH_22/03/2026

**Document Classification:** Internal — Engineering Leadership  
**Framework Version:** 1.0  
**Principle Constraints:** DRY (Don't Repeat Yourself) | Zero-Trust Security  

---

## Table of Contents

1. [Workstream Decomposition](#1-workstream-decomposition)
2. [Master Task Board — Deliverables & Artifacts](#2-master-task-board)
3. [Verification & Validation (V&V) Matrix](#3-verification--validation)
4. [Preservation & Guardrails](#4-preservation--guardrails)
5. [AI Innovation Triggers](#5-ai-innovation-triggers)
6. [Self-Healing Resolution Table](#6-self-healing-resolution-table)
7. [Progress Cadence — Weekly Tracking Schema](#7-progress-cadence)

---

## 1. Workstream Decomposition

```
WS-1  WCAG 2.2 Accessibility ─────────── P0 ── Week 1-3
WS-2  CI/CD Pipeline Stabilization ───── P0 ── Week 1
WS-3  CISO Security G5 Sign-Off ──────── P0 ── Week 1-4
WS-4  Video Architecture (LiveKit SFU) ─ P0 ── Week 1-6
WS-5  Platform Deployment (Wave 1-4) ─── P0 ── Month 1-4
WS-6  Architecture Modernization ──────── P1 ── Week 5-12
WS-7  AI Innovation Layer ────────────── P1 ── Week 13-24
WS-8  Integration Bridge Hardening ───── P1 ── Week 2-4
```

**Critical Path:**
```
WS-2 (CI/CD) ──→ WS-1 (WCAG) ──→ WS-3 (CISO) ──→ WS-5 Wave 1
                                                      ↑
WS-4 (LiveKit) ─────────────────────────────────────── ┘
```

---

## 2. Master Task Board — Deliverables & Artifacts

### WS-1: WCAG 2.2 Accessibility Remediation (P0)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS1-01 | Aria-label injection across all interactive elements | Modified `.jsx` files (est. 324 files) | `grep -rn 'aria-label' src/ \| wc -l` >= 1,500 (from current 14) | Frontend | Week 1 |
| WS1-02 | Keyboard navigation + tabIndex | Modified `.jsx` files | All interactive elements reachable via Tab key; zero keyboard traps; `tabIndex` count >= 200 | Frontend | Week 1 |
| WS1-03 | Focus management (modals, dialogs) | Focus trap utility + integration | Every modal/dialog traps focus; Escape closes; focus returns to trigger element | Frontend | Week 1 |
| WS1-04 | Skip-navigation component | `SkipNav.jsx` component in layout | First Tab press reveals "Skip to main content" link; link jumps past nav | Frontend | Week 1 |
| WS1-05 | Color contrast remediation | Updated CSS variables / Tailwind config | All text passes WCAG 4.5:1 (AA); verified via axe-core automated scan: 0 contrast violations | Frontend | Week 2 |
| WS1-06 | Screen reader validation report | `docs/WCAG_SCREEN_READER_REPORT.md` | VoiceOver (macOS/iOS), TalkBack (Android), NVDA (Windows) tested on 5 critical flows: login, job search, meeting join, messenger, resume builder | QA | Week 2 |
| WS1-07 | WCAG automated test suite | `tests/test_accessibility.py` (5+ tests: ACC-01 to ACC-05) | Tests integrated into G1 gate; all pass in CI | QA | Week 2 |
| WS1-08 | Touch target sizing (24x24 min) | Modified button/link styles | All interactive targets >= 24x24 CSS pixels; verified via axe-core | Frontend | Week 2 |
| WS1-09 | Drag alternative controls | Button alternatives for all drag interactions | Every drag operation has a button/keyboard alternative (WCAG 2.5.7) | Frontend | Week 3 |

### WS-2: CI/CD Pipeline Stabilization (P0)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS2-01 | Dependency conflict resolution | `.github/workflows/test.yml` | `pip install` succeeds without `--no-deps` workaround; zero `ResolutionImpossible` errors | DevOps | Day 1 |
| WS2-02 | Core requirements file | `backend/requirements-core.txt` | Contains only direct dependencies (est. 40-50 packages) vs. full freeze (212); pip resolves cleanly | DevOps | Day 2 |
| WS2-03 | CI pipeline green confirmation | GitHub Actions run #N (screenshot/artifact) | All 204 tests pass; Phase 1 (59) + Phase 3 (41) green; artifact uploaded | DevOps | Day 1-2 |
| WS2-04 | Dependency audit CI step | New step in `test.yml`: `pip audit` | Zero known CVEs in production dependencies; runs on every push | DevOps | Day 3 |
| WS2-05 | CI caching for pip/yarn | Cache steps in `test.yml` | Install time < 60 seconds (from current ~120s); uses `actions/cache@v4` | DevOps | Day 3 |

### WS-3: CISO Security G5 Sign-Off (P0)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS3-01 | STRIDE threat model | `docs/security/THREAT_MODEL.md` | Covers all 6 STRIDE categories for each portal; reviewed by security lead | Security | Week 1 |
| WS3-02 | Data flow diagrams | `docs/security/DATA_FLOW_DIAGRAMS.md` (+ Mermaid/draw.io) | Covers: user auth flow, meeting data flow, messenger E2EE flow, payment flow, AI inference flow | Security | Week 1 |
| WS3-03 | SAST results (backend) | `reports/sast_bandit_results.json` | Bandit scan: 0 high-severity findings; all mediums have documented mitigations | DevOps | Week 2 |
| WS3-04 | SAST results (frontend) | `reports/sast_eslint_security.json` | ESLint security plugin: 0 errors; all warnings documented | DevOps | Week 2 |
| WS3-05 | DAST results | `reports/dast_zap_results.html` | OWASP ZAP scan against staging: 0 high-risk alerts; mediums mitigated | Security | Week 2 |
| WS3-06 | Penetration test report | `reports/pentest_report.pdf` (external vendor) | External firm engagement; report delivered; all critical/high findings remediated | Security | Week 3 |
| WS3-07 | Incident response plan | `docs/security/INCIDENT_RESPONSE_PLAN.md` | Covers: detection, triage, containment, eradication, recovery, post-mortem; reviewed by ops lead | Security | Week 2 |
| WS3-08 | Encryption documentation | `docs/security/ENCRYPTION_SPEC.md` | Documents: TLS config, E2EE protocol, key management, at-rest encryption, JWT signing | Security | Week 2 |
| WS3-09 | G5 evidence pack assembly | `docs/security/G5_EVIDENCE_PACK/` (folder) | All 8 artifacts above compiled; executive summary written; CISO briefing scheduled | Security | Week 3 |
| WS3-10 | G5 sign-off | Signed approval document | CISO approval recorded; gate status updated to PASSED | CISO | Week 4 |

### WS-4: Video Architecture — LiveKit SFU (P0)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS4-01 | LiveKit evaluation spike | `docs/architecture/LIVEKIT_EVALUATION.md` | Covers: self-hosting vs. cloud, cost model, SDK compatibility, latency benchmarks, migration plan | Backend | Day 1-3 |
| WS4-02 | Architecture decision record | `docs/architecture/ADR-001-SFU.md` | Option A vs B decision documented; signed by tech lead; timeline confirmed | Architect | Day 3 |
| WS4-03 | LiveKit server deployment | `docker-compose.livekit.yml` or K8s manifest | LiveKit instance running; health endpoint responding; TURN/STUN configured | DevOps | Week 2 |
| WS4-04 | Backend SFU integration | Modified `karau_webrtc.py`, `karau_meet.py`, new `services/karau_meet/livekit_service.py` | Room creation API works; token generation works; participant join/leave events flow | Backend | Week 2-3 |
| WS4-05 | Frontend SFU integration | Modified `MeetingRoom.jsx`, new `hooks/useLiveKit.js` | Video/audio connects via SFU; screen share works; 20+ simultaneous participants tested | Frontend | Week 3-4 |
| WS4-06 | Migration compatibility layer | Abstraction in `hooks/useWebRTC.js` | P2P and SFU both work via same hook interface; feature flag toggles mode | Frontend | Week 4 |
| WS4-07 | Load test report | `reports/livekit_load_test.md` | 50 concurrent participants; p95 latency < 200ms; zero dropped frames at 720p | QA | Week 5 |
| WS4-08 | Recording integration | Modified `karau_recordings.py` | SFU recordings saved to storage; replay works with Director Cuts | Backend | Week 5-6 |

### WS-5: Platform Deployment (Waves 1-4)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS5-01 | iOS TestFlight build | `.ipa` + TestFlight submission | Build accepted by Apple; internal testers can install; crash-free rate > 99.5% | Mobile | Week 2 |
| WS5-02 | Android internal testing | `.aab` + Play Console internal track | Build accepted by Google; APK size < 50MB; data safety form approved | Mobile | Week 2 |
| WS5-03 | Web/PWA canary deployment | Production URL + service worker | Lighthouse PWA score >= 90; offline mode works; 5% traffic canary with rollback | DevOps | Week 2 |
| WS5-04 | Wave 1 GA launch | All 3 platforms at 100% traffic | Crash-free >= 99.0%; CRS >= target; zero encryption errors for 72h | Release | Week 4 |
| WS5-05 | Windows MSIX package | Signed `.msix` + Microsoft Store listing | EV code-signed; WACK test pass; Store certification approved | Desktop | Month 2 |
| WS5-06 | macOS Universal Binary | Signed `.dmg` + Mac App Store listing | Universal (Intel+ARM); notarized by Apple; Gatekeeper passes | Desktop | Month 2 |
| WS5-07 | Linux packages | `.deb`, `.rpm`, `.flatpak` + Flathub listing | GPG signed; Flathub review approved; AppArmor/SELinux compatible | Desktop | Month 3 |
| WS5-08 | Chrome Extension | Manifest V3 `.crx` + Chrome Web Store listing | MV3 compliant; Store review approved; CSP headers correct | Frontend | Month 3 |
| WS5-09 | M365 Teams App | Teams app manifest + Partner Center submission | M365 certification passed; MSAL SSO works; Graph API permissions granted | Backend | Month 3-4 |
| WS5-10 | Enterprise API GA | OpenAPI 3.1 spec + developer portal | Spec published; sandbox environment live; rate limiting works; SLA contract template ready | Backend | Month 3-4 |

### WS-6: Architecture Modernization (P1)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS6-01 | Sentry integration | `sentry.init()` in frontend + backend | Errors captured in Sentry dashboard; source maps uploaded; alerts configured | DevOps | Week 5 |
| WS6-02 | God file decomposition | Split `lumi_messenger.py` (2,466 → 5 files < 500 LOC each) | All existing tests pass; no behavior change; import paths updated | Backend | Week 5-6 |
| WS6-03 | Frontend state management (Zustand) | `stores/` directory + migration of top-20 useState chains | Top 20 components migrated; prop drilling reduced by 50%+; all tests pass | Frontend | Week 6-8 |
| WS6-04 | CRA → Vite migration | `vite.config.ts` replaces Craco/CRA | Dev server starts in < 3s (vs ~15s); HMR < 100ms; all 324 files build | Frontend | Week 8-9 |
| WS6-05 | Redis caching layer | Redis config + cache middleware | Session cache: Redis; rate limit state: Redis; cache hit rate > 60% on hot paths | Backend | Week 7 |
| WS6-06 | Vector search implementation | Atlas Vector Search or Meilisearch config | Semantic job search returns relevant results; query latency < 200ms; embedding pipeline runs | Backend | Week 9-10 |
| WS6-07 | OpenTelemetry tracing | OTEL collector config + instrumented routes | Traces visible in Grafana/Jaeger; p95 latency dashboards; top-10 slow endpoints identified | DevOps | Week 10 |
| WS6-08 | `datetime.utcnow()` cleanup | 46 files modified | `grep -rn 'utcnow' backend/ \| wc -l` = 0; all use `datetime.now(timezone.utc)` | Backend | Week 5 |
| WS6-09 | Exception handling tightening | 424 `except Exception` → specific catches | Broad catches reduced to < 50; specific exception types for DB, HTTP, AI, validation | Backend | Week 6-8 |
| WS6-10 | Test coverage expansion | 20+ new test files targeting critical paths | Coverage from 4.4% → 25%+; auth, payments, meetings, messenger, smart-apply covered | QA | Week 5-12 |

### WS-7: AI Innovation Layer (P1)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS7-01 | Agentic job application agent | `services/agents/job_agent.py` + `routes/agents.py` | Autonomously finds, matches, applies to jobs matching resume; human approval gate configurable | AI/ML | Week 13-16 |
| WS7-02 | RAG pipeline (cross-portal) | `services/rag/` + vector embeddings | "Ask anything" query returns relevant context from jobs + meetings + messages; latency < 2s | AI/ML | Week 14-17 |
| WS7-03 | Meeting scheduling agent | `services/agents/scheduling_agent.py` | Autonomously proposes meeting times based on calendar + conversation context; conflict detection | AI/ML | Week 16-18 |
| WS7-04 | Predictive caching | `services/predictive_cache.py` | ML model predicts user's next action; pre-fetches API responses; cache hit rate > 40% | AI/ML | Week 18-20 |
| WS7-05 | NLP-based structured logging | `services/nlp_logger.py` | Converts unstructured error messages to structured JSON; auto-categorizes by severity/component | AI/ML | Week 20-22 |
| WS7-06 | Developer API marketplace | `routes/marketplace.py` + SDK + docs | Third-party bot registration API; OAuth2 for apps; webhook delivery; sandbox environment | Backend | Week 18-24 |

### WS-8: Integration Bridge Hardening (P1)

| ID | Deliverable | Artifact | Success Criteria | Owner | ETA |
|----|-------------|----------|-----------------|-------|-----|
| WS8-01 | Bridge contract tests | `tests/test_bridge_contracts.py` | Tests: schedule push (ENZI→KARAU), video→meeting, post-meeting sync; all pass | QA | Week 2 |
| WS8-02 | Graceful degradation (ENZI when KARAU down) | Circuit breaker in `enzi_meetings.py` | ENZI messenger functions normally when KARAU service is unreachable; timeout < 3s | Backend | Week 3 |
| WS8-03 | Bridge monitoring dashboard | Grafana/custom dashboard | Real-time: bridge message queue depth, sync latency, failure rate; alerts at > 1% failure | DevOps | Week 4 |
| WS8-04 | Integration regression suite | `tests/test_integration_bridge.py` | Full regression on every PR touching bridge files (4 files, 3,867 LOC); runs in CI | QA | Week 3 |

---

## 3. Verification & Validation (V&V) Matrix

### Automated Test Cases

| Workstream | Test ID | Automated Test | Tool | Pass Criteria |
|------------|---------|---------------|------|---------------|
| WS-1 | ACC-01 | `axe-core` scan on all pages | axe-core + playwright | 0 critical/serious violations |
| WS-1 | ACC-02 | Keyboard tab order test on 5 critical flows | playwright script | All elements reachable via Tab; no traps |
| WS-1 | ACC-03 | Color contrast ratio check | axe-core | 0 contrast violations (4.5:1 AA) |
| WS-1 | ACC-04 | `aria-label` coverage check | custom grep script | `aria-label` count >= 1,500 |
| WS-1 | ACC-05 | Touch target size validation | axe-core custom rule | All interactive elements >= 24x24px |
| WS-2 | CI-01 | Full pipeline execution | GitHub Actions | All 204+ tests pass; exit code 0 |
| WS-2 | CI-02 | Dependency vulnerability scan | `pip audit` | 0 known CVEs in production deps |
| WS-2 | CI-03 | Dependency conflict check | `pip check` | 0 conflicts reported |
| WS-3 | SEC-01 | Bandit SAST scan | Bandit | 0 high-severity findings |
| WS-3 | SEC-02 | ESLint security scan | eslint-plugin-security | 0 error-level findings |
| WS-3 | SEC-03 | OWASP ZAP DAST scan | ZAP | 0 high-risk alerts |
| WS-4 | SFU-01 | Room creation + join + leave | pytest | API returns 200; room_id valid; events fire |
| WS-4 | SFU-02 | 20-participant load test | k6 / custom script | All 20 connect; p95 latency < 200ms |
| WS-4 | SFU-03 | Recording start/stop | pytest | Recording file created; playback works |
| WS-5 | PLT-01 | Lighthouse PWA audit | Lighthouse CI | Score >= 90 (PWA category) |
| WS-5 | PLT-02 | iOS crash-free rate | TestFlight analytics | >= 99.5% over 48h |
| WS-5 | PLT-03 | Android crash-free rate | Play Console | >= 99.5% over 48h |
| WS-6 | MOD-01 | Import path validation post-decomposition | pytest | All existing 204 tests pass unchanged |
| WS-6 | MOD-02 | Redis cache hit rate | custom metric | >= 60% on `/api/jobs/search`, `/api/lumi/channels` |
| WS-8 | BRG-01 | ENZI → KARAU schedule push | pytest | Meeting created from ENZI; meeting_id returned |
| WS-8 | BRG-02 | KARAU → ENZI post-meeting sync | pytest | Chat messages appear in ENZI channel < 5s |
| WS-8 | BRG-03 | ENZI graceful degradation | pytest (KARAU mocked as down) | ENZI responds normally; error logged; no crash |

### Manual Sanity Check Protocols

| Workstream | Check ID | Manual Protocol | Frequency | Validator |
|------------|----------|----------------|-----------|-----------|
| WS-1 | MAN-ACC-01 | Navigate entire login → dashboard → job search flow using ONLY keyboard (no mouse). Every element must be reachable and usable. | Per sprint | QA Lead |
| WS-1 | MAN-ACC-02 | Enable VoiceOver (macOS) / TalkBack (Android). Complete: login, search job, apply. All content must be read aloud correctly. | Pre-Wave 1 | QA Lead |
| WS-1 | MAN-ACC-03 | Zoom browser to 400%. All content must reflow to single column (no horizontal scroll). | Pre-Wave 1 | Frontend Lead |
| WS-3 | MAN-SEC-01 | Walk through data flow diagrams with CISO. Verify each arrow has encryption annotation. | Pre-G5 | Security Lead |
| WS-3 | MAN-SEC-02 | Attempt top-5 OWASP attacks manually on staging: SQLi, XSS, CSRF, IDOR, broken auth. | Pre-G5 | Pen Tester |
| WS-4 | MAN-SFU-01 | Join meeting with 10 participants on different networks (mobile + desktop + tablet). Verify audio/video quality subjectively (MOS >= 3.5). | Pre-Wave 1 | QA Team |
| WS-5 | MAN-PLT-01 | Install iOS build via TestFlight. Complete full flow: register → search job → join meeting → send message. | Pre-Wave 1 | PM + QA |
| WS-5 | MAN-PLT-02 | Install Android build from internal track. Same flow as MAN-PLT-01. | Pre-Wave 1 | PM + QA |
| WS-8 | MAN-BRG-01 | In ENZI, type `/meet` to create a meeting. Join in KARAU. Send chat. Return to ENZI. Verify chat synced. | Per sprint | QA Lead |

---

## 4. Preservation & Guardrails — "Do Not Change" Registry

### Legacy Dependencies (Protected)

| Component | File(s) | Constraint | Reason |
|-----------|---------|-----------|--------|
| **MongoDB connection** | `server.py:57-69` | `MONGO_URL` and `DB_NAME` from env only; database name = `MedMatch` | Changing DB name breaks all 173 collections; standardized in iteration 220 |
| **JWT authentication flow** | `routes/auth.py:25` | `JWT_SECRET` via `os.environ.get("JWT_SECRET_KEY", ...)` | All active sessions invalidated on change; zero-trust boundary |
| **E2EE key exchange** | `routes/e2ee.py` | Client-side key generation; server stores encrypted blobs only | Server must NEVER see plaintext keys; compliance requirement |
| **WebRTC signaling protocol** | `services/karau_meet/webrtc_signaling.py` | Signal format must remain backward-compatible for P2P fallback | LiveKit migration (WS-4) must wrap, not replace, existing signals |
| **Emergent LLM Key routing** | All `EMERGENT_LLM_KEY` consumers | Key sourced from env; routes through `emergentintegrations` library | Key is shared across OpenAI/Gemini/Claude; breaking = all AI features down |
| **Bridge contract: ENZI → KARAU** | `routes/meeting_channel_sync.py`, `routes/enzi_meetings.py` | API contract (request/response schema) must not change without bridge regression | Unified suite moat depends on this; failure cascades across portals |
| **Trust score formula** | `services/trust_score.py` | CRS = (Uptime x 0.35) + (AI Accuracy x 0.30) + (HFI x 0.20) + (Integration Stability x 0.15) | Enterprise SLAs reference this formula; changing requires legal review |
| **Frontend env vars** | `frontend/.env` | `REACT_APP_BACKEND_URL` — never delete | K8s ingress routing depends on this value |
| **Backend env vars** | `backend/.env` | `MONGO_URL`, `DB_NAME` — never delete or rename | Production DB connection; renaming = outage |
| **Rate limiter config** | `services/global_rate_limiter.py` | Rate limits per endpoint must not be relaxed without security review | Zero-trust: every relaxation is a potential DDoS vector |

### Core Business Logic (Protected)

| Logic | Location | Guard |
|-------|----------|-------|
| Smart Apply cover letter generation | `routes/smart_apply.py` | AI prompt engineering is tuned; changes require A/B test validation |
| Behavioral prediction ML model | `services/ml_model_trainer.py` | Model version pinned; retraining requires bias audit (WS7 governance) |
| Payment flow (Stripe + PayPal) | `routes/payments.py` | Webhook signatures verified; amount calculation logic frozen |
| ORCID OAuth redirect | `routes/orcid_oauth.py` | Redirect URIs registered with ORCID; changes require ORCID reconfiguration |
| Meeting-to-channel mapping | `routes/meeting_channel_sync.py` | 1:1 mapping between KARAU meeting_id and ENZI channel_id is contractual |

---

## 5. AI Innovation Triggers

| Module | AI/ML Injection Point | Trigger Event | Expected Outcome | Priority |
|--------|----------------------|---------------|-----------------|----------|
| **Job Search** (`routes/jobs.py`) | Vector embeddings + semantic matching | User searches with natural language query (not keyword) | Results ranked by meaning, not keyword frequency; relevance score > 80% | P1 (WS6-06) |
| **Meeting Scheduling** (`routes/karau_scheduling.py`) | Calendar inference agent | User says "schedule a meeting with team" in ENZI | Agent proposes optimal time based on all calendars; conflict resolution | P1 (WS7-03) |
| **Messenger** (`routes/lumi_messenger.py`) | Predictive reply suggestions | User opens conversation thread | 3 contextual reply suggestions shown; click-through rate > 15% | P2 |
| **Error Logging** (`services/ai_supervisor.py`) | NLP log classification | New error logged with unstructured message | Auto-classified: severity (P0-P3), component, suggested fix; < 500ms | P2 (WS7-05) |
| **API Gateway** (`server.py` middleware) | Predictive caching | User navigates to dashboard | Pre-fetches top-3 likely next API calls based on behavior model; cache hit rate > 40% | P2 (WS7-04) |
| **Recruitment CRM** (`routes/talent_crm.py`) | Churn prediction | Candidate hasn't responded in > 7 days | AI flags at-risk candidates; suggests re-engagement template; < 2% false positive | P2 |
| **Translation** (`routes/translation.py`) | Quality prediction before publish | New translation submitted | AI scores quality (1-5) before human review; filters < 3.0 for manual review | P3 |
| **Meeting Intelligence** (`routes/meeting_intelligence.py`) | Real-time topic detection | Meeting in progress > 5 minutes | Auto-generates live agenda items; detects topic drift; notifies host | P3 |
| **Trust Scoring** (`services/trust_score.py`) | Anomaly detection on CRS components | CRS component deviates > 2 standard deviations | Auto-alert + root-cause hypothesis generated; < 1 min detection latency | P1 |
| **Smart Apply** (`routes/smart_apply.py`) | Application success prediction | User selects job to auto-apply | Shows probability of callback before applying; calibration error < 5% | P2 |

---

## 6. Self-Healing Resolution Table

### Autonomous Resolution Logic

| # | Common Error | Detection Method | AI-Automated Resolution | Escalation Trigger | Escalation Target |
|---|-------------|-----------------|------------------------|--------------------|--------------------|
| SH-01 | MongoDB connection timeout | Motor raises `ServerSelectionTimeoutError` | Exponential backoff retry (3 attempts, 1s/2s/4s); switch to read-replica if primary down | 3 consecutive failures in 60s | On-call DevOps (PagerDuty) |
| SH-02 | LLM API rate limit (429) | `emergentintegrations` returns 429 | Auto-failover: OpenAI → Gemini → Claude (LiteLLM routing); queue request for retry in 30s | All 3 providers return 429 within 5 min | AI/ML Lead + Budget alert |
| SH-03 | JWT token expired during request | `401 Unauthorized` from auth middleware | Frontend auto-refreshes token via `/api/auth/refresh`; retries original request | Refresh also returns 401 (session truly expired) | User redirected to login |
| SH-04 | CI/CD `pip install` conflict | `ResolutionImpossible` in GitHub Actions log | CI step auto-runs: `sed` numpy pin relaxation → `--no-deps` fallback → core package install | Fallback also fails | DevOps Lead (Slack alert) |
| SH-05 | WebRTC TURN server unreachable | ICE connection state = `failed` | Auto-switch to backup TURN (Xirsys → Twilio); if both fail, fallback to relay-only mode | All TURN servers unreachable for > 2 min | DevOps + Network team |
| SH-06 | Meeting participant exceeds P2P limit | 5th participant join attempt on P2P room | If LiveKit available: auto-upgrade room to SFU mode; if not: queue with "room full" message | > 3 queued participants for > 1 min | Product (capacity decision) |
| SH-07 | Stripe webhook signature mismatch | `stripe.error.SignatureVerificationError` | Log full headers + body (redacted); retry verification with alternate signing secret | 5 consecutive mismatches in 10 min | Security Lead (potential attack) |
| SH-08 | Translation API timeout | LLM call for translation exceeds 30s | Return cached translation if available; fallback to Google Translate API; queue for async retry | No cache + no fallback available | AI/ML Lead |
| SH-09 | Memory pressure on backend | `psutil.virtual_memory().percent > 90%` | Dragon scheduler pauses non-critical background jobs; GC forced; alert sent | Memory > 95% for > 5 min | DevOps (auto-restart pod) |
| SH-10 | Frontend chunk load failure | `ChunkLoadError` in browser console | Auto-retry chunk load (3 attempts); if persistent, hard reload page; if still failing, serve cached version | 3 hard reloads fail | Frontend Lead |
| SH-11 | E2EE key exchange failure | Client reports `key_exchange_failed` event | Retry key exchange (2 attempts); if fails, offer unencrypted fallback with explicit user consent | User declines unencrypted; 3 failures in session | Security Lead |
| SH-12 | CRS drops below SLA threshold | `production_metrics` reports CRS < target for > 15 min | Auto-trigger: disable non-essential features (gamification, predictions); redirect traffic to healthy region | CRS < target for > 30 min | Incident Commander |
| SH-13 | Crash-free rate drops below 99.0% | App store analytics / Sentry crash rate | Auto-pause rollout (Wave 1 traffic ramp); generate crash report digest; notify release team | Rate < 98.5% | Release Manager (rollback) |
| SH-14 | Bot marketplace bot crashes | Bot execution throws unhandled exception | Auto-disable bot for user; log error; notify bot developer webhook; retry with sandboxed execution | Same bot crashes > 5 times in 1 hour | Platform team (bot delisted) |

### Resolution Flow Diagram

```
Error Detected
     │
     ├── Matches Known Pattern? ──Yes──→ Execute Auto-Resolution
     │                                        │
     │                                   Resolved? ──Yes──→ Log + Continue
     │                                        │
     │                                       No
     │                                        │
     │                                   Escalation Trigger Met? ──Yes──→ Alert Human
     │                                        │
     │                                       No
     │                                        │
     │                                   Retry with backoff ──→ Loop (max 3)
     │
     └── Unknown Pattern? ──→ NLP Logger classifies (WS7-05)
                                   │
                                   ├── Creates structured alert
                                   └── Suggests resolution hypothesis
```

---

## 7. Progress Cadence — Weekly Scope Tracking Schema

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AI Suite Weekly Progress Report",
  "type": "object",
  "required": ["report_id", "week_number", "date_range", "workstreams", "velocity", "tech_debt", "blockers", "decisions_needed"],
  "properties": {
    "report_id": {
      "type": "string",
      "pattern": "^MEDMATCH-WPR-\\d{4}-W\\d{2}$",
      "description": "Format: MEDMATCH-WPR-YYYY-WNN"
    },
    "week_number": { "type": "integer", "minimum": 1, "maximum": 52 },
    "date_range": {
      "type": "object",
      "properties": {
        "start": { "type": "string", "format": "date" },
        "end": { "type": "string", "format": "date" }
      }
    },
    "workstreams": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "status", "tasks_planned", "tasks_completed", "tasks_blocked", "completion_pct"],
        "properties": {
          "id": { "type": "string", "pattern": "^WS-[1-8]$" },
          "name": { "type": "string" },
          "status": { "enum": ["on_track", "at_risk", "blocked", "completed", "not_started"] },
          "tasks_planned": { "type": "integer" },
          "tasks_completed": { "type": "integer" },
          "tasks_blocked": { "type": "integer" },
          "completion_pct": { "type": "number", "minimum": 0, "maximum": 100 },
          "key_deliverables_this_week": { "type": "array", "items": { "type": "string" } },
          "risks": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "velocity": {
      "type": "object",
      "properties": {
        "story_points_planned": { "type": "integer" },
        "story_points_completed": { "type": "integer" },
        "velocity_trend": { "enum": ["increasing", "stable", "decreasing"] },
        "burndown_deviation_pct": { "type": "number" }
      }
    },
    "tech_debt": {
      "type": "object",
      "properties": {
        "new_debt_items": { "type": "integer" },
        "resolved_debt_items": { "type": "integer" },
        "total_outstanding": { "type": "integer" },
        "debt_ratio": {
          "type": "number",
          "description": "tech_debt_points / total_points_delivered (target < 0.15)"
        },
        "top_debt_items": {
          "type": "array",
          "maxItems": 5,
          "items": {
            "type": "object",
            "properties": {
              "description": { "type": "string" },
              "severity": { "enum": ["critical", "high", "medium", "low"] },
              "age_weeks": { "type": "integer" }
            }
          }
        }
      }
    },
    "quality_metrics": {
      "type": "object",
      "properties": {
        "tests_total": { "type": "integer" },
        "tests_passing": { "type": "integer" },
        "test_coverage_pct": { "type": "number" },
        "accessibility_score": { "type": "number", "minimum": 0, "maximum": 100 },
        "sentry_unresolved_errors": { "type": "integer" },
        "ci_pipeline_status": { "enum": ["green", "red", "flaky"] }
      }
    },
    "crs_health": {
      "type": "object",
      "description": "CRS = (Uptime * 0.35) + (AI Accuracy * 0.30) + (HFI * 0.20) + (Integration Stability * 0.15)",
      "properties": {
        "uptime_pct": { "type": "number" },
        "ai_accuracy_pct": { "type": "number" },
        "human_feedback_index": { "type": "number" },
        "integration_stability_pct": { "type": "number" },
        "crs_composite": { "type": "number" },
        "crs_target": { "type": "number" },
        "crs_status": { "enum": ["above_target", "at_target", "below_target", "critical"] }
      }
    },
    "blockers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "blocked_workstreams": { "type": "array", "items": { "type": "string" } },
          "owner": { "type": "string" },
          "resolution_eta": { "type": "string", "format": "date" },
          "status": { "enum": ["new", "in_progress", "resolved", "escalated"] }
        }
      }
    },
    "decisions_needed": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "decision": { "type": "string" },
          "options": { "type": "array", "items": { "type": "string" } },
          "deadline": { "type": "string", "format": "date" },
          "decision_maker": { "type": "string" },
          "impact_if_delayed": { "type": "string" }
        }
      }
    },
    "deployment_status": {
      "type": "object",
      "properties": {
        "current_wave": { "type": "string" },
        "traffic_pct": { "type": "object" },
        "rollback_events": { "type": "integer" },
        "next_milestone": { "type": "string" }
      }
    }
  }
}
```

### Example Week 1 Report

```json
{
  "report_id": "MEDMATCH-WPR-2026-W13",
  "week_number": 13,
  "date_range": { "start": "2026-03-23", "end": "2026-03-29" },
  "workstreams": [
    {
      "id": "WS-1",
      "name": "WCAG 2.2 Accessibility",
      "status": "at_risk",
      "tasks_planned": 4,
      "tasks_completed": 2,
      "tasks_blocked": 0,
      "completion_pct": 22,
      "key_deliverables_this_week": ["WS1-01 aria-labels", "WS1-02 keyboard nav"],
      "risks": ["324 files to modify; may need 2 sprints"]
    },
    {
      "id": "WS-2",
      "name": "CI/CD Pipeline",
      "status": "on_track",
      "tasks_planned": 3,
      "tasks_completed": 3,
      "tasks_blocked": 0,
      "completion_pct": 100,
      "key_deliverables_this_week": ["WS2-01 dep fix", "WS2-03 CI green", "WS2-04 pip audit"],
      "risks": []
    }
  ],
  "velocity": {
    "story_points_planned": 34,
    "story_points_completed": 28,
    "velocity_trend": "stable",
    "burndown_deviation_pct": -17.6
  },
  "tech_debt": {
    "new_debt_items": 0,
    "resolved_debt_items": 2,
    "total_outstanding": 19,
    "debt_ratio": 0.12,
    "top_debt_items": [
      { "description": "424 broad except Exception catches", "severity": "high", "age_weeks": 8 },
      { "description": "MeetingRoom.jsx 2,195 LOC god file", "severity": "critical", "age_weeks": 12 },
      { "description": "46 datetime.utcnow() deprecated calls", "severity": "medium", "age_weeks": 6 }
    ]
  },
  "quality_metrics": {
    "tests_total": 209,
    "tests_passing": 209,
    "test_coverage_pct": 5.2,
    "accessibility_score": 35,
    "sentry_unresolved_errors": 0,
    "ci_pipeline_status": "green"
  },
  "blockers": [
    {
      "id": "BLK-001",
      "description": "CISO not yet scheduled for G5 review",
      "blocked_workstreams": ["WS-3", "WS-5"],
      "owner": "Security Lead",
      "resolution_eta": "2026-04-05",
      "status": "in_progress"
    }
  ],
  "decisions_needed": [
    {
      "decision": "LiveKit SFU: Option A (defer) vs Option B (integrate before Wave 1)",
      "options": ["A: Launch with 4-person cap, defer SFU to Wave 2", "B: Integrate LiveKit, delay Wave 1 by 3-6 weeks"],
      "deadline": "2026-03-26",
      "decision_maker": "CTO / Product Lead",
      "impact_if_delayed": "Wave 1 timeline uncertain; enterprise demo capability limited"
    }
  ],
  "deployment_status": {
    "current_wave": "Pre-Wave 1",
    "traffic_pct": { "ios": 0, "android": 0, "web": 100 },
    "rollback_events": 0,
    "next_milestone": "iOS TestFlight internal build (Week 2)"
  }
}
```

---

## Appendix A: DRY Compliance Checklist

| Principle | Current Violation | Resolution | Workstream |
|-----------|------------------|------------|------------|
| No duplicate route logic | `push.py` (324 LOC) + `push_notifications.py` (318 LOC) + `webpush.py` (677 LOC) = 3 files for push | Consolidate into single `notifications/push.py` service | WS-6 |
| No duplicate DB access patterns | Raw `db.collection.find()` in 131 route files | Extract to repository pattern (`repos/users.py`, `repos/jobs.py`, etc.) | WS-6 |
| No duplicate error handling | 424 `except Exception` blocks with similar patterns | Create `utils/error_handler.py` decorator | WS-6 |
| No duplicate auth checks | `get_current_user` duplicated in route files | Already uses FastAPI `Depends()` — verify 100% adoption | WS-6 |
| Single source of truth for config | Env vars read in multiple places | Already centralized in `.env` — verify no hardcoded values | WS-2 |

## Appendix B: Zero-Trust Security Checklist

| Control | Status | Gap | Workstream |
|---------|--------|-----|------------|
| All API endpoints require authentication | Partial (health check exempt) | Verify no unprotected data endpoints | WS-3 |
| JWT tokens have expiry | Yes | Verify refresh token rotation | WS-3 |
| Rate limiting on all public endpoints | Yes (global limiter) | Verify per-endpoint limits appropriate | WS-3 |
| Input validation on all endpoints | Yes (Pydantic models) | Verify 100% coverage | WS-3 |
| CORS restricted to known origins | Configurable | Verify production CORS is not `*` | WS-3 |
| Secrets never in code | Yes (env vars) | Verify via `git log --all -S "password"` | WS-3 |
| E2EE for messenger | Yes | Verify server-side key access = impossible | WS-3 |
| Webhook signatures verified | Yes (Stripe) | Verify PayPal + all others | WS-3 |
| Admin actions audit-logged | Yes (admin_audit.py) | Verify completeness | WS-3 |
| Dependency CVE scanning | Not in CI | Add `pip audit` step (WS2-04) | WS-2 |

---

*End of Autonomous Project Architect Execution Framework — MEDMATCH_22/03/2026*
