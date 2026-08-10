# Gap Assessment Report — State of the Art
## AI KARAU Portal & MedMatch Job Toolkit vs. Top-10 Market Benchmarks
### Original: February 2026 · **Revised & code-verified: 10 August 2026**

> **This revision supersedes the February 2026 assessment.** The original was a
> feature-list benchmark written before a large build-out. This version was
> re-derived by **auditing the actual codebase** (routes, services, and UI
> components), so every verdict below is backed by a file/endpoint reference.
> The prior scores (KARAU 62/100, MedMatch 58/100) are obsolete — most of the
> "critical" gaps have shipped, several previously "missing" items are real, and
> a few previously "present" items turned out to be stubs. See
> [§0 What changed since February 2026](#0-what-changed-since-february-2026).

---

## Executive Summary

Both platforms have moved from "rich feature list with critical AI gaps" to
"broad, AI-complete feature surface with **depth/production-hardening** as the
remaining risk." The dominant gap is no longer *missing features* — it is the
number of features that exist as **UI + LLM-prompt or simulated backend** rather
than production-grade systems.

**Revised readiness (two axes):**

| Platform | Feature breadth | Production depth | Notes |
|----------|-----------------|------------------|-------|
| AI KARAU Video Portal | **~80/100** (was 62) | **~55/100** | Nearly all table-stakes AI meeting features shipped; media transport is still WebRTC **mesh** (no real SFU), meeting-media E2EE and beamforming DSP are simulated. |
| MedMatch Job Toolkit | **~82/100** (was 58) | **~60/100** | Full AI recruiter/candidate suite shipped; matching is LLM+fuzzy (no vector embeddings), several analytics endpoints return hardcoded numbers, no trained hiring-outcome model. |

**The three highest-leverage remaining themes:**
1. **KARAU media scaling** — the real limit is a peer-to-peer mesh; the SFU
   endpoints are hardcoded stubs. This caps webinars at a handful of live
   publishers regardless of the webinar UI. (P0)
2. **"Real vs. simulated" hardening** — meeting-media E2EE, beamforming DSP,
   spatial/SLAM/IoT streams, and several MedMatch analytics endpoints are
   mock/hardcoded. They demo well but aren't production truth. (P1)
3. **Matching intelligence** — MedMatch "semantic matching" is LLM-prompt +
   `difflib` fuzzy, not embeddings; candidate/success scoring is LLM, not a
   trained ranker. Competitive parity with Eightfold/LinkedIn needs a real
   vector/embedding layer. (P1)

---

## 0. What changed since February 2026

### Now IMPLEMENTED (were flagged CRITICAL/HIGH gaps in Feb 2026)

**KARAU**
- Real-time transcription & live captions — `frontend/.../KarauMeet/LiveCaptions.jsx` (Web Speech API), `backend/routes/realtime_stt.py` (`/transcribe`, WS `/stream`), `services/transcription_service.py` + `services/karau_meet/ai_transcription_service.py` (Whisper).
- AI meeting summaries & action items — `routes/meeting_notes.py`, `routes/meeting_intelligence.py`, `routes/karau_collaboration.py` (action-item extract/CRUD), `services/meeting_notes_service.py`.
- Live language translation of captions — `services/karau_meet/translation_service.py`, `routes/karau_extended.py` `/translate`, `routes/karau_webinar.py` `/translate-caption`.
- AI noise cancellation (client-side, **real**) — `KarauMeet/useNoiseCancellation.js` (RNNoise WASM + Web Audio fallback).
- Whiteboard / collaborative canvas — `routes/karau_collaboration.py`, `KarauMeet/EnhancedWhiteboard.jsx`.
- Live polls & Q&A — `routes/karau_polls_challenges.py`, `routes/karau_webinar.py` (`/qa/*`).
- In-meeting reactions/emojis — `KarauMeet/EmojiReactions.jsx`, `routes/karau_gamification.py`.
- Recording auto-transcript + searchable archive + AI chapters/highlights — `routes/karau_recordings.py`, `routes/karau_replay.py` (`/search`, `/generate-chapters`, `/generate-highlights`).
- Sentiment analysis + in-meeting AI copilot — `routes/karau_enhanced_sentiment.py`.
- Webinar view-only mode & host moderation — `routes/karau_webinar.py`, `KarauMeet/WebinarLiveRoom.jsx`.

**MedMatch**
- AI candidate scoring/ranking — `routes/ai_talent.py` `score_candidate` (`/ai-talent/score-candidate`), `CandidateScoringPage.jsx`.
- AI job-description generation — `routes/ai_talent.py` `generate_job_description`, `JobDescriptionGenerator.jsx`.
- Talent CRM + nurture campaigns — `routes/talent_crm.py` (pools, contacts, pipeline, `/campaigns`).
- Interview scorecards — `routes/ai_talent.py` `/scorecards`.
- DEI analytics + blind screening — `routes/dei_analytics.py`, `routes/recruiter_rbac.py` (`/blind-screening/*`).
- One-click / smart apply — `routes/smart_apply.py`, `routes/talent_tools.py` `/one-click-apply`.
- Team collaboration on candidates + recruiter RBAC/audit — `routes/recruiter_rbac.py`, `talent_tools.py` `/collaborate/*`.
- Offer management + approval workflow + letter generation — `routes/advanced_features.py` `/offers*`.
- Hiring funnel / trends analytics (**real, computed**) — `routes/analytics_funnel.py`, `routes/analytics.py`, `routes/production_metrics.py`.
- AI candidate chatbot (Dragon), voice coach, QA/video-interview practice — `routes/ai_features.py`.

### Corrections — prior claims that the code contradicts

| Prior claim (Feb 2026) | Reality in code (Aug 2026) |
|---|---|
| KARAU max ~50 participants | Transport is **P2P mesh** (`routes/karau_webrtc.py`, `services/karau_meet/webrtc_signaling.py`); practical live-publisher limit is a handful. SFU config (`routes/meeting_infrastructure.py` `/sfu/*`) is **hardcoded stub** (`wss://sfu-*.karau.ai`, `active_meetings: 0`). |
| E2EE "Partial (WebRTC SRTP)" | **Real E2EE exists for chat DMs** (`frontend/src/utils/e2ee.js` ECDH-P256 + AES-GCM, key server `routes/e2ee.py`). **Meeting-media E2EE is a stub** (`meeting_infrastructure.py /e2ee/*` returns protocol strings only). |
| MedMatch "semantic skill matching" gap → (implied embeddings) | Matching is **LLM-prompt + `difflib` fuzzy** (`routes/platform_features.py /semantic-match`, `services/search_engine.py`). **No vector embeddings anywhere** (no SentenceTransformer/faiss/pgvector). |
| "Predictive candidate success — On Par (ML Predictor)" | Candidate success is **LLM callback-probability** (`routes/ai_features.py /jobs/predict-callback`). The real ML pipeline (`ml_model_trainer.py`, `ml_issue_predictor.py`) predicts **compliance/data-integrity issues, not hires**. |
| "Job board distribution (multi-post) — Partial" | **Reversed**: the system **ingests** from boards (`services/job_sources.py`, `web_job_crawler.py`); there is **no outbound multi-posting**. |
| Hiring metrics present | `routes/ai_talent.py /hiring-metrics` returns **hardcoded** `avg_time_to_hire_days=14`, `avg_cost_per_hire=4250`, static `source_effectiveness`. Funnel counts are real; these three fields are placeholders. |
| DEI metrics | `routes/dei_analytics.py` computes gender/geographic distribution for real, but index scores (`gender_parity_index=0.85`, `+3%` deltas) are **hardcoded**. |
| Beamforming / spatial / SLAM / IoT | UI + **simulated telemetry** backends (`karau_beamforming.py`, `karau_simulation.py`, `karau_slam_spatial.py`), not real DSP/sensors. RNNoise noise-cancellation is the exception (real). |

---

## PART 1: AI KARAU VIDEO PORTAL — current state

### Competitive set
Zoom Workplace, Microsoft Teams, Google Meet, Webex, RingCentral, Dialpad,
GoTo, Zoho Meeting, Livestorm, ClickMeeting.

### Verdicts (code-verified)

| Feature | Status | Evidence / caveat |
|---|---|---|
| Real-time transcription & captions | ✅ Implemented | Live path is browser Web Speech API; server path (Whisper) is chunk/file-based, not streaming ASR. |
| AI summaries & action items | ✅ Implemented | `meeting_notes.py`, `meeting_intelligence.py`, `karau_collaboration.py`. |
| Live translation | ✅ Implemented | Caption translation via GPT-4o-mini; cached. |
| AI noise cancellation | ✅ Implemented (real) | RNNoise WASM client-side. |
| Speaker diarization | ⚠️ Partial | Per-speaker labels come from the client track; **no acoustic diarization** (no pyannote/voiceprint). |
| Sentiment analysis + copilot | ✅ Implemented | `karau_enhanced_sentiment.py`. |
| Whiteboard | ✅ Implemented | REST CRUD; **no CRDT/OT** real-time sync layer. |
| Polls & Q&A | ✅ Implemented | `karau_polls_challenges.py`, `karau_webinar.py`. |
| Reactions/emojis | ✅ Implemented | `EmojiReactions.jsx`, `karau_gamification.py`. |
| Recording transcript + searchable archive | ✅ Implemented | `karau_recordings.py`, `karau_replay.py /search`. |
| AI highlights/clips + chapters | ✅ Implemented | `karau_replay.py`; has demo fallbacks when no LLM key. |
| Participant scaling / SFU | ❌ Stub | Mesh only; SFU endpoints hardcoded. **P0.** |
| Webinar view-only mode | ✅ Implemented | Host controls, promote/demote, hand-raise. |
| Meeting-media E2EE | ❌ Stub | Advertised, not implemented (chat E2EE is real). **P1.** |
| CRM connectors (Salesforce/HubSpot) | ❌ Absent | Only a **generic outbound webhook** (`karau_extended.py /webhooks`). |
| App marketplace / SDK | ❌ Absent | No developer portal/plugin system. |
| Native mobile meeting client | ❌ Absent | `mobile/` is the job-search app; no WebRTC/meeting screens. |

**Genuine remaining KARAU gaps (ranked):**
1. **P0 — Real SFU/MCU media server** (mediasoup/Janus/LiveKit). Everything else about "1000 participants / webinar scale" is gated on this. The Feb→now webinar UI is real but rides on mesh transport.
2. **P1 — Meeting-media E2EE** (insertable streams / SFrame) to match the E2EE already shipped for chat.
3. **P1 — Replace simulated infra with real or clearly-labeled** (beamforming DSP, spatial/SLAM/IoT). Either implement or mark as "preview/simulated" in-product to avoid over-claiming.
4. **P2 — Acoustic diarization** for unattended transcripts.
5. **P2 — Real-time whiteboard sync** (CRDT) — currently REST/poll.
6. **P2 — Named CRM connectors** on top of the existing webhook bus.
7. **P3 — Native mobile meeting client** (or an in-app WebRTC screen in the Expo app).

**KARAU differentiators already in code** (competitors lack): guest 2FA/OTP + age gate + QR entry, AI breakout-room assignment & themed "lounges," skin-tone-safe rendering, Director Mode (auto multi-cam cutting), cross-meeting Intelligence + auto Team-Status-Report, ghost-booking detection, embedded Lumi mini-messenger, D-ID AI avatar presenter, 50+ language UI. (Several sensor/spatial features are simulated — see caveats.)

---

## PART 2: MEDMATCH JOB TOOLKIT — current state

### Competitive set
LinkedIn Recruiter, Greenhouse, Lever, Workday, iMocha, Eightfold, Recruitly,
HireVue, Handshake, Phenom.

### Verdicts (code-verified)

| Feature | Status | Evidence / caveat |
|---|---|---|
| AI resume parsing | ✅ Implemented | `resume.py` upload + `autofill.py`; confirm PDF/DOCX breadth in `upload_resume`. |
| Semantic matching | ⚠️ Partial | **LLM-prompt + `difflib` fuzzy**, no embeddings. `platform_features.py /semantic-match`, `search_engine.py`. **P1.** |
| Candidate scoring/ranking | ✅ Implemented (LLM) | `ai_talent.py score_candidate`; not a trained ranker (falls back to 50s on error). |
| Talent rediscovery | ⚠️ Partial | Manual via pools/search; no automated silver-medalist re-match. |
| Predictive candidate success | ⚠️ Partial | LLM callback-probability; no trained hiring-outcome model. |
| AI JD generation | ✅ Implemented | `ai_talent.py generate_job_description`. |
| Skill-gap / career pivot | ✅ Implemented (rule-based) | `services/career_pivot.py`, `taxonomy.py /career-pivots/*`. |
| DEI analytics | ⚠️ Partial | Distributions real; index scores hardcoded. |
| Interview scheduling optimization | ⚠️ Partial | Calendar sync + availability + AI prep; **no slot-optimization algorithm**. |
| One-click / smart apply | ✅ Implemented | `smart_apply.py`, `talent_tools.py`. |
| Personalized job recommendations | ⚠️ Partial | Fuzzy/intent search + crawl; **no behavioral/collaborative recommender** for candidates. |
| AI candidate chatbot | ✅ Implemented | `ai_features.py /assistant` (Dragon). |
| Talent CRM / nurture | ✅ Implemented | `talent_crm.py /campaigns`. |
| Interview scorecards | ✅ Implemented | `ai_talent.py /scorecards`. |
| Multi-channel outreach | ⚠️ Partial | Email real; **SMS/InMail recorded but not dispatched** (`talent_tools.py /outreach/send`). |
| Team collaboration / RBAC | ✅ Implemented | `recruiter_rbac.py`, `talent_tools.py /collaborate/*`. |
| Offer management + approval | ✅ Implemented | `advanced_features.py /offers*`. |
| Onboarding workflow | ❌ Absent | No routes. |
| Requisition approval workflow | ❌ Absent | Job creation is direct, no approval chain. |
| Time-to-hire / cost-per-hire / source | ⚠️ Partial | **Hardcoded** in `ai_talent.py /hiring-metrics` (funnel analytics elsewhere are real). |
| Job board multi-posting (outbound) | ❌ Absent | Inbound aggregation only. |
| HRIS / background check | ⚠️ Partial | Config/record **scaffolding** (`platform_features.py`); no vendor SDK wiring. |
| Credential verification (PSV/ORCID/Credly) | ✅ Implemented | `psv.py` (OIG-LEIE, NPI, ORCID), `orcid_oauth.py`, `credentials.py` + `credly_service.py`. |

**Genuine remaining MedMatch gaps (ranked):**
1. **P1 — Real matching layer** (vector embeddings for skills/roles) to back "semantic match" and personalized recommendations with something beyond fuzzy string overlap.
2. **P1 — Make hardcoded analytics real** — `/hiring-metrics` (time-to-hire, cost-per-hire, source effectiveness) and DEI index scores. *(Note the status-casing gotcha below.)*
3. **P2 — Trained hiring-outcome model** (reuse the existing `ml_model_trainer.py` infra, retarget from compliance issues to hire success).
4. **P2 — Real SMS/InMail dispatch** (e.g., Twilio) behind the existing `/outreach/send` channel field.
5. **P2 — Talent rediscovery engine** (auto re-surface past applicants against new reqs).
6. **P3 — Onboarding & requisition-approval workflows.**
7. **P3 — Named HRIS / background-check vendor integrations** on the existing scaffolding.

**MedMatch differentiators already in code** (competitors lack): healthcare PSV (OIG-LEIE + NPI), Trust-Score engine with leaderboard, ORCID + Credly verified badges, mutual-match + ghost-mode double-opt-in, AI-compliance/AI-QA oversight + candidate-transparency explainability, full interview-prep suite (voice coach, QA/video practice, real-time STT), live job-freshness scoring, 50+ language support.

---

## PART 3: PRIORITIZED RECOMMENDATION ROADMAP

Ordered by leverage, and by how safely a change can be shipped and verified.

### Tier A — Quick, safe, verifiable code wins (days)
These are self-contained and close real gaps. Each needs a test because backend
tests hit a running server (see `CLAUDE.md`).

1. **Make `/hiring-metrics` real** (`routes/ai_talent.py:226`). Compute
   `avg_time_to_hire_days` from `hired` applications as `updated_at − applied_at`.
   ⚠️ **Gotcha:** applications are written with `status:"Applied"` (capitalized,
   `routes/jobs.py:765`) while this endpoint queries lowercase `"hired"/"rejected"`.
   Normalize status casing first (or the "real" metric silently returns 0).
   `avg_cost_per_hire` has **no source data** — make it a configurable input or
   drop it rather than fabricate. Derive `source_effectiveness` from `job.source`
   only if that field is reliably populated.
2. **Make DEI index scores real** (`routes/dei_analytics.py`). Compute
   `gender_parity_index` from the already-real `gender_distribution` instead of
   the hardcoded `0.85`; drop or compute the `+3%` deltas.
3. **Label simulated features in-product.** Add a "preview/simulated" badge where
   backends are mock (beamforming, SFU status, spatial/SLAM/IoT, meeting E2EE) so
   the product does not over-claim. Cheap, protects trust.

### Tier B — Substantive features (weeks)
4. **KARAU SFU migration (P0).** Stand up a real SFU (LiveKit is already the
   planned direction per `.emergent/summary.txt`), swap the mesh signaling in
   `services/karau_meet/webrtc_signaling.py`, wire TURN, and replace the
   `meeting_infrastructure.py /sfu/*` stubs with live status. Unblocks every
   "scale/webinar" claim.
5. **Vector matching layer (P1).** Add an embeddings index (skills, roles,
   resumes) behind `platform_features.py /semantic-match` and job
   recommendations. Keep the LLM criteria-extraction as the query front-end.
6. **Meeting-media E2EE (P1).** Extend the real chat E2EE (`utils/e2ee.js`) to
   media via insertable streams/SFrame; replace the `/e2ee/*` protocol-string stub.
7. **Real SMS/InMail dispatch (P2)** behind `talent_tools.py /outreach/send`.

### Tier C — Larger / organizational (months)
8. Trained hiring-outcome model (retarget existing ML infra).
9. Native mobile meeting client (or in-app WebRTC screen in the Expo app).
10. Onboarding & requisition-approval workflows.
11. Named CRM / HRIS / background-check vendor integrations.
12. Compliance certifications (HIPAA BAA, SOC 2) — process, not code.

### Cross-cutting engineering (from `.emergent/summary.txt`, still open)
- Verify the Phase-4 accessibility CI job is green on the runner.
- CRA → Vite migration (build speed + CVE surface).
- Sentry APM / production observability.
- Decompose backend "god files" and large frontend pages.

---

## Methodology

- **Evidence-based:** every verdict was checked against `backend/routes/*.py`,
  `backend/services/**`, and `frontend/src/{pages,components}/**`. "Stub" means a
  route returns hardcoded/simulated data; "Partial" means a real-but-incomplete
  implementation; "Implemented" means a working end-to-end path (LLM-backed
  features degrade to mock output when `EMERGENT_LLM_KEY` is absent).
- **Benchmark framing** retained from the Feb 2026 competitive set for continuity.
- Prior scores were feature-list estimates; the revised two-axis scores separate
  *feature breadth* (high) from *production depth* (the real remaining work).

_Revised 10 August 2026. Supersedes the February 2026 edition._
