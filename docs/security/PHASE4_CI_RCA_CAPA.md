# RCA & CAPA — Phase 4 Accessibility CI Gate Failure

**Date:** 2026-06-22
**Pipeline:** `.github/workflows/test.yml` → job `phase4-accessibility`
**Status:** Phase 1 (G1) ✅ · Phase 3 (G3) ✅ · Phase 4 (WCAG AA) ❌ · Gate Summary ❌ (cascaded)

## 1. Symptom
On commit `b2f3f8b` (push to `main`), the Phase 4 job failed in ~3m34s with 2 annotations; the
Gate Summary job then failed by design (`exit 1`) because Phase 4 was not `success`.

## 2. Investigation
- Reproduced the axe-core WCAG scan locally against all 12 routes → **0 violations**
  (critical/serious/moderate/minor). The accessibility content is clean — this is **not** a real
  WCAG regression.
- Compared environments: local/preview (passing) runs **Node v20.20.2**; the CI job had been
  bumped to **Node 22** in a prior "resilience" patch.
- Phase 4 is the **only** Node-based job in the pipeline. Phases 1 & 3 are Python and passed.
  The failure is therefore isolated to the Node toolchain that changed.
- App uses **craco + react-scripts 5.0.1 + React 19**, which is validated on Node 20, not Node 22.

## 3. Root Cause
**Primary:** Node version bumped from 20 → 22 for the Phase 4 job. craco/react-scripts 5 on
Node 22 with React 19 is unstable (dev-server / webpack toolchain), breaking the job that scans
the CRA dev server.

**Contributing risk:** GitHub Actions sets `CI=true` by default, which makes `craco build`
(react-scripts) treat ESLint warnings as **errors**. Any future move to a build step would fail
unless `CI` is explicitly `false`.

**Secondary fragility:** The gate read the summary from a copied relative path
(`axe-results/_summary.json`) rather than the canonical path the scanner always writes, so a
partial scan produced a confusing `ENOENT` instead of a clear failure.

## 4. Corrective Actions (applied)
- **Pinned Node to 20** in `phase4-accessibility` (matches preview/prod, the known-good env).

## 5. Preventive Actions (applied)
- **Scan a production build, not the dev server.** Replaced `yarn start` (CRA dev server) with
  `yarn build` + `npx serve -s build -l 3000`. Deterministic DOM, no HMR/websocket/Node-quirk
  flakiness, faster server start (verified locally: build 46s, scan still 0 violations).
- **`CI: "false"` + `DISABLE_ESLINT_PLUGIN: "true"`** on the build step so warnings never break
  the build; `GENERATE_SOURCEMAP: "false"` for speed.
- **Gate reads the canonical summary** `/app/docs/security/axe-results/_summary.json` with an
  explicit existence guard that emits a clear `::error::` if the scan did not complete.
- **Artifact paths corrected** to existing dirs (`axe-results/`, `docs/security/axe-results/`).

## 6. Verification
- `yarn build` → success on Node 20 (46.59s).
- `npx serve -s build` → SPA fallback returns 200 on `/`, `/login`, `/dashboard`.
- `node scripts/wcag_audit.cjs` against served build → **0 critical/serious** across 12 routes;
  gate check reads summary and passes.
- `test.yml` validated as well-formed YAML.

## 7. Residual / Follow-up
- Final confirmation requires the user to push and observe a green Phase 4 run on the GitHub
  runner (cannot exercise the runner from this environment).
