# P2 — Build Tooling & Observability Decisions

**Date:** 2026-06-22 · **Status:** Sentry implemented (gated); Vite migration **recommended: defer**.

---

## A. Sentry APM — IMPLEMENTED (gated, no-op until DSNs added)

**What was wired**
- Backend (`backend/server.py`): `sentry_sdk.init` with `FastApiIntegration` +
  `PyMongoIntegration`, gated on `SENTRY_DSN`. `traces_sample_rate`/`profiles_sample_rate`
  = 0.1 in production, 1.0 otherwise. Dependency: `sentry-sdk[fastapi,pymongo]` (in requirements.txt).
- Frontend (`frontend/src/index.js`): `Sentry.init` with browser tracing + session
  replay, gated on `REACT_APP_SENTRY_DSN`; `<App>` wrapped in `Sentry.ErrorBoundary`.
  Dependency: `@sentry/react`.

**To activate (ACTION — needs your DSNs)**
1. Create **two** Sentry projects: one **React** (frontend), one **FastAPI** (backend).
2. Add env vars:
   - `backend/.env`: `SENTRY_DSN=...` and `ENVIRONMENT=production` (on the deployed env).
   - `frontend/.env`: `REACT_APP_SENTRY_DSN=...` and `REACT_APP_ENV=production`.
3. In the Sentry React project → Security & Privacy → **Allowed Domains**: add the prod domain.
4. (CI) Upload source maps via `@sentry/webpack-plugin` so prod stack traces de-minify.
5. Ensure CORS exposes `sentry-trace` + `baggage` headers (current CORS allows all headers).

Until DSNs are set, Sentry is a **complete no-op** — zero runtime impact.

---

## B. CRA → Vite Migration — RECOMMEND DEFER

**Original drivers:** faster builds; eliminate transitive-dependency CVEs.

**Findings (why deferring is the right call now):**
1. **Emergent platform coupling.** The frontend runs on **craco** with the
   Emergent **`visual-edits`** plugin (`craco.config.js` →
   `plugins/visual-edits/dev-server-setup` + `babel-metadata-plugin`) and a
   health-check webpack plugin. Vite would **break the platform's visual-editing**
   dev tooling and the existing dev-server wiring.
2. **Protected env vars.** **135** source files use `process.env.REACT_APP_*`,
   including the **platform-protected `REACT_APP_BACKEND_URL`**. Vite expects
   `import.meta.env.VITE_*`; migrating means renaming protected vars (not allowed)
   or maintaining a shim across 135 files — high blast radius.
3. **Drivers already mitigated.** Build speed is acceptable (prod build ~47s on
   Node 20); the CVE driver was already addressed in **SEC-003** (65+ CVEs cleared)
   and Node pinned to 20. The marginal benefit no longer justifies the risk.
4. **Pipeline risk.** supervisor/preview/deploy expect `craco start`/`craco build`
   on port 3000; a bundler swap touches the whole run/deploy path.

**Recommendation:** keep CRA + craco for now. Revisit Vite only if/when we decouple
from the Emergent visual-edits tooling (e.g., self-hosted deploy) — at which point
do it behind a branch with a full regression pass (Phases 1/3/4 CI must stay green).

**If we still must reduce build/CVE surface without Vite:**
- Continue `yarn audit` + targeted upgrades (existing SEC-003 cadence).
- Enable webpack persistent caching via craco for faster rebuilds.
- Tree-shake/code-split heavy routes (already partially done via React.lazy where applicable).
