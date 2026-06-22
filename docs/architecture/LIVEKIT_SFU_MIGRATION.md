# AI KARAU — LiveKit SFU Migration Design (P0)

**Status:** Proposed · **Author:** Engineering · **Date:** 2026-06-22
**Goal:** Replace the current full-mesh WebRTC P2P topology (practical ceiling ~4
participants) with a LiveKit SFU so AI KARAU meetings/webinars scale to dozens
(meetings) and thousands (webinar/broadcast) of participants.

---

## 1. Current State (as-built)

| Layer | File | Behaviour |
|------|------|-----------|
| Frontend media | `frontend/src/components/KarauMeet/MeetingRoom.jsx` | Full **mesh**: `peerConnectionsRef.current` holds one `RTCPeerConnection` per *other* participant. Each client `createOffer`/`addTrack` to every peer. |
| Signaling | `backend/services/karau_meet/webrtc_signaling.py` (`SignalingManager`) | In-memory `participants` per meeting; relays `offer`/`answer`/`ice_candidate`; broadcasts join/leave; keeps message history. |
| Signaling transport | `backend/routes/karau_webrtc.py` | `WS /api/karau-webrtc/ws/{meeting_id}` + `/ice-servers`, `/room/{id}/participants`, `/room/{id}/status`. |
| NAT traversal | `backend/services/karau_meet/turn_service.py` | STUN+TURN from **Xirsys** (`get_ice_servers`). |
| Meeting CRUD | `backend/routes/karau_meet.py` | Rooms, scheduling, membership. |

### Why it caps at ~4
Mesh is **O(N²)** connections and **O(N) upstream** per client. A participant
publishing 720p (~1.5–2.5 Mbps) to `N-1` peers needs `(N-1)×` upstream and
decodes `N-1` inbound streams. At N=5 most consumer uplinks and CPUs saturate.
There is no central media routing, no server-side recording of the composited
stream, no simulcast/SVC, and no broadcast path.

---

## 2. Target Architecture (SFU)

Each client publishes **one** upstream to the **LiveKit SFU**; the SFU forwards
(selectively, per-subscriber) to others. Upstream becomes **O(1)** per client;
the server fans out. Add **simulcast** (3 spatial layers) so the SFU sends each
subscriber the layer their bandwidth/viewport allows.

```
        ┌──────────── LiveKit SFU (media) ───────────┐
publish │  selective forwarding + simulcast layer    │ subscribe
  ──────▶  selection + server-side recording/egress  ◀──────
        └────────────────────────────────────────────┘
              ▲ join token (JWT)        ▲ webhooks
   FastAPI (our backend): mints LiveKit access tokens,
   manages rooms/roles, receives egress + room webhooks.
```

- **Meetings (≤ ~50 active):** all participants publish+subscribe (SFU).
- **Webinars (1→many):** hosts/panelists publish; attendees subscribe only
  (LiveKit `canPublish=false`), scaling to thousands via the same SFU + optional
  HLS egress for very large audiences.

---

## 3. LiveKit Deployment Options

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **LiveKit Cloud** | Zero-ops, global edge, autoscale, built-in TURN/egress/recording, SLA | Per-minute cost | **Phase 1 (now)** — fastest path to scale; validate product. |
| **Self-hosted** (K8s / VM) | Cost control at high volume, data residency (G5/CISO) | Run SFU + Redis + TURN + egress; ops burden | **Phase 3** once usage + compliance justify it. |

Self-host components when we move: `livekit-server` (with Redis for multi-node),
`livekit-egress` (recording/HLS), coturn (or LiveKit's TURN), behind a UDP/TCP
load balancer with a wide UDP port range.

**Decision:** start on **LiveKit Cloud**; keep the integration provider-agnostic
behind our token endpoint so a later self-host swap is config-only.

---

## 4. Backend Changes

### 4.1 Token minting (replaces SDP relay role)
New endpoint, e.g. `POST /api/karau-webrtc/livekit/token`:
- Auth via existing JWT (`verify_token` in `karau_webrtc.py`).
- Validate the user is a member/host of `meeting_id` (reuse `karau_meet.py`).
- Mint a LiveKit `AccessToken` (server SDK `livekit-api`) with grants:
  - `room = meeting_id`, `identity = user_id`, `name = display_name`
  - `canPublish` = host/panelist; attendees `canPublish=false` (webinar)
  - `canSubscribe = true`, `canPublishData = true` (chat/reactions)
- Return `{ url: LIVEKIT_WS_URL, token }`.

```python
# pip dependency: livekit-api
from livekit import api
def mint_token(room, identity, name, can_publish):
    grant = api.VideoGrants(room_join=True, room=room,
                            can_publish=can_publish, can_subscribe=True,
                            can_publish_data=True)
    return (api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            .with_identity(identity).with_name(name)
            .with_grants(grant).to_jwt())
```

### 4.2 Webhooks
`POST /api/karau-webrtc/livekit/webhook` (verify LiveKit signature): handle
`room_started/finished`, `participant_joined/left`, `egress_ended` to keep
`db.karau_participants` / recording rows in sync. This replaces the in-memory
participant tracking in `SignalingManager` as the source of truth.

### 4.3 Recording / transcription bridge
Use LiveKit **Egress** (room composite → MP4/HLS) → store via existing
`services/object_storage` → reuse `services/transcription_service.auto_transcribe_and_store`
(Whisper) → feeds the new **Managed Agents** worklist extraction. (Nice synergy:
SFU server-side recording makes transcripts reliable, which powers `/agents`.)

### 4.4 ICE / TURN
LiveKit Cloud provides its own TURN — `turn_service.py`/Xirsys becomes unused for
the LiveKit path (keep until P2P is fully retired). Self-host phase reintroduces
coturn.

### 4.5 Env vars (backend/.env — no defaults)
```
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_WS_URL=wss://<project>.livekit.cloud
LIVEKIT_WEBHOOK_KEY=...   # same as API key/secret pair for signature verify
```

## 5. Frontend Changes (`MeetingRoom.jsx`)

Remove the mesh machinery (`peerConnectionsRef`, manual `createOffer/answer`,
ICE handlers, per-peer `addTrack`). Replace with the LiveKit client SDK.

- Add deps: `livekit-client`, `@livekit/components-react` (+ `@livekit/components-styles`).
- Flow: `GET token` → `const room = new Room({ adaptiveStream:true, dynacast:true })`
  → `await room.connect(LIVEKIT_WS_URL, token)` → `room.localParticipant.enableCameraAndMicrophone()`.
- Render remote tiles by subscribing to `RoomEvent.TrackSubscribed`; or adopt
  `@livekit/components-react` (`<LiveKitRoom>`, `<GridLayout>`, `<ParticipantTile>`)
  to delete most custom tile/grid code.
- Enable **simulcast** on publish (default on) + **adaptive stream** + **dynacast**
  (SFU pauses layers nobody views).
- Reuse existing UI affordances: data channel (`room.localParticipant.publishData`)
  for chat/reactions/polls already in the app; screen-share via
  `setScreenShareEnabled(true)`.
- Keep our WS (`/ws/{meeting_id}`) **only** for app-level events not tied to media
  (or migrate those to LiveKit data messages and retire it).

## 6. Data Model

- `db.karau_recordings`: add `egress_id`, `livekit_room`, keep existing
  `transcription_*` fields (unchanged downstream).
- `db.karau_participants`: now updated via webhooks (`identity`, role, joined/left).
- No breaking changes to `karau_meet` room documents; add `media_backend: "livekit"|"p2p"`
  flag for gradual rollout.

## 7. Migration Phases (incremental, reversible)

| Phase | Scope | Exit criteria |
|------|-------|---------------|
| **0. Spike** | LiveKit Cloud project; token endpoint; throwaway page connects 2 clients | ✅ **DONE (2026-06-22)** — `routes/livekit_spike.py` (`/api/livekit/token` + `/webhook` + `/status`); `pages/LiveKitSpikePage.jsx` at `/livekit-spike` (nav "Video (LiveKit)") using `@livekit/components-react`. Verified: token mint with correct grants, LiveKit Cloud reachable, client connects to SFU and renders `<VideoConference>`. |
| **1. Dual-stack behind flag** | `media_backend` per room; new rooms → LiveKit, old → P2P; SDK swap in `MeetingRoom.jsx` gated by flag | 10–20 participant meeting stable; recording→transcript works |
| **2. Webinar mode** | Attendee `canPublish=false`; optional HLS egress | 200+ attendee webinar stable |
| **3. Default + cleanup** | LiveKit default for all; remove mesh code + Xirsys path | Mesh code deleted; 0 regressions |
| **4. (Optional) Self-host** | Move to self-hosted SFU+egress+TURN for cost/residency | Parity + cost target met |

## 8. Cost (order-of-magnitude, LiveKit Cloud)
Billed per participant-minute (+ egress minutes for recording/HLS). Model:
`active_participants × meeting_minutes × rate` + recording. Re-evaluate self-host
at the crossover volume (typically thousands of daily participant-hours).

## 9. Risks & Mitigations
- **UDP blocked on corporate networks** → LiveKit TURN/TCP/TLS 443 fallback (built-in).
- **Cost surprise at scale** → usage dashboards + alerts; dynacast/adaptive on; self-host plan ready.
- **Vendor lock-in** → isolate behind our token endpoint + a thin media adapter; LiveKit is open-source (self-host exit).
- **Compliance (G5/CISO, data residency)** → Phase 1 documents DPA/region; Phase 4 self-host for residency.
- **Regression during swap** → feature flag + dual-stack; keep P2P until Phase 3.

## 10. Definition of Done
- Token + webhook endpoints live and signature-verified.
- `MeetingRoom.jsx` connects via LiveKit with simulcast/adaptive/dynacast.
- 25-person meeting and 200-person webinar verified stable.
- Server-side recording → Whisper transcript → `/agents` worklist extraction works.
- Mesh + Xirsys code removed (Phase 3); rollback flag documented.

## 11. Open Decisions (need sign-off)
1. **Cloud vs self-host for Phase 1** (recommend Cloud).
2. **Webinar very-large audience**: WebRTC subscribe (≤~3k) vs HLS egress (unbounded, ~10–30s latency).
3. **Retire app WS** entirely in favor of LiveKit data messages, or keep for non-media events.
