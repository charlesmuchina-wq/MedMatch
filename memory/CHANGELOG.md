# AI KARAU Changelog

## Mar 2, 2026 — Phase 3: Hardware Discovery, Breakout Lounges, Polls, Biometric Verification

### New Features

#### Hardware Discovery Dashboard
- Auto-detect 6 device types: 360 cameras, mic arrays, IoT hubs, XR headsets, displays, speaker arrays
- Device scan with realistic simulated results (Meeting Owl 3, Shure MXA920, Crestron CP4, Apple Vision Pro, Samsung Flip, Bose ES1)
- Live/Simulation mode toggle per device
- Backend: `karau_hardware_discovery.py` with 5 endpoints

#### Virtual Breakout Lounges
- Interactive 2D map with draggable avatar positioning
- Proximity-based audio (150px threshold with volume falloff)
- Host controls: create/edit/close lounges with topics and capacity
- Automatic lounge zone detection based on avatar position
- Backend: `karau_breakout_lounges.py` with 6 endpoints

#### Interactive Polls & Challenges
- 4 poll types: Multiple Choice, Quiz (with scoring), Word Cloud, Rating (1-10)
- Duplicate vote prevention (409 conflict)
- Quiz scoring with correct_answer_id and leaderboard point integration
- Poll lifecycle: create -> vote -> results -> close
- Backend: `karau_polls_challenges.py` with 6 endpoints

#### Biometric Feed Verification
- SHA256 session watermarks with unique visual patterns
- Rolling integrity score with continuous verification checks
- Trust levels: high (>90%), medium (>70%), low (>40%), unverified
- Simulated anti-deepfake detection for 6 participants
- Backend: `karau_biometric_verify.py` with 3 endpoints

### Testing
- 35/35 backend tests passed (100%)
- Test report: `/app/test_reports/iteration_154.json`

---

## Mar 2, 2026 — Meeting Replay with Director Cuts + Hardware Integration Layer

### New Features

#### Meeting Replay with Director Cuts
- Cinematic replay page at `/karau-meet/replay/:meetingId`
- Playback controls (play/pause, skip +/-15s, timeline scrubbing)
- Key moments markers (intro, presentation, discussion, decision, action_item, wrap_up)
- Camera view simulation (panoramic gallery, speaker close-up, conversation side-by-side)
- AI Highlights generation via Emergent LLM in 3 styles (executive_summary, action_items, full_replay)
- View distribution analytics with percentages
- Demo replay auto-generation for showcase (30 min, ~75 cuts, 7 key moments)

#### SLAM Spatial Tracking
- 3D room mapping with user positions around conference table
- Face confidence scoring and auto-frame adjustments
- Lighting quality assessment with auto-enhancement recommendations
- Top-down room visualization with position dots

#### 360 Multi-Focus Framing
- Panoramic-to-headshot extraction pipeline
- Per-person crop regions with quality scores and gaze direction
- Panoramic view simulation with speaking indicators
- Headshot grid with real-time quality metrics

#### Apple Vision Pro / WebXR Spatial Meetings
- 3D meeting room environments (boardroom, amphitheater, lounge)
- Spatial persona rendering with headset type labels (Vision Pro, Quest 3, Browser)
- Hand tracking, eye tracking, spatial audio, shared objects capabilities
- 3D perspective room visualization with positioned avatars

#### IoT Room Environmental Control
- Voice-activated commands: "dim the lights", "close shades", "raise temperature", etc.
- 4 room presets: Presentation, Discussion, Break, Focus
- 7 controllable devices: 3x lights, temperature, shades, display, speaker volume
- Natural language command parsing with suggestions for unrecognized commands

#### Adaptive Beamforming Audio
- 4 beam modes: Auto, Directional, Omnidirectional, Interview
- Polar beam pattern SVG visualization
- Per-user audio profiles with SNR scoring and noise type detection
- Noise source detection (ambient, HVAC, keyboard) with auto-suppression
- Audio quality dashboard with latency, sample rate, channels metrics

### Files Created
- `backend/routes/karau_slam_spatial.py`, `karau_webxr.py`, `karau_iot_control.py`, `karau_beamforming.py`, `karau_replay.py`
- `frontend/src/pages/KarauMeet/MeetingReplayPage.jsx`
- `frontend/src/components/KarauMeet/SpatialTrackingPanel.jsx`, `PanoramicFramingPanel.jsx`, `SpatialMeetingPanel.jsx`, `RoomControlPanel.jsx`, `BeamformingPanel.jsx`, `ReplayListPanel.jsx`

### Testing
- 51/51 backend tests passed (100%)
- All frontend components verified
- Test report: `/app/test_reports/iteration_153.json`

---

## Mar 2, 2026 — Distance Zero Feature Suite (Phase 1)

### Bug Fix
- **P2 Fix**: Gamification endpoints (`/api/karau/webinar/{id}/reaction`, `/api/karau/webinar/{id}/leaderboard/track`) now return 401 for unauthenticated requests (was 500). Changed `get_current_user` to `require_auth`.

### New Features

#### Cinematic Director Mode
- AI-powered automatic camera view switching between Panoramic, Speaker Close-Up, Conversation, and Manual modes
- Backend: `karau_director.py` with 3 endpoints (set mode, get mode, analyze patterns)
- Frontend: `DirectorModePanel.jsx`, `useDirectorMode.js` hook
- Integrated into WebinarLiveRoom with control button

#### QR Code Touchless Meeting Entry
- Generate QR codes for instant meeting join
- Token-based validation with expiry and max-use tracking
- Backend: `karau_qr_entry.py` with CRUD endpoints
- Frontend: `QRCodePanel.jsx` with copy link and deactivation

#### Ghost Booking Prevention
- Activity pinging system (60s intervals)
- Idle meeting detection with configurable timeout
- Auto-release and manual keep-alive functionality
- Backend: `karau_ghost_booking.py` with 5 endpoints
- Frontend: `GhostBookingAlert.jsx`, `useGhostBooking.js` hook

#### Enhanced Real-Time Sentiment Dashboard
- Per-participant heatmap with attention/confusion/engagement/energy metrics
- AI recommendations: clarify, engage, break, energize based on aggregate scores
- History tracking with sliding window (last 30 data points per participant)
- Backend: `karau_enhanced_sentiment.py`
- Frontend: `SentimentDashboard.jsx` with real-time polling

#### Multiplayer AI Copilots
- Cross-meeting intelligence using Emergent LLM
- Context from current meeting, past meeting summaries, shared documents
- Query history tracking per meeting
- Frontend: `CopilotPanel.jsx` with suggestion prompts and chat interface

### Files Created
- `backend/routes/karau_director.py`
- `backend/routes/karau_qr_entry.py`
- `backend/routes/karau_ghost_booking.py`
- `backend/routes/karau_enhanced_sentiment.py`
- `frontend/src/hooks/useDirectorMode.js`
- `frontend/src/hooks/useGhostBooking.js`
- `frontend/src/components/KarauMeet/DirectorModePanel.jsx`
- `frontend/src/components/KarauMeet/QRCodePanel.jsx`
- `frontend/src/components/KarauMeet/GhostBookingAlert.jsx`
- `frontend/src/components/KarauMeet/SentimentDashboard.jsx`
- `frontend/src/components/KarauMeet/CopilotPanel.jsx`

### Files Modified
- `backend/routes/karau_gamification.py` — require_auth fix
- `backend/server.py` — 4 new routers registered
- `frontend/src/pages/KarauMeet/WebinarLiveRoom.jsx` — new imports, hooks, controls, panels

### Testing
- 36/36 backend tests passed (100%)
- Frontend components verified clean
- Test report: `/app/test_reports/iteration_152.json`

---

## Mar 1, 2026 — Gamification, Video Framing, Spatial Audio

### New Features
- AI-Powered Video Framing (active speaker main stage)
- Gamification Suite (emoji reactions, participation leaderboard)
- Spatial Audio Integration (Web Audio API with HRTF PannerNode)

---

## Prior History
See `/app/docs/GAP_ASSESSMENT.md` for full competitive benchmarking.

## 2026-06-22 — Phase 4 CI Accessibility Gate RCA & CAPA
- RCA: Phase 4 (only Node job) failed after Node bump 20→22; craco+react-scripts5+React19 needs Node 20.
- Corrective: pinned `phase4-accessibility` to Node 20 in `.github/workflows/test.yml`.
- Preventive: scan a production build (`yarn build` + `serve -s build`) instead of CRA dev server; CI=false on build (craco treats warnings as errors when CI=true); gate reads canonical summary path with guard.
- Verified locally: build 46s, served build scan = 0 critical/serious across 12 routes. Final green run requires user push (runner-only validation).
- Doc: `/app/docs/security/PHASE4_CI_RCA_CAPA.md`

## 2026-06-22 — Managed Agents (Claude) MVP
- New module: Claude-powered (claude-sonnet-4-6 via Emergent key) "Managed Agents".
- Backend routes/managed_agents.py (/api/agents): trackable worklist task CRUD + stats; extract-worklist (transcript->tasks); agent definitions (3 admin templates + client custom); conversational agent with JSON tool-loop (tools: create_task/update_task/list_tasks/send_followup_email). Registered in server.py.
- Frontend pages/AgentsPage.jsx (route /agents + nav "AI Agents"): Worklist / Extract / Agent chat / Agents-builder tabs, theme-aware, full data-testids.
- Reuses Whisper transcription, send_email service, require_auth. Tool-use implemented as ReAct JSON protocol (LlmChat has no native function-calling).
- Tested: testing_agent iteration_221 — backend 8/8, frontend 100% flows, 0 issues.

## 2026-06-22 — P0/P1 docs + P2 (Sentry + Vite decision)
- P0: LiveKit SFU migration design doc — /app/docs/architecture/LIVEKIT_SFU_MIGRATION.md (replaces mesh P2P ~4-cap; token endpoint, webhooks, egress->Whisper->agents, phased rollout).
- P1: Microsoft 365 Publisher Attestation evidence package — /app/docs/compliance/M365_PUBLISHER_ATTESTATION.md (scopes justification, data handling, security, submission steps; lists inputs still needed).
- P2 Sentry APM: wired gated (no-op without DSN) on backend (server.py, sentry-sdk[fastapi,pymongo]) + frontend (index.js, @sentry/react + ErrorBoundary). Needs SENTRY_DSN + REACT_APP_SENTRY_DSN to activate.
- P2 Vite: RECOMMEND DEFER — conflicts with Emergent craco visual-edits plugin + 135 files on protected REACT_APP_* vars; CVE/build drivers already mitigated. Doc: /app/docs/architecture/P2_TOOLING_OBSERVABILITY.md.

## 2026-06-22 — Zero-cost in-house error tracking (replaces paid Sentry)
- Backend routes/observability.py: /api/observability/error (capture, optional auth), /errors, /errors/stats, PATCH/DELETE /errors/{id} (admin); server.py middleware captures unhandled 5xx to Mongo error_logs.
- Frontend utils/errorReporter.js (window.onerror + unhandledrejection) wired in index.js; Sentry ErrorBoundary onError also reports.
- Admin UI pages/AdminErrorsPage.jsx at /admin/errors (nav "Error Logs"): stats, filters, stack traces, resolve/delete.
- Sentry SDK retained as Sentry-compatible GlitchTip client (free self-host) — activate by setting SENTRY_DSN / REACT_APP_SENTRY_DSN to a GlitchTip DSN. Sentry hosted = 14-day trial only.
- Verified via curl (capture/list/stats/401) + screenshot (admin page renders with captured error).

## 2026-06-22 — P0 LiveKit Phase 0 spike (SFU PoC) — DONE
- Backend routes/livekit_spike.py: POST /api/livekit/token (auth, VideoGrants, 2h TTL), POST /api/livekit/webhook (raw-body signature verify), GET /api/livekit/status. livekit-api==1.1.0.
- Frontend pages/LiveKitSpikePage.jsx at /livekit-spike (nav "Video (LiveKit)") using @livekit/components-react <LiveKitRoom>/<VideoConference>; invite link via ?room=.
- Env: backend LIVEKIT_URL/LIVEKIT_API_KEY/LIVEKIT_API_SECRET; frontend REACT_APP_LIVEKIT_URL (provided by user; medmatch-5zieh7od.livekit.cloud).
- Verified: token grants correct + 2h exp; LiveKit Cloud reachable (room.list_rooms); client connects to SFU and renders VideoConference with controls.
- Optional next: register webhook URL in LiveKit dashboard; Phase 1 dual-stack flag in MeetingRoom.jsx.

## 2026-06-22 — P0 LiveKit Phase 1 dual-stack (flag) — STARTED & verified
- Backend karau_meet.py: KARAU_MEDIA_BACKEND env (default "p2p") + per-meeting settings.media_backend override; resolve_media_backend(); /meetings/{id}/info now returns media_backend; new POST /meetings/{id}/livekit-token (authed host or guest). Shared create_access_token() in livekit_spike.py.
- Frontend: MeetingRoomSwitch.jsx (routes /karau-meet/room/{id}) -> LiveKitMeetingRoom.jsx (SFU) when livekit, else untouched P2P MeetingRoom (fallback intact). KarauMeetPortal uses the switch.
- Verified: meeting with settings.media_backend=livekit -> info shows livekit; token mints for host (is_host true) and guest; /room/{id} renders LiveKit SFU room (VideoConference, connected as Guest). Default meetings unchanged (p2p).
- Enable globally: set KARAU_MEDIA_BACKEND=livekit in backend/.env. Per-meeting: settings.media_backend="livekit".
- Remaining: webinar /live path (separate WebinarLiveRoom), load test, egress recording->Whisper->agents.

## 2026-06-22 — P0 LiveKit Phase 1 finish: webinar mode (attendee canPublish=false)
- Backend: /meetings/{id}/livekit-token now role-based — host/panelist can_publish=true, webinar attendee can_publish=false; webinar detected via body {webinar:true} or settings.is_webinar/mode; panelists via settings.panelists. Returns role + can_publish.
- Frontend: WebinarLiveSwitch.jsx routes /karau-meet/webinar/{id}/live -> LiveKitMeetingRoom (webinar=true, attendee view-only) when livekit, else legacy WebinarLiveRoom. LiveKitMeetingRoom takes `webinar` prop + shows "Webinar · view-only" badge.
- Verified: host token role=host/publish; guest attendee role=attendee/can_publish=false; webinar /live renders LiveKit with NO mic/cam publish controls (only Chat/Leave/Start Audio).
- Load test: use `lk load-test` CLI (documented in LIVEKIT_SFU_MIGRATION.md). Phase 2 HLS egress + egress recording->Whisper->agents BLOCKED on S3-compatible storage creds.

## 2026-06-22 — P1 foundation: public legal pages (Privacy + Terms)
- Created public, no-auth pages: /legal/privacy (PrivacyPolicyPage.jsx) and /legal/terms (TermsPage.jsx); added to isPublicRoute + public Routes block in App.js.
- Content drafted from actual data handling (account/content/MS+Google consent data, AI processing, sharing, retention, GDPR rights). Placeholders: [Legal Entity Name], [Hosting Region], [privacy@/security@/support@your-domain] for user to fill.
- M365 attestation doc updated: Privacy/Terms now hosted in-app; remaining inputs = Partner ID, legal entity + contacts, support email, hosting region, prod Entra client ID/redirect URIs.
- Verified: both pages render without login (testids present).

## 2026-06-22 — Legal pages finalized + discoverability
- Filled legal-page placeholders with brand defaults: operator "AI KARAU", contacts privacy@/security@/support@aikarau.com; hosting-region claim softened.
- Added Privacy/Terms links: LumiFooter (app-wide footer) + LoginPage ("By continuing you agree to our Terms and Privacy Policy"). Verified rendering.
- Reviewer-friendly (Microsoft/app-store look for these). Remaining M365 blocker: Partner Center account + prod Entra IDs (user-side only).
