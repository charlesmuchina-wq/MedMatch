# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool), "ENZI" (professional-grade AI messenger), and "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus -- a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React 19 + Tailwind CSS 3.4 + Shadcn/UI + react-markdown
- Backend: FastAPI 0.110.1 + MongoDB 7.0 + emergentintegrations
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (LiteLLM multi-provider routing)
- Payments: Stripe + PayPal (both in test/sandbox mode)
- Auth: Email/password, Google SSO, Microsoft SSO, Apple, GitHub, ORCID, Passkeys/WebAuthn
- Desktop: Electron (Win/Mac/Linux)
- Mobile: Expo SDK 54 + React Native 0.81 (iOS/Android)
- Microsoft: Teams App + Outlook Add-in (pending Azure AD)
- CI/CD: GitHub Actions + Local runner (Phase 1 + Phase 3 gates)

## Codebase Metrics
- Backend: 228 Python files, 96,680 LOC, 131 route modules, 71 services
- Frontend: 324 source files, 89,801 LOC, 92 pages, 161 components
- Database: 173 MongoDB collections
- Dependencies: 212 backend packages, 71 frontend packages

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| Phase 1 (iteration_216) | Functional Testing - Gate G1 | 59/59 PASS |
| Phase 2 (iteration_217) | Reliability Testing - Gate G2 | 31/31 PASS |
| Phase 3 (iteration_218) | Post-Reliability Regression - Gate G3 | 41/41 PASS |
| Phase 4 (iteration_219) | Deployment Readiness - Gate G4 | 54/54 PASS |
| Iteration 220 | CI/CD + Email + Refactoring + Triggers | 19/19 PASS |
| **Grand Total** | | **204/204 PASS** |

## All Features (Implemented & Tested)
1-29: See CHANGELOG.md for complete list

## Completed This Session (March 22, 2026)
- CI/CD Pipeline Fix v2: Resolved `numpy` version conflict (scipy vs python-jobspy), fixed shell escaping in seed script (heredoc), added system dependencies and diagnostic output
- System Requirements Audit Document: `/app/docs/SYSTEM_REQUIREMENTS_AUDIT.md`
- File Inventory Audit Document: `/app/docs/FILE_INVENTORY_AUDIT.md`
- Development Analyst Report: `/app/docs/DEVELOPMENT_ANALYST_REPORT_22_03_2026.md`

## Next Action Items (Detailed playbook: /app/docs/PRODUCTION_LAUNCH_PLAYBOOK.md)

### P0 — CI/CD Pipeline Verification
- User must "Save to GitHub" to trigger the fixed pipeline
- Pipeline includes system deps, sed-based numpy conflict resolution, heredoc seed script, diagnostic output

### Task 2 — Register Azure AD for Teams/Outlook
Prerequisites: Azure sub with Global Admin role, redirect URIs, tenant ID
- User status: "No to Azure / not sure"

### Task 3 — Obtain CISO Security Sign-Off (Gate G5)
Prerequisites: threat model, pen test report, SAST/DAST results, data flow diagrams, incident response plan

### Task 1 — Submit Platform Builds (blocked by Tasks 2 & 3)
Prerequisites: release branch, signing certs, store access

## Future/Backlog
- P1: Real-time Deployment Dashboard
- P2: Production Monitoring & CRS Dashboard
- P2: Chrome Extension
- P3: Enterprise Customer Onboarding

## Deployment Gate Status
| Gate | Status |
|------|--------|
| G1 Functional | PASSED |
| G2 Reliability | PASSED |
| G3 Regression | PASSED |
| G4 Platform Cert | Prerequisites Met (store submissions pending) |
| G5 Security | Prerequisites Met (CISO review pending) |

## Audit Documents
| Document | Path |
|----------|------|
| System Requirements | `/app/docs/SYSTEM_REQUIREMENTS_AUDIT.md` |
| File Inventory | `/app/docs/FILE_INVENTORY_AUDIT.md` |
| Technical SWOT Audit | `/app/docs/TECHNICAL_SWOT_AUDIT_22_03_2026.md` |
| Execution Framework | `/app/docs/EXECUTION_FRAMEWORK_22_03_2026.md` |
| RICE Cadence Roadmap | `/app/docs/CADENCE_ROADMAP_22_03_2026.md` |
| Development Analyst Report | `/app/docs/DEVELOPMENT_ANALYST_REPORT_22_03_2026.md` |
| Production Launch Playbook | `/app/docs/PRODUCTION_LAUNCH_PLAYBOOK.md` |
| Gap Assessment | `/app/docs/GAP_ASSESSMENT.md` |
| Testing Strategy | `/app/docs/TESTING_STRATEGY_RESULTS.md` |
| Deployment Readiness | `/app/docs/DEPLOYMENT_READINESS.md` |
