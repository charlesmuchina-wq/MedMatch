# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with Liquid Glass aesthetics and predictive design.

## What's Been Implemented

### Brand Rename: LUMI → ENZI (Completed - March 8, 2026)
- Renamed all user-visible text from "LUMI" to "ENZI" across 15+ files
- Updated translation files (en.json, sw.json) for ENZI branding
- Internal code (file names, API routes `/api/lumi/*`, CSS classes) kept unchanged
- URL route `/lumi` intentionally preserved for backward compatibility

### Invite System with Registration-Gated Security (Completed - March 8, 2026)
- **Email Invitations**: Send invites via Resend API with branded HTML template
- **Shareable Links**: Generate invite links with 7-day expiry
- **Social Sharing**: SMS, LinkedIn, Twitter/X share buttons
- **Registration Gate**: Invited users MUST register before accessing ENZI
- **Token Validation**: Expiry checking, already-used detection, invalid token handling
- **Invite History**: Track all sent invitations with status (pending/accepted)
- **Dashboard CTA**: Prominent "Invite to ENZI" tile on the command center
- **Sidebar Button**: "Invite to ENZI" in sidebar for quick access
- Backend: `/api/lumi/invite/send`, `/api/lumi/invite/link`, `/api/lumi/invite/validate/{token}`, `/api/lumi/invite/register`, `/api/lumi/invite/history`

### Domain-Based Company Discovery (Completed - March 8, 2026)
- Users with same email domain can find and message each other
- Free email domains (gmail, yahoo, etc.) excluded from company matching
- "Company" section in sidebar shows domain colleagues
- Backend: `/api/lumi/domain/colleagues`, `/api/lumi/domain/info`

### ENZI Splash Screen (Completed - March 8, 2026)
- Animated logo intro: icon scale-in → gradient text reveal → loading bar → fade out
- Shows once per session (sessionStorage gated)
- 2.2 second total animation duration

### Core Infrastructure (Previous Sessions)
- Full ENZI messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + Microsoft SSO (Azure AD) + email/password authentication
- Content moderation, compliance framework (HIPAA/GDPR/PIPL/APPI/UK DPA)
- Message retention & holds system, admin audit logs
- Dark/Light mode toggle, keyboard shortcuts
- AI Writing Assistant (Refine, Suggest, Translate, Voice) + Templates
- Smart Buckets (Urgent, Action Required, Meeting Requests)
- Channel invite system with approval flow
- MS Calendar status sync
- Predictive navigation with "Suggested for You"

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- Auth: Google SSO (Emergent) + Microsoft SSO (Azure AD) + email/password + invite registration

## Pending / Backlog
- **P1:** Task-Driven Side Layout with Smart Buckets as primary navigation
- **P2:** Full Predictive Zero-Click Navigation (reorder UI based on tracking data)
- **P2:** Behavioral Modeling & Context-Aware Triggers
- **P2:** Kinetic Typography & Micro-interactions
- **P2:** End-to-End Encryption (E2EE)
- **P2:** Live Payment Gateway (Stripe)
- **P2:** Passkeys & Biometric Authentication
- **P3:** Legacy Admin User Display fix

## Key DB Schema
- `enzi_invites`: `{ id, invited_email, invited_by, invited_by_name, invited_by_domain, message, status, type, expires_at, created_at }`
- `users` (updated): Added `domain`, `auth_method: "invite"`, `invited_by` fields for invite-registered users

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...
- Resend: Testing mode (sends only to charles.muchina@gmail.com)
