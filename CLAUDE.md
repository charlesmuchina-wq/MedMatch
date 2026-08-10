# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this project is

**MedMatch-AI** is a large, feature-dense monorepo for a healthcare-focused
recruitment / talent platform, fused with two sibling products that share the
same backend and auth:

- **MedMatch** — job seeking, resumes, applications, interviews, recruiter/ATS
  tooling, credential verification (PSV), compliance (WCAG, DEI, global).
- **KARAU** — webinar / video-meeting suite (WebRTC, recordings, replay,
  scheduling, spatial audio, etc.), routes prefixed `karau_*`.
- **ENZI / LUMI** — AI professional messenger + workspace (channels, bots,
  meetings-to-channels), routes prefixed `enzi_*` / `lumi_*`.

> ⚠️ The root `README.md` is a placeholder ("Here are your Instructions") and
> `ROADMAP.md` / `CHANGELOG.md` describe the KARAU/ENZI side. Treat this
> `CLAUDE.md` and `docs/` as the source of truth for structure, not the README.
> The richest narrative context lives in `.emergent/summary.txt` and the dated
> reports in `docs/` (e.g. `SYSTEM_REQUIREMENTS_AUDIT.md`, `GAP_ASSESSMENT.md`).

## Repository layout

```
backend/     FastAPI + MongoDB (Motor) API server        → the core of the app
frontend/    React 19 web app (CRA + CRACO, Tailwind, shadcn/ui, Radix)
mobile/      Expo / React Native app (expo-router, NativeWind), EAS builds
desktop/     Electron desktop wrapper
tests/       Top-level integration tests (requests-based, hit a running server)
scripts/     One-off Python utilities (translations, video/locale generation)
docs/        Audits, roadmaps, deployment playbooks, security evidence
data/        AI QA + CAPA seed/reference data
memory/      Persisted assistant/agent context
.github/     CI workflows (test.yml, mobile-builds.yml)
```

### Backend (`backend/`)

- `server.py` — FastAPI app factory, MongoDB pooling, CORS, caching, scheduler
  startup, and **the single place every router is registered**. ~430 lines of
  imports + `include_router(...)` calls.
- `routes/` — **~150 route modules**, one `router` (an `APIRouter`) per file,
  grouped by domain: `auth`, `jobs`, `resume`, `interview`, `recruiter`, `ats`,
  `payments`, `karau_*`, `enzi_*`, `lumi_*`, `ml_*`, compliance/audit, etc.
- `services/` — business logic and integrations (AI supervisor, rate limiter,
  video generation, transcription, PSV/trust-score, ML training/prediction).
- `models/schemas.py` — Pydantic request/response models.
- `util/`, `utils/` — helpers (note: both spellings exist; check before adding).
- `k8s/production.yaml`, `PRODUCTION_CONFIG.md` — production deployment config.
- `requirements.txt` — pinned deps (FastAPI 0.110, Motor, Pydantic v2, etc.).

### Frontend (`frontend/`)

- CRA bootstrapped, built with **CRACO** (`craco.config.js`); `@` aliases to
  `src/`. Tailwind + shadcn/ui (`components.json`) + Radix primitives.
- `src/pages/*.jsx` — top-level pages (one per route). `src/App.js` imports every
  page and wires all `<Route>`s + the multi-portal shell.
- `src/components/`, `src/contexts/`, `src/hooks/`, `src/lib/`, `src/services/`,
  `src/locales/` (i18n — heavily used, see `scripts/*translate*`).

### Mobile (`mobile/`) & Desktop (`desktop/`)

- Mobile: Expo SDK 54, `expo-router` file-based routes under `app/`
  (`(auth)/`, `(tabs)/`, `job/[id]`). Builds via EAS (`eas.json`, `app.json`).
- Desktop: Electron (`main.js`, `preload.js`), packaged via `build.sh`.

## Running locally

**Backend** (needs a MongoDB instance):
```bash
cd backend
pip install -r requirements.txt   # heavy; see CI notes about pin conflicts
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
# health check: GET http://localhost:8001/api/health
```
Required env (backend `.env` in `backend/`):
- `MONGO_URL`, `DB_NAME` (defaults to `MedMatch`) — **required**.
- `EMERGENT_LLM_KEY` — key for all LLM calls (see below).
- `JWT_SECRET_KEY`, `CORS_ORIGINS` (default `*`), plus pooling/cache overrides
  (`MONGO_POOL_SIZE`, `CACHE_EXPIRE_SECONDS`, `MAX_CONCURRENT_USERS`).

**Frontend**:
```bash
cd frontend
yarn install
yarn start        # CRACO dev server on :3000
yarn build        # production bundle
```
Frontend talks to the API via `process.env.REACT_APP_BACKEND_URL` (set in
`frontend/.env`). All backend routes are under the `/api` prefix.

**Mobile**: `cd mobile && yarn install && yarn start` (Expo). API base URL is
read from Expo config/constants.

## Key conventions & gotchas

- **Every backend route is mounted under `/api`.** `include_router(..., prefix="/api")`
  in `server.py`. The frontend/mobile always call `${BACKEND_URL}/api/...`.
- **Adding a backend endpoint** takes two edits in `server.py`: (1) import the
  router (either inside the big `from routes import (...)` block near the top or
  as a dedicated `from routes.<mod> import router as <name>_router` line), and
  (2) add a matching `app.include_router(<name>_router, prefix="/api")`. Define
  the endpoints in a `routes/<domain>.py` module exposing `router = APIRouter()`.
- **Auth** lives in `routes/auth.py`: bcrypt password hashing, session tokens +
  JWT, `get_current_user(request)` / `require_auth(request)` dependencies, plus
  Google / Microsoft / Apple SSO and membership-tier checks. Reuse these helpers
  rather than re-implementing auth.
- **LLM access** goes through `emergentintegrations`' `LlmChat` using
  `EMERGENT_LLM_KEY` (used in ~180 places). Do **not** wire in raw OpenAI/Gemini
  clients for new features — follow the existing `LlmChat` pattern.
- **Hardcoded `/app/...` paths.** A lot of code (CAPA, ai_qa, videos, static
  assets) assumes the repo is mounted at `/app` (the Emergent container layout).
  CI works around this by symlinking `/app -> $GITHUB_WORKSPACE`. If you touch
  file paths, prefer keeping the existing `/app/...` convention or make paths
  configurable; don't silently break the symlink assumption.
- **i18n**: locale JSON under `frontend/src/locales/` is generated/maintained by
  `scripts/*translate*.py` and `generate_locales.py`. Prefer regenerating over
  hand-editing large locale files.
- **`util/` vs `utils/`**: both directories exist in `backend/`. Check where a
  helper already lives before adding a new one.

## Testing

Two test surfaces exist:

1. **`backend/tests/`** — pytest suites organized as CI "gates":
   - `test_phase1_functional.py` (Gate G1, functional)
   - `test_phase2_reliability.py`
   - `test_phase3_regression.py` (Gate G3, regression)
   - `test_phase4_deployment_readiness.py`
   - plus iteration/feature-specific suites.
   Most tests hit a **running** backend, so start the server first. Run via:
   ```bash
   ./scripts/run_tests.sh [phase1|phase3|all]
   # or directly:
   cd backend && python -m pytest tests/test_phase1_functional.py -v
   ```
2. **`tests/`** (repo root) — broader `requests`-based integration tests
   (`test_medmatch_api.py`, `test_auth.py`, `test_recruiter_features.py`, …) that
   exercise the live API. `backend_test.py` at the root is a large end-to-end
   driver; results land in `backend_test_results.json` and `test_reports/`.

### CI (`.github/workflows/test.yml`) — the deployment gates

Runs on push/PR to `main`/`develop`. Spins up `mongo:7`, symlinks `/app`, seeds
admin/test users, boots `uvicorn` on :8001, then:
- **Phase 1 – Functional (G1)**
- **Phase 3 – Regression (G3)**
- **Phase 4 – Accessibility**: builds the frontend, serves it, runs an
  **axe / WCAG 2.2 AA** scan (`frontend/scripts/wcag_audit.cjs`). **Critical or
  serious violations fail the build** — accessibility is a hard gate.
- **Gate Summary** — fails if any gate failed.

CI massages `requirements.txt` into `requirements.ci.txt` to resolve known pin
conflicts (numpy vs `python-jobspy`, arch-specific wheels). If you add deps that
conflict, mirror that handling. `mobile-builds.yml` handles EAS mobile builds.

When changing frontend UI, **run/anticipate the axe scan** — new critical/serious
WCAG violations will block merge.

## Working agreements for changes

- Keep the `/api` prefix and the `routes/` + `server.py` registration pattern.
- Match existing style: FastAPI async routes with Motor; React function
  components with Tailwind + shadcn/ui; `@/`-aliased imports on the frontend.
- Prefer editing the correct domain module over creating parallel ones — this
  repo already has heavy duplication; add to what's there.
- Update or add tests in the relevant phase suite when changing backend behavior.
- Don't commit secrets. Note there are already some credential-like files under
  `mobile/` (iOS signing) and `backend/keys/`; leave them as-is and never add new
  secrets to source.

## Git / branch workflow

- Default branch: `main`. Development for this task happens on the designated
  feature branch; commit with clear messages and push with
  `git push -u origin <branch>`.
- Do **not** open a pull request unless explicitly asked.
