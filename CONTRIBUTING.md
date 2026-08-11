# Contributing — Developer Must-Do Checklist

Mandatory rules for changing this repo. These are the conventions CI and the
architecture actually enforce — skipping them breaks the build or the app. For
the wider picture (layout, how to run each app, gotchas) see
[`CLAUDE.md`](./CLAUDE.md) and [`docs/`](./docs).

> The root `README.md` is a placeholder and `ROADMAP.md` / `CHANGELOG.md`
> describe the KARAU/ENZI side only. **Treat `CLAUDE.md` + `docs/` as the source
> of truth**, not the README.

## Quick checklist (before you push)

- [ ] New endpoints are under the `/api` prefix and registered in `server.py`.
- [ ] Auth reuses `routes/auth.py` helpers; AI calls go through `LlmChat`.
- [ ] No new secrets committed; existing credential files left untouched.
- [ ] Backend behavior change → tests updated/added in the right phase suite.
- [ ] UI change → no new **critical/serious** WCAG 2.2 AA violations.
- [ ] Locale changes regenerated via scripts, not hand-edited.
- [ ] Work is on the designated feature branch; no PR unless explicitly asked.

---

## Backend

1. **Every endpoint must be mounted under `/api`.** The frontend and mobile
   apps always call `${BACKEND_URL}/api/...`.
2. **Adding an endpoint is two edits in `server.py`** — import the router, then
   add `app.include_router(<name>_router, prefix="/api")` — plus a
   `routes/<domain>.py` module exposing `router = APIRouter()`. Register in that
   one canonical place; do not create parallel wiring.
3. **Reuse auth.** Use `get_current_user(request)` / `require_auth(request)` and
   the membership/SSO helpers in `routes/auth.py`. Do not re-implement auth.
4. **All LLM access goes through `emergentintegrations`' `LlmChat` with
   `EMERGENT_LLM_KEY`.** Do not wire raw OpenAI/Gemini/etc. clients into new
   features.
5. **Keep the `/app/...` path convention.** Much of the code assumes the repo is
   mounted at `/app` (CI symlinks `/app` → the workspace). If you touch paths,
   keep `/app/...` or make them configurable — don't break the symlink.
6. **`util/` vs `utils/`** — both exist. `utils/` is the real package; check
   where a helper already lives before adding a new one.
7. **Prefer editing the correct domain module** over creating a new parallel
   one — this repo already has heavy duplication.

## Frontend

8. **Match the stack:** React function components, Tailwind + shadcn/ui, and
   `@/`-aliased imports (CRACO). 
9. **i18n:** regenerate locale JSON under `frontend/src/locales/` via
   `scripts/*translate*.py` / `generate_locales.py`. Don't hand-edit the ~50
   large locale files. (Tip: gating UI behind a flag avoids locale churn.)
10. **Accessibility is a hard gate.** Any UI change must not introduce new
    **critical or serious** WCAG 2.2 AA violations — they fail the build (see
    below). Label state with text, not color alone; give interactive/among
    elements accessible names.

## Testing & CI (must pass)

The pipeline (`.github/workflows/test.yml`) runs on push/PR to `main`/`develop`:

- **Phase 1 — Functional (G1)** and **Phase 3 — Regression (G3):** pytest
  against a running backend (`backend/tests/`).
- **Phase 4 — Accessibility:** builds the frontend and runs an axe / WCAG 2.2 AA
  scan. **Critical or serious violations fail the build.**
- **Gate Summary** fails if any gate failed.

Therefore:

11. **Update or add tests in the relevant phase suite** when you change backend
    behavior. Most tests hit a running server — start it first
    (`./scripts/run_tests.sh [phase1|phase3|all]`). DB-free unit tests are fine
    too (see `backend/tests/test_metrics_utils.py`).
12. **If you add dependencies that conflict, mirror the CI handling** that
    massages `requirements.txt` → `requirements.ci.txt` (numpy vs
    `python-jobspy`, arch-specific wheels).
13. **Anticipate the axe scan** on any UI work.

## Security & secrets

14. **Never commit secrets.** Existing credential-like files (`mobile/` iOS
    signing, `backend/keys/`) must be **left as-is** — never add new secrets to
    source.
15. **Don't over-claim in the UI.** Features backed by simulated or stubbed
    backends must be labeled (e.g. the `PreviewBadge`) or gated behind a feature
    flag (`frontend/src/config/features.js`) — not presented as production.

## Git / branch workflow

16. Default branch is `main`. **Develop on your designated feature branch**,
    commit with clear messages, and push with `git push -u origin <branch>`.
17. **Do not open a pull request unless explicitly asked.**
