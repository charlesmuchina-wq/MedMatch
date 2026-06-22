# P2 — Build Tooling & Observability Decisions

**Date:** 2026-06-22 · **Status:** Sentry implemented (gated); Vite migration **recommended: defer**.

---

## A. Error Tracking & APM

### A1. In-house zero-cost tracker — IMPLEMENTED & VERIFIED (default, always-on)
No third-party service, no cost, no data leaves the stack (good for G5/CISO).
- Backend: `routes/observability.py` (`/api/observability/error` capture [auth optional];
  `/errors`, `/errors/stats`, PATCH/DELETE `/errors/{id}` [admin-only]) + an exception
  middleware in `server.py` that records unhandled 5xx into Mongo `error_logs`.
- Frontend: `utils/errorReporter.js` (global `window.onerror` + `unhandledrejection`
  handlers, posts to our endpoint) wired in `index.js`; Sentry `ErrorBoundary` also
  reports via `onError`.
- Admin UI: `pages/AdminErrorsPage.jsx` at `/admin/errors` (nav "Error Logs") — stats,
  source/status filters, stack traces, resolve/delete.
- Verified: frontend error capture, admin list/stats, 401 without auth, page renders.

### A2. Sentry SDK retained → point at free GlitchTip (optional, richer)
The wired `@sentry/react` + `sentry-sdk` code is **Sentry-protocol compatible**, so it
also works with **GlitchTip** (open-source, free self-host) by setting the DSN to a
GlitchTip instance. Sentry's own hosted plan is only free for a 14-day trial, so prefer
GlitchTip if you want session-replay/perf-tracing without ongoing cost. Set
`SENTRY_DSN` / `REACT_APP_SENTRY_DSN` to the GlitchTip DSN to activate; leave unset to
rely solely on the in-house tracker (A1).

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
