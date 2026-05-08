# AI Suite — Cadence Deliverables Implementation Roadmap
## RICE-Scored | Priority-Ranked | Status-Tracked
### Source: Developer Summary (March 22, 2026) + Platform Deployment Readiness Strategy

---

## Status Legend

| Indicator | Meaning | Action Required |
|-----------|---------|-----------------|
| :red_circle: **RED** | Blocked / Critical Risk / Not Started (overdue) | Immediate escalation; resource reallocation |
| :orange_circle: **ORANGE** | At Risk / In Progress with concerns | Monitor closely; mitigate this sprint |
| :green_circle: **GREEN** | On Track / Completed / No issues | Continue cadence |

---

## RICE Scoring Methodology

```
RICE Score = (Reach x Impact x Confidence) / Effort

Reach:       Users/stakeholders impacted (1-100 scale, normalized)
Impact:      Value delivered (1-5: Minimal, Low, Medium, High, Massive)
Confidence:  Data certainty (0.5-1.0)
Effort:      Person-weeks required
```

---

## 1. Master RICE Priority Table — All Deliverables

### Tier 0: Pre-Launch Blockers (Must complete before ANY Wave 1 launch)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 1 | BLK-01 | **CI/CD Pipeline Verification** — Confirm 204 tests green in GitHub Actions | 100 | 5 | 0.95 | 0.5 | **950.0** | :orange_circle: ORANGE | DevOps | TODAY |
| 2 | BLK-02 | **WCAG 2.2 Accessibility Remediation** — Score from 25 → 90+ / 100 | 100 | 5 | 0.90 | 4.0 | **112.5** | :red_circle: RED | Frontend | Week 2 |
| 3 | BLK-03 | **G5 CISO Security Sign-Off** — Evidence pack + review + approval | 100 | 5 | 0.70 | 6.0 | **58.3** | :red_circle: RED | Security | Week 4 |
| 4 | BLK-04 | **SFU Architecture Decision** — LiveKit evaluation spike + Option A/B | 80 | 5 | 0.80 | 0.5 | **640.0** | :red_circle: RED | Architect | This Week |

### Tier 1: Wave 1 Prerequisites (Month 1)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 5 | W1-01 | **iOS TestFlight Internal Build** — 14-day minimum run | 70 | 4 | 0.85 | 1.5 | **159.3** | :red_circle: RED | Mobile | Week 2 |
| 6 | W1-02 | **Android Internal Testing Track** — Data Safety form + API 34+ | 75 | 4 | 0.85 | 1.5 | **170.0** | :red_circle: RED | Mobile | Week 2 |
| 7 | W1-03 | **Web/PWA Canary Deployment** — 5% traffic + monitoring | 60 | 4 | 0.90 | 1.0 | **216.0** | :orange_circle: ORANGE | DevOps | Week 2 |
| 8 | W1-04 | **App Privacy Nutrition Label (iOS)** | 70 | 3 | 0.95 | 0.5 | **399.0** | :red_circle: RED | Legal | Week 1 |
| 9 | W1-05 | **Export Compliance Documentation (iOS)** | 70 | 3 | 0.90 | 0.5 | **378.0** | :red_circle: RED | Legal | Week 1 |
| 10 | W1-06 | **Google Play Data Safety Form** | 75 | 3 | 0.95 | 0.5 | **427.5** | :red_circle: RED | Legal | Week 1 |
| 11 | W1-07 | **Wave 1 Traffic Ramp Plan Execution** — iOS 1%→100%, Android 10%→100%, Web 5%→100% | 100 | 5 | 0.80 | 2.0 | **200.0** | :red_circle: RED | Release | Week 3-4 |
| 12 | W1-08 | **CRS Monitoring Baseline** — Establish per-portal CRS baselines | 50 | 4 | 0.70 | 1.0 | **140.0** | :red_circle: RED | DevOps | Week 2 |

### Tier 2: Security Evidence Pack (Week 1-4)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 13 | SEC-01 | **STRIDE Threat Model** — All 6 categories x 3 portals | 100 | 4 | 0.80 | 1.5 | **213.3** | :red_circle: RED | Security | Week 1 |
| 14 | SEC-02 | **Data Flow Diagrams** — Auth, E2EE, payments, AI inference, bridge flows | 100 | 4 | 0.85 | 1.0 | **340.0** | :red_circle: RED | Security | Week 1 |
| 15 | SEC-03 | **SAST Results (Backend)** — Bandit scan: 0 high-severity | 100 | 4 | 0.90 | 0.5 | **720.0** | :red_circle: RED | DevOps | Week 2 |
| 16 | SEC-04 | **SAST Results (Frontend)** — ESLint security: 0 errors | 100 | 4 | 0.90 | 0.5 | **720.0** | :red_circle: RED | DevOps | Week 2 |
| 17 | SEC-05 | **DAST Results** — OWASP ZAP against staging: 0 high-risk | 100 | 5 | 0.75 | 1.0 | **375.0** | :red_circle: RED | Security | Week 2 |
| 18 | SEC-06 | **Penetration Test Report** — External firm engagement | 100 | 5 | 0.60 | 3.0 | **100.0** | :red_circle: RED | Security | Week 3 |
| 19 | SEC-07 | **Incident Response Plan** — Detection → recovery → post-mortem | 100 | 4 | 0.80 | 1.0 | **320.0** | :red_circle: RED | Security | Week 2 |
| 20 | SEC-08 | **Encryption Documentation** — TLS, E2EE protocol, JWT, at-rest | 100 | 4 | 0.85 | 1.0 | **340.0** | :red_circle: RED | Security | Week 2 |

### Tier 3: WCAG 2.2 Remediation Breakdown (Week 1-3)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 21 | ACC-01 | **aria-label + aria-describedby + role** — All 324 frontend files | 100 | 5 | 0.90 | 2.0 | **225.0** | :red_circle: RED | Frontend | Week 1 |
| 22 | ACC-02 | **Keyboard navigation** — tabIndex + focus traps + skip-nav | 100 | 5 | 0.85 | 1.5 | **283.3** | :red_circle: RED | Frontend | Week 1 |
| 23 | ACC-03 | **Screen reader validation** — VoiceOver, TalkBack, NVDA/JAWS on 5 flows | 80 | 4 | 0.70 | 1.5 | **149.3** | :red_circle: RED | QA | Week 2 |
| 24 | ACC-04 | **Color contrast** — WCAG 4.5:1 AA on all text + AI content areas | 100 | 4 | 0.90 | 1.0 | **360.0** | :red_circle: RED | Frontend | Week 2 |
| 25 | ACC-05 | **Automated accessibility test suite** — ACC-01 to ACC-05 in CI | 100 | 4 | 0.85 | 1.0 | **340.0** | :red_circle: RED | QA | Week 2 |

### Tier 4: LiveKit SFU Integration (If Option B chosen — Week 1-6)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 26 | SFU-01 | **LiveKit Evaluation Spike** — Self-host vs cloud, cost, SDK, latency | 80 | 5 | 0.80 | 0.5 | **640.0** | :red_circle: RED | Backend | Day 1-3 |
| 27 | SFU-02 | **Architecture Decision Record** — ADR-001-SFU (Option A vs B) | 80 | 5 | 0.90 | 0.2 | **1800.0** | :red_circle: RED | Architect | Day 3 |
| 28 | SFU-03 | **LiveKit Server Deployment** — Docker/K8s + TURN/STUN | 60 | 4 | 0.75 | 1.5 | **120.0** | :red_circle: RED | DevOps | Week 2 |
| 29 | SFU-04 | **Backend SFU Integration** — Room API, token gen, events | 60 | 5 | 0.70 | 2.0 | **105.0** | :red_circle: RED | Backend | Week 3 |
| 30 | SFU-05 | **Frontend SFU Integration** — Video/audio via SFU, 20+ participants | 60 | 5 | 0.65 | 3.0 | **65.0** | :red_circle: RED | Frontend | Week 4 |
| 31 | SFU-06 | **Compatibility Layer** — P2P + SFU via same hook; feature flag toggle | 60 | 3 | 0.80 | 1.0 | **144.0** | :red_circle: RED | Frontend | Week 5 |
| 32 | SFU-07 | **Load Test** — 50 concurrent, p95 < 200ms, 720p stable | 60 | 4 | 0.70 | 1.0 | **168.0** | :red_circle: RED | QA | Week 5 |
| 33 | SFU-08 | **Recording via SFU** — Server-side recording + Director Cuts replay | 40 | 3 | 0.65 | 1.5 | **52.0** | :red_circle: RED | Backend | Week 6 |

### Tier 5: Wave 2-4 Deployments (Month 2-4)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 34 | W2-01 | **Windows MSIX Package** — EV code-sign + WACK pass + Store listing | 30 | 3 | 0.80 | 2.0 | **36.0** | :red_circle: RED | Desktop | Month 2 |
| 35 | W2-02 | **macOS Universal Binary** — arm64+x86_64, notarised, sandbox + hardened | 25 | 3 | 0.75 | 2.0 | **28.1** | :red_circle: RED | Desktop | Month 2 |
| 36 | W3-01 | **Linux Packages** — .deb/.rpm (GPG), Flatpak, AppImage + Flathub | 15 | 2 | 0.70 | 2.0 | **10.5** | :red_circle: RED | Desktop | Month 3 |
| 37 | W3-02 | **Chrome Extension** — Manifest V3, Chrome Web Store + Edge Add-ons | 20 | 3 | 0.75 | 2.0 | **22.5** | :red_circle: RED | Frontend | Month 3 |
| 38 | W4-01 | **Microsoft 365 Certification** — Publisher Attestation + security review | 40 | 4 | 0.50 | 8.0 | **10.0** | :orange_circle: ORANGE | Security | Month 3-4 |
| 39 | W4-02 | **Enterprise API GA** — OpenAPI 3.1 spec + developer portal + sandbox | 30 | 4 | 0.70 | 3.0 | **28.0** | :red_circle: RED | Backend | Month 3-4 |

### Tier 6: Architecture Modernization (Week 5-12)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 40 | MOD-01 | **Sentry APM Integration** — Frontend + backend error tracking | 100 | 4 | 0.90 | 0.5 | **720.0** | :red_circle: RED | DevOps | Week 5 |
| 41 | MOD-02 | **God File Decomposition** — lumi_messenger.py (2,466→5 files <500 LOC) | 30 | 3 | 0.85 | 2.0 | **38.3** | :red_circle: RED | Backend | Week 5-6 |
| 42 | MOD-03 | **datetime.utcnow() Cleanup** — 46 instances → datetime.now(timezone.utc) | 100 | 2 | 0.95 | 0.3 | **633.3** | :red_circle: RED | Backend | Week 5 |
| 43 | MOD-04 | **Zustand State Management** — Top-20 useState chains migrated | 80 | 4 | 0.75 | 3.0 | **80.0** | :red_circle: RED | Frontend | Week 6-8 |
| 44 | MOD-05 | **Exception Handling Tightening** — 424 broad catches → specific | 50 | 3 | 0.80 | 2.0 | **60.0** | :red_circle: RED | Backend | Week 6-8 |
| 45 | MOD-06 | **CRA → Vite Migration** — Dev start <3s, HMR <100ms | 30 | 3 | 0.70 | 2.0 | **31.5** | :red_circle: RED | Frontend | Week 8-9 |
| 46 | MOD-07 | **Redis Caching Layer** — Session cache + rate limit state | 80 | 4 | 0.80 | 1.5 | **170.7** | :red_circle: RED | Backend | Week 7 |
| 47 | MOD-08 | **Vector Search** — Atlas Vector Search for semantic job matching | 60 | 4 | 0.65 | 3.0 | **52.0** | :red_circle: RED | Backend | Week 9-10 |
| 48 | MOD-09 | **OpenTelemetry Distributed Tracing** | 40 | 3 | 0.70 | 2.0 | **42.0** | :red_circle: RED | DevOps | Week 10 |
| 49 | MOD-10 | **Test Coverage Expansion** — 4.4% → 25%+ (20 new test files) | 100 | 4 | 0.80 | 6.0 | **53.3** | :red_circle: RED | QA | Week 5-12 |

### Tier 7: Integration Bridge Hardening (Week 2-4)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 50 | BRG-01 | **Bridge Contract Tests** — Schedule push, video→meeting, post-sync | 80 | 5 | 0.85 | 1.0 | **340.0** | :red_circle: RED | QA | Week 2 |
| 51 | BRG-02 | **Graceful Degradation** — ENZI works when KARAU is down | 80 | 4 | 0.80 | 1.0 | **256.0** | :red_circle: RED | Backend | Week 3 |
| 52 | BRG-03 | **Bridge Monitoring Dashboard** — Queue depth, sync latency, failure rate | 40 | 3 | 0.70 | 1.5 | **56.0** | :red_circle: RED | DevOps | Week 4 |
| 53 | BRG-04 | **Integration Regression Suite** — Full regression on bridge file PRs | 80 | 4 | 0.85 | 1.0 | **272.0** | :red_circle: RED | QA | Week 3 |

### Tier 8: AI Innovation Layer (Week 13-24)

| Rank | ID | Deliverable | Reach | Impact | Confidence | Effort (pw) | RICE Score | Status | Owner | Deadline |
|------|----|-------------|-------|--------|-----------|-------------|-----------|--------|-------|----------|
| 54 | AI-01 | **Agentic Job Application Agent** — Auto-find, match, apply with approval gate | 70 | 5 | 0.60 | 6.0 | **35.0** | :red_circle: RED | AI/ML | Week 13-16 |
| 55 | AI-02 | **RAG Pipeline (Cross-Portal)** — "Ask anything" with vector embeddings | 80 | 5 | 0.55 | 5.0 | **44.0** | :red_circle: RED | AI/ML | Week 14-17 |
| 56 | AI-03 | **Meeting Scheduling Agent** — Calendar-aware auto-propose | 60 | 4 | 0.60 | 3.0 | **48.0** | :red_circle: RED | AI/ML | Week 16-18 |
| 57 | AI-04 | **Predictive Caching** — ML-based pre-fetch; cache hit >40% | 80 | 3 | 0.50 | 3.0 | **40.0** | :red_circle: RED | AI/ML | Week 18-20 |
| 58 | AI-05 | **Developer API Marketplace** — Third-party bot OAuth + webhooks + SDK | 50 | 5 | 0.50 | 8.0 | **15.6** | :red_circle: RED | Backend | Week 18-24 |
| 59 | AI-06 | **Healthcare Vertical** — HIPAA module + medical credential verification | 40 | 5 | 0.45 | 6.0 | **15.0** | :red_circle: RED | Backend | Week 20-24 |

---

## 2. RICE Score Rankings — Top 20 by Priority

| Rank | RICE Score | ID | Deliverable | Status | Sprint |
|------|-----------|-----|-------------|--------|--------|
| 1 | **1800.0** | SFU-02 | Architecture Decision Record (Option A/B) | :red_circle: RED | Sprint 1 |
| 2 | **950.0** | BLK-01 | CI/CD Pipeline Verification | :orange_circle: ORANGE | Sprint 1 |
| 3 | **720.0** | SEC-03 | SAST Backend (Bandit) | :red_circle: RED | Sprint 2 |
| 4 | **720.0** | SEC-04 | SAST Frontend (ESLint) | :red_circle: RED | Sprint 2 |
| 5 | **720.0** | MOD-01 | Sentry APM Integration | :red_circle: RED | Sprint 5 |
| 6 | **640.0** | BLK-04 | SFU Architecture Decision | :red_circle: RED | Sprint 1 |
| 7 | **640.0** | SFU-01 | LiveKit Evaluation Spike | :red_circle: RED | Sprint 1 |
| 8 | **633.3** | MOD-02 | datetime.utcnow() Cleanup | :red_circle: RED | Sprint 5 |
| 9 | **427.5** | W1-06 | Google Play Data Safety Form | :red_circle: RED | Sprint 1 |
| 10 | **399.0** | W1-04 | App Privacy Nutrition Label (iOS) | :red_circle: RED | Sprint 1 |
| 11 | **378.0** | W1-05 | Export Compliance (iOS) | :red_circle: RED | Sprint 1 |
| 12 | **375.0** | SEC-05 | DAST Scan (OWASP ZAP) | :red_circle: RED | Sprint 2 |
| 13 | **360.0** | ACC-04 | Color Contrast Remediation | :red_circle: RED | Sprint 2 |
| 14 | **340.0** | SEC-02 | Data Flow Diagrams | :red_circle: RED | Sprint 1 |
| 15 | **340.0** | SEC-08 | Encryption Documentation | :red_circle: RED | Sprint 2 |
| 16 | **340.0** | ACC-05 | Automated Accessibility Tests in CI | :red_circle: RED | Sprint 2 |
| 17 | **340.0** | BRG-01 | Bridge Contract Tests | :red_circle: RED | Sprint 2 |
| 18 | **320.0** | SEC-07 | Incident Response Plan | :red_circle: RED | Sprint 2 |
| 19 | **283.3** | ACC-02 | Keyboard Navigation + Skip-Nav | :red_circle: RED | Sprint 1 |
| 20 | **272.0** | BRG-04 | Integration Regression Suite | :red_circle: RED | Sprint 3 |

---

## 3. Sprint Cadence — 12-Week Execution Plan

### Sprint 1 (Week 1) — "Ground Zero"

**Theme:** Unblock everything. No new features.

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| BLK-01 | CI/CD Pipeline Green | 950 | :orange_circle: ORANGE | 204 tests pass in GitHub Actions |
| SFU-02 | ADR-001-SFU Decision | 1800 | :red_circle: RED | Signed document: Option A or B |
| SFU-01 | LiveKit Evaluation Spike | 640 | :red_circle: RED | Evaluation doc with cost + latency data |
| BLK-04 | SFU Architecture Decision | 640 | :red_circle: RED | CTO sign-off on direction |
| W1-04 | iOS Privacy Nutrition Label | 399 | :red_circle: RED | Label submitted to App Store Connect |
| W1-05 | iOS Export Compliance | 378 | :red_circle: RED | Documentation submitted |
| W1-06 | Google Play Data Safety | 428 | :red_circle: RED | Form submitted to Play Console |
| ACC-01 | aria-label + role injection | 225 | :red_circle: RED | grep count >= 800 (from 14) |
| ACC-02 | Keyboard navigation | 283 | :red_circle: RED | Tab through login → dashboard → job search |
| SEC-01 | STRIDE Threat Model | 213 | :red_circle: RED | Document covers all 3 portals |
| SEC-02 | Data Flow Diagrams | 340 | :red_circle: RED | 5 core flows diagrammed |

**Sprint 1 Velocity Target:** 13 story points  
**Sprint 1 Risk Level:** :red_circle: HIGH — All items are net-new, no runway

---

### Sprint 2 (Week 2) — "Evidence & Accessibility"

**Theme:** Security evidence + WCAG completion + store submissions

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| SEC-03 | SAST Backend (Bandit) | 720 | :red_circle: RED | 0 high-severity findings |
| SEC-04 | SAST Frontend (ESLint) | 720 | :red_circle: RED | 0 error-level findings |
| SEC-05 | DAST Scan (ZAP) | 375 | :red_circle: RED | 0 high-risk alerts |
| SEC-07 | Incident Response Plan | 320 | :red_circle: RED | Reviewed by ops lead |
| SEC-08 | Encryption Documentation | 340 | :red_circle: RED | E2EE + TLS + JWT documented |
| ACC-03 | Screen Reader Validation | 149 | :red_circle: RED | 5 flows tested on 3 readers |
| ACC-04 | Color Contrast | 360 | :red_circle: RED | axe-core: 0 contrast violations |
| ACC-05 | Accessibility Tests in CI | 340 | :red_circle: RED | ACC-01 to ACC-05 pass in pipeline |
| W1-01 | iOS TestFlight Build | 159 | :red_circle: RED | Build accepted, internal testers installing |
| W1-02 | Android Internal Track | 170 | :red_circle: RED | Build accepted, testers installing |
| W1-03 | Web/PWA Canary (5%) | 216 | :orange_circle: ORANGE | Canary deployed, monitoring active |
| BRG-01 | Bridge Contract Tests | 340 | :red_circle: RED | All bridge tests pass |
| W1-08 | CRS Monitoring Baseline | 140 | :red_circle: RED | Baseline values recorded per portal |

**Sprint 2 Velocity Target:** 18 story points  
**Sprint 2 Risk Level:** :red_circle: HIGH — External dependencies (pen test firm, Apple review)

---

### Sprint 3 (Week 3) — "Enterprise Prep & Bridge"

**Theme:** Enterprise pilot readiness + bridge hardening

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| SEC-06 | Penetration Test Report | 100 | :red_circle: RED | External firm engaged; report delivered |
| BLK-02 | WCAG Score >= 75 | 113 | :red_circle: RED | axe-core scan: <=5 non-critical issues |
| BRG-02 | Graceful Degradation | 256 | :red_circle: RED | ENZI works when KARAU mocked as down |
| BRG-04 | Integration Regression Suite | 272 | :red_circle: RED | Runs in CI on bridge file PRs |
| SFU-03* | LiveKit Server Deployment | 120 | :red_circle: RED | Health endpoint responding (*if Option B) |
| SFU-04* | Backend SFU Integration | 105 | :red_circle: RED | Room creation + token gen works |
| W4-01 | M365 Certification (start) | 10 | :orange_circle: ORANGE | Publisher Attestation submitted |

**Sprint 3 Velocity Target:** 14 story points  
**Sprint 3 Risk Level:** :orange_circle: MEDIUM — Pen test timeline is external dependency

---

### Sprint 4 (Week 4) — "G5 Gate & Wave 1 Launch"

**Theme:** Security sign-off + Wave 1 GA

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| SEC-09 | G5 Evidence Pack Assembly | — | :red_circle: RED | All 8 artifacts compiled + executive summary |
| BLK-03 | G5 CISO Sign-Off | 58 | :red_circle: RED | Signed approval; gate = PASSED |
| BRG-03 | Bridge Monitoring Dashboard | 56 | :red_circle: RED | Real-time metrics visible |
| W1-07 | Wave 1 Traffic Ramp | 200 | :red_circle: RED | iOS/Android/Web at GA (100%) |
| SFU-05* | Frontend SFU Integration | 65 | :red_circle: RED | 20+ participants tested |

**Sprint 4 Velocity Target:** 10 story points  
**Sprint 4 Risk Level:** :red_circle: HIGH — G5 is binary gate; launch depends on it

---

### Sprint 5-6 (Week 5-6) — "Stabilize & Modernize"

**Theme:** Post-launch stabilization + architecture improvements

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| MOD-01 | Sentry APM Integration | 720 | :red_circle: RED | Errors visible in Sentry dashboard |
| MOD-02 | datetime.utcnow() Cleanup | 633 | :red_circle: RED | grep count = 0 |
| MOD-03 | God File Decomposition | 38 | :red_circle: RED | lumi_messenger.py → 5 files, all tests pass |
| MOD-10 | Test Coverage Phase 1 | 53 | :red_circle: RED | 10 new test files; coverage 4.4% → 15% |
| SFU-06* | P2P/SFU Compatibility Layer | 144 | :red_circle: RED | Feature flag toggles mode |
| SFU-07* | SFU Load Test | 168 | :red_circle: RED | 50 concurrent OK |

**Sprint 5-6 Velocity Target:** 16 story points  

---

### Sprint 7-8 (Week 7-8) — "Scale Layer"

**Theme:** Caching + state management + exception hardening

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| MOD-07 | Redis Caching Layer | 171 | :red_circle: RED | Cache hit rate > 60% on hot paths |
| MOD-04 | Zustand Migration (Phase 1) | 80 | :red_circle: RED | Top-10 components migrated |
| MOD-05 | Exception Handling Phase 1 | 60 | :red_circle: RED | Broad catches reduced to < 200 |
| W2-01 | Windows MSIX Package | 36 | :red_circle: RED | Store certified |
| W2-02 | macOS Universal Binary | 28 | :red_circle: RED | Notarised + Store listed |

**Sprint 7-8 Velocity Target:** 14 story points  

---

### Sprint 9-10 (Week 9-10) — "Intelligence Layer"

**Theme:** Search + tracing + Vite migration

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| MOD-06 | CRA → Vite Migration | 32 | :red_circle: RED | Dev start < 3s; all files build |
| MOD-08 | Vector Search | 52 | :red_circle: RED | Semantic job search < 200ms |
| MOD-09 | OpenTelemetry Tracing | 42 | :red_circle: RED | Top-10 slow endpoints identified |
| MOD-04 | Zustand Migration (Phase 2) | — | :red_circle: RED | Top-20 components migrated |

**Sprint 9-10 Velocity Target:** 12 story points  

---

### Sprint 11-12 (Week 11-12) — "Platform Expansion"

**Theme:** Wave 3 platforms + test coverage push

| ID | Deliverable | RICE | Status | Exit Criteria |
|----|-------------|------|--------|---------------|
| W3-01 | Linux Packages | 11 | :red_circle: RED | Flathub review approved |
| W3-02 | Chrome Extension | 23 | :red_circle: RED | Chrome Web Store listed |
| MOD-10 | Test Coverage Phase 2 | — | :red_circle: RED | Coverage 15% → 25% |
| MOD-05 | Exception Handling Phase 2 | — | :red_circle: RED | Broad catches < 50 |

**Sprint 11-12 Velocity Target:** 10 story points  

---

## 4. CRS Health Tracking (Per-Portal SLA Dashboard)

### Year 1 Targets vs Baselines

| Portal | CRS Y1 Target | Uptime SLA | Key AI Metric | Baseline | Status |
|--------|---------------|-----------|---------------|----------|--------|
| MedMatch AI | 85% | 99.95% | Inference < 2s P95 | TBD post-launch | :red_circle: RED (not measured) |
| AI KARAU | 84% | 99.90% | Video latency < 150ms | TBD post-launch | :red_circle: RED (not measured) |
| ENZI | 88% | 99.99% | Msg delivery < 500ms P99 | TBD post-launch | :red_circle: RED (not measured) |
| Integration Bridge | 78% | 99.95% | Bridge sync < 1s | TBD post-launch | :red_circle: RED (not measured) |

### CRS Formula
```
CRS = (Uptime x 0.35) + (AI Accuracy x 0.30) + (Human Feedback Index x 0.20) + (Integration Stability x 0.15)
```

### Rollback Triggers
| Trigger | Threshold | Action |
|---------|-----------|--------|
| Crash-free rate | < 99.0% (7-day rolling) | Pause rollout; investigate |
| CRS degradation | > 5% below target sustained 30+ min | Auto-rollback; incident declared |
| Encryption error | Non-zero in 15-min window | **Immediate P0 declaration** |

---

## 5. AI Governance Cadence (Post-Launch)

| AI Change Type | Mechanism | Human Gate? | Rollback Speed | Cadence |
|----------------|-----------|-------------|----------------|---------|
| Job-skill matching model | Server-side auto-promote if accuracy delta < 2% on 7-day roll | No | < 5 min | Weekly |
| Meeting transcription (WER) | Server-side auto-promote if WER degradation < 1.5% | No | < 5 min | Weekly |
| Accreditation taxonomy sync | Auto on industry API change event | No | < 5 min | Event-driven |
| AI scheduling acceptance rate | Auto if acceptance rate decline < 8% | No | < 5 min | Daily |
| Encryption algorithm change | CISO + CTO mandatory sign-off | **YES** | App update required | As needed |
| Post-quantum migration | CISO + Legal + CTO mandatory | **YES** | 90-day enterprise runway | As needed |
| Regulatory compliance model | Legal + Compliance Officer | **YES** | 30-day enterprise notice | Quarterly |
| AI bias detected | Emergency retrain; diversity audit | **YES** | Server-side revert; < 24hr notification | Immediate |

---

## 6. Cadence Summary — 16-Week Overview

```
WEEK  1  ██████████████████████████████████  Sprint 1: GROUND ZERO
         CI/CD ✓ | SFU Decision | WCAG Start | STRIDE | Store Forms

WEEK  2  ██████████████████████████████████  Sprint 2: EVIDENCE & A11Y
         SAST/DAST | WCAG Complete | TestFlight | Android Track | Bridge Tests

WEEK  3  ██████████████████████████████████  Sprint 3: ENTERPRISE PREP
         Pen Test | Bridge Hardening | SFU Backend | M365 Start

WEEK  4  ██████████████████████████████████  Sprint 4: G5 GATE & LAUNCH
         CISO Sign-Off | Wave 1 GA | SFU Frontend

WEEK  5  ████████████████████████            Sprint 5-6: STABILIZE
WEEK  6  ████████████████████████            Sentry | God Files | utcnow | Tests

WEEK  7  ████████████████████████            Sprint 7-8: SCALE
WEEK  8  ████████████████████████            Redis | Zustand | Exceptions | Wave 2

WEEK  9  ████████████████████████            Sprint 9-10: INTELLIGENCE
WEEK 10  ████████████████████████            Vite | Vector Search | OTEL

WEEK 11  ████████████████████████            Sprint 11-12: EXPANSION
WEEK 12  ████████████████████████            Linux | Chrome Ext | Test Coverage

WEEK 13  ░░░░░░░░░░░░░░░░░░░░░░░░          Sprint 13+: AI INNOVATION
WEEK 14  ░░░░░░░░░░░░░░░░░░░░░░░░          Agentic AI | RAG | API Marketplace
WEEK 15  ░░░░░░░░░░░░░░░░░░░░░░░░          
WEEK 16  ░░░░░░░░░░░░░░░░░░░░░░░░          Wave 4: M365 + Enterprise API

█ = Active development    ░ = Innovation/backlog
```

### Current Overall Program Status

| Dimension | Status | Score | Key Issue |
|-----------|--------|-------|-----------|
| **Wave 1 Readiness** | :red_circle: RED | 15% | 4 blockers unresolved |
| **Security Posture** | :red_circle: RED | 30% | G5 evidence pack not started |
| **Accessibility** | :red_circle: RED | 25/100 | 14 aria-labels in 324 files |
| **CI/CD Pipeline** | :orange_circle: ORANGE | 80% | Fix applied, not verified |
| **Video Architecture** | :red_circle: RED | 40% | P2P only; SFU decision pending |
| **Integration Bridge** | :orange_circle: ORANGE | 60% | Works but no contract tests |
| **Test Coverage** | :red_circle: RED | 4.4% | 10 test files / 228 source |
| **CRS Monitoring** | :red_circle: RED | 0% | No baselines established |
| **Architecture Health** | :orange_circle: ORANGE | 55% | God files, no caching, no APM |
| **Feature Completeness** | :green_circle: GREEN | 95% | 204/204 tests pass |

---

*Document: `/app/docs/CADENCE_ROADMAP_22_03_2026.md`*  
*Next Update: End of Sprint 1 (Week 1)*  
*Session: MEDMATCH_22/03/2026*
