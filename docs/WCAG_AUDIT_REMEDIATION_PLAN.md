# WCAG 2.2 AA Accessibility Audit & Remediation Plan
## axe-core Automated Scan + Prioritised Backlog · AI KARAU + ENZI + MedMatch AI

**Current score**: ~25/100 · **Target**: WCAG 2.1 AA minimum (85+/100) · **Timeline**: Sprint 1 (2 weeks)
**Stack**: React 19 + Tailwind CSS 3.4 + Shadcn/UI · 92 pages · 161 components

## Current State Assessment

| Metric | Current | Target | Gap |
|---|---|---|---|
| Estimated WCAG score | ~25/100 | 85+/100 | 60 points |
| aria-label attributes | 14 across 324 files | Every interactive element | Critical |
| tabindex usage | 1 across codebase | All custom interactive elements | Critical |
| Skip-navigation links | 0 | Every page | Critical |
| Focus management | Not detected | All modals/dialogs | Critical |
| Screen reader testing | No evidence | VoiceOver · TalkBack · NVDA/JAWS | Critical |
| Colour contrast (4.5:1 AA) | Unknown | 100% of text | High |
| WCAG tests in G1 gate | 0 (ACC-01–05 not yet added) | 5 test cases | Must add |

## Remediation Backlog

### CRITICAL — Week 1 (App Store blocker)
| ID | WCAG | Rule | Description | Effort |
|---|---|---|---|---|
| **WCAG-01** | 4.1.2 Name, Role, Value | button-name, link-name, image-alt | aria-labels on icon-only buttons (KARAU controls, ENZI compose, sidebar, admin actions, job filters) | Low |
| **WCAG-02** | 2.4.1 Bypass Blocks | bypass | Skip-navigation link in root layout | Low |
| **WCAG-03** | 2.1.1 Keyboard | tabindex, focus-trap | tabIndex + onKeyDown on custom Dropdown, Modal, DatePicker, ParticipantTile, EmojiPicker, FilterChip | Medium |
| **WCAG-04** | 2.4.3 Focus Order | focus-trap, dialog-name | focus-trap-react on all modals + return-focus on close | Medium |
| **WCAG-05** | 1.1.1 Non-text Content | image-alt | Alt text on all `<img>` (informative for content, `alt=""` for decorative) | Low |

### HIGH — Week 1–2 (WCAG 2.1 AA required)
| ID | WCAG | Rule | Description | Effort |
|---|---|---|---|---|
| **WCAG-06** | 1.4.3 Contrast | color-contrast | Tailwind tokens: gray-400 → gray-600, blue-400 → blue-600 (4.5:1 AA) | Medium |
| **WCAG-07** | 1.3.1 Info & Relationships | label, input-button-name | Form `<label htmlFor>` + `aria-required` + `aria-invalid` + `aria-describedby` | Low |
| **WCAG-08** | 4.1.3 Status Messages | aria-live | `role="status"`/`role="alert"` on AI responses, toasts, validation, messenger log | Medium |
| **WCAG-09** | 1.3.1 Heading Structure | heading-order | Fix h1→h4 jumps; one h1 per page; nested h2/h3 | Low |

### MEDIUM — Week 2 (Complete AA coverage)
| ID | WCAG | Rule | Description | Effort |
|---|---|---|---|---|
| **WCAG-10** | 4.1.2 (KARAU) | toolbar, aria-pressed | Meeting `Controls.tsx` — toolbar role, aria-pressed for mute/video, aria-haspopup for share | Medium |
| **WCAG-11** | 4.1.3 (ENZI) | role=log, aria-live | Messenger thread `role="log"` + compose form labels + Enter-to-send hint | Medium |
| **WCAG-12** | 1.3.1 (MedMatch) | aria-required, aria-invalid, error-summary | Application/profile forms with error summary + per-field errors | High |

## G1 Gate Test Cases (ACC-01 → ACC-05)

| ID | Test | Pass Criterion |
|---|---|---|
| **ACC-01** | Keyboard navigation reachability | 0 `tabindex`/`scrollable-region-focusable` violations across `/`, `/login`, `/dashboard` |
| **ACC-02** | Screen-reader labels | 0 critical/serious `button-name`, `link-name`, `label`, `image-alt` on `/`, `/login`, `/dashboard`, `/jobs`, `/messages`, `/meetings` |
| **ACC-03** | Colour contrast 4.5:1 | 0 critical/serious `color-contrast` on `/`, `/login`, `/dashboard`, `/jobs` |
| **ACC-04** | Text resize 200% | 0 `meta-viewport`/`zoom-and-shrink-text` on `/dashboard` |
| **ACC-05** | Meeting controls | 0 critical/serious `button-name`, `aria-required-attr`, `aria-allowed-attr` on `/meetings/demo` |

**Target G1**: 59 existing + 5 ACC = **64/64 PASS**

## Sprint Exit Criteria
- [ ] axe-core: zero critical+serious violations across all 92 pages
- [ ] ACC-01–05 tests added and passing (64/64)
- [ ] VoiceOver (iOS), TalkBack (Android), NVDA (Windows), VoiceOver (macOS) manual passes signed off
- [ ] Colour contrast 4.5:1 verified
- [ ] Skip-nav present and functional on every page
- [ ] All modals: working focus trap + return-focus
- [ ] WCAG score re-estimated 85+/100

## Three Portal-Specific Patterns (verbatim from plan)
1. **KARAU controls**: `<div role="toolbar" aria-label="Meeting controls">` with `aria-pressed` toggle buttons + sr-only labels for icon buttons
2. **ENZI compose**: `<form aria-label="Send message">` + `role="log" aria-live="polite"` thread + `aria-describedby` Enter-to-send hint
3. **MedMatch forms**: `<form aria-labelledby>` + error-summary alert at top with anchor links to each invalid field

## Prerequisite & Unblocks
- **Prerequisite**: Regression test scope (`/app/docs/REGRESSION_TEST_SCOPE.md`) — ✅ PASSED 104/104 (Feb 8, 2026)
- **Unblocks**: iOS App Store submission · Android Play Store submission · G1 final close
