# AI KARAU + ENZI + MedMatch AI — System Requirements Document
## For Third-Party Audit

**Document Version:** 1.0  
**Date:** March 22, 2026  
**Classification:** Confidential — Audit Use Only

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Requirements](#2-user-requirements)
3. [System Requirements](#3-system-requirements)
4. [Architecture Requirements](#4-architecture-requirements)
5. [Backend Requirements](#5-backend-requirements)
6. [Frontend Requirements](#6-frontend-requirements)
7. [Security Requirements](#7-security-requirements)
8. [Data Requirements](#8-data-requirements)
9. [Third-Party Integrations](#9-third-party-integrations)
10. [Testing & Quality Assurance](#10-testing--quality-assurance)
11. [File Inventory](#11-file-inventory)

---

## 1. Executive Summary

The AI Suite is a three-portal communication and recruitment platform:

| Portal | Purpose | Primary Users |
|--------|---------|---------------|
| **MedMatch AI** | AI-powered job seeking toolkit | Job seekers, recruiters, hiring managers |
| **AI KARAU** | Webinar and video conferencing platform | Meeting hosts, participants, organizations |
| **ENZI** | AI-driven professional messenger | Teams, organizations, enterprise users |

### Codebase Metrics

| Metric | Value |
|--------|-------|
| Backend Python files | 228 |
| Backend lines of code | 96,680 |
| Frontend source files | 324 |
| Frontend lines of code | 89,801 |
| API route modules | 131 |
| Service modules | 71 |
| Test files | 10 |
| Database collections | 173 |
| Frontend pages | 92 |
| Frontend components | 161 |
| Backend dependencies | 212 packages |
| Frontend dependencies | 59 + 12 dev packages |
| Markdown documentation files | 44 |

---

## 2. User Requirements

### 2.1 User Roles

| Role | Portal | Capabilities |
|------|--------|-------------|
| **Job Seeker** | MedMatch | Resume builder, job search, applications, interview prep, skill assessments, AI cover letters, smart apply |
| **Recruiter** | MedMatch | Job posting, ATS, blind screening, candidate scoring, talent CRM, team outreach, offer management |
| **Admin** | MedMatch | User management, AI compliance, data integrity, translation coverage, recruiter verification, audit reports |
| **Meeting Host** | KARAU | Create/schedule meetings, webinar management, recording, breakout rooms, polls, analytics |
| **Meeting Participant** | KARAU | Join meetings, video/audio/screen share, chat, reactions, whiteboard collaboration |
| **Guest** | KARAU | Join via link without account, OTP verification, QR code entry |
| **Messenger User** | ENZI | Channels, DMs, bots, file sharing, AI writing assistant, scheduled messages |
| **Organization Admin** | ENZI/KARAU | Org management, SSO configuration, domain setup, member management |

### 2.2 Functional Requirements by Portal

#### MedMatch AI
- FR-MM-01: User registration and multi-provider authentication
- FR-MM-02: Resume creation, editing, and PDF export
- FR-MM-03: Job search with semantic and geolocation filtering
- FR-MM-04: AI-powered job matching and callback prediction
- FR-MM-05: Smart Apply — automated job application with tailored cover letters
- FR-MM-06: Interview preparation with AI-generated questions
- FR-MM-07: Video interview practice with AI analysis
- FR-MM-08: Skill assessment with competency tracking
- FR-MM-09: Real-time speech-to-text for interview coaching
- FR-MM-10: Recruiter job posting and applicant tracking (ATS)
- FR-MM-11: Blind screening and DEI analytics
- FR-MM-12: Credential verification (PSV) and ID verification
- FR-MM-13: Employer reviews and company profiles
- FR-MM-14: Membership tiers with Stripe/PayPal payments
- FR-MM-15: Internationalization (50 languages)
- FR-MM-16: Push notifications (web + mobile)
- FR-MM-17: ORCID and LinkedIn OAuth integration
- FR-MM-18: Taxonomy explorer for career pathways

#### AI KARAU
- FR-AK-01: Video conferencing with WebRTC (peer-to-peer + TURN fallback)
- FR-AK-02: Webinar management (create, schedule, broadcast, record)
- FR-AK-03: Meeting recording and replay with Director Cuts
- FR-AK-04: Real-time AI transcription and live captions
- FR-AK-05: Breakout rooms/lounges with proximity audio
- FR-AK-06: Interactive polls and challenges (quiz, word cloud, rating)
- FR-AK-07: Gamification (emoji reactions, leaderboards)
- FR-AK-08: Screen sharing and collaborative whiteboard
- FR-AK-09: QR code touchless meeting entry
- FR-AK-10: Ghost booking prevention with idle detection
- FR-AK-11: Guest verification (OTP, email, biometric)
- FR-AK-12: Organization management with RBAC
- FR-AK-13: SSO configuration for enterprise tenants
- FR-AK-14: Hardware discovery (360 cameras, mic arrays, IoT devices)
- FR-AK-15: Spatial audio with HRTF panning
- FR-AK-16: AI-powered video framing and director mode
- FR-AK-17: IoT room environmental control
- FR-AK-18: SLAM spatial tracking and XR/Vision Pro support
- FR-AK-19: Adaptive beamforming audio
- FR-AK-20: Meeting intelligence (sentiment analysis, copilot)
- FR-AK-21: Calendar integration and scheduling
- FR-AK-22: Biometric feed verification (anti-deepfake)

#### ENZI Messenger
- FR-EN-01: Channel-based messaging (public, private, direct)
- FR-EN-02: End-to-end encryption (E2EE)
- FR-EN-03: Bot marketplace with specialized bots
- FR-EN-04: Bot chain builder (workflow automation)
- FR-EN-05: AI writing assistant with tone/style controls
- FR-EN-06: Auto-reply suggestions
- FR-EN-07: Scheduled messages
- FR-EN-08: File sharing and cloud storage integration
- FR-EN-09: Slash commands and keyboard shortcuts
- FR-EN-10: Thread-based conversations
- FR-EN-11: Behavioral predictions (churn, engagement)
- FR-EN-12: Team analytics dashboard
- FR-EN-13: Invite system with link and email
- FR-EN-14: Custom domain support
- FR-EN-15: Webhook templates for external integrations
- FR-EN-16: Meeting channel sync (KARAU meetings → ENZI channels)
- FR-EN-17: Notification preferences and quiet hours
- FR-EN-18: Sentiment analysis per conversation
- FR-EN-19: Premium packages with payment integration

### 2.3 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| **Availability** | 99.9% uptime target |
| **Latency** | API response < 500ms (p95) |
| **Concurrent Users** | Designed for 10,000+ concurrent connections |
| **Data Retention** | User data retained until deletion request |
| **Browser Support** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| **Mobile Support** | iOS 15+ (Expo/Capacitor), Android 10+ (Expo) |
| **Desktop Support** | Windows 10+, macOS 12+, Linux (Electron) |
| **Accessibility** | WCAG 2.1 AA compliance target |
| **Internationalization** | 50 languages with AI translation pipeline |

---

## 3. System Requirements

### 3.1 Runtime Environment

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11.15 | Backend runtime |
| **Node.js** | 20.20.2 | Frontend build and dev server |
| **MongoDB** | 7.0.32 | Primary database |
| **Redis** | 7.x | Caching layer (optional) |
| **Yarn** | 1.22.22 | Frontend package manager |
| **npm** | 10.8.2 | Available but Yarn preferred |

### 3.2 Operating System

| Environment | OS | Architecture |
|-------------|-----|-------------|
| Development | Debian 12 (Bookworm) | aarch64 (ARM64) |
| CI/CD | Ubuntu Latest (GitHub Actions) | x86_64 |
| Production | Kubernetes (cloud-agnostic) | x86_64 |

### 3.3 System Dependencies (apt packages)

Required for full backend functionality:

```
libcairo2-dev          # PDF/image generation (weasyprint)
libpango1.0-dev        # Text rendering (weasyprint)
libgdk-pixbuf-2.0-dev  # Image processing (weasyprint)
libffi-dev             # Foreign function interface
shared-mime-info       # MIME type detection
poppler-utils          # PDF processing (pdf2image)
ffmpeg                 # Video/audio processing (moviepy, edge-tts)
libjq-dev              # JSON processing (jq Python package)
pkg-config             # Build tool for native extensions
```

### 3.4 Network Requirements

| Service | Port | Protocol | Direction |
|---------|------|----------|-----------|
| Backend API | 8001 | HTTP/HTTPS | Inbound |
| Frontend Dev | 3000 | HTTP | Inbound |
| MongoDB | 27017 | TCP | Internal |
| Redis | 6379 | TCP | Internal |
| WebSocket | 8001 | WS/WSS | Bidirectional |
| WebRTC TURN | 443 | UDP/TCP | Outbound (Xirsys) |

### 3.5 Environment Variables

#### Backend (54 keys)

| Category | Variables |
|----------|-----------|
| **Database** | MONGO_URL, DB_NAME |
| **Auth/JWT** | JWT_SECRET_KEY |
| **AI/LLM** | EMERGENT_LLM_KEY |
| **Google** | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_API_KEY, GOOGLE_CSE_ID, GOOGLE_PROJECT_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL |
| **Microsoft/Azure** | AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID |
| **Apple** | APPLE_KEY_ID, APPLE_PRIVATE_KEY_PATH, APPLE_SERVICE_ID, APPLE_TEAM_ID |
| **LinkedIn** | LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI |
| **ORCID** | ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, ORCID_ENVIRONMENT, ORCID_REDIRECT_URI |
| **Payments** | STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET, PAYPAL_CLIENT_ID, PAYPAL_SECRET |
| **Email** | RESEND_API_KEY, SENDER_EMAIL, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, ALERT_RECIPIENT |
| **Push** | VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY |
| **Cloud Storage** | DROPBOX_ACCESS_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REDIRECT_URI, ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_REDIRECT_URI |
| **Media/Video** | D_ID_API_KEY, XIRSYS_IDENT, XIRSYS_SECRET, XIRSYS_CHANNEL |
| **WebAuthn** | WEBAUTHN_RP_ID, WEBAUTHN_RP_NAME |
| **App** | REACT_APP_BACKEND_URL, CORS_ORIGINS |

#### Frontend (7 keys)

| Variable | Purpose |
|----------|---------|
| REACT_APP_BACKEND_URL | API base URL |
| REACT_APP_GOOGLE_CLIENT_ID | Google OAuth |
| REACT_APP_GOOGLE_API_KEY | Google services |
| REACT_APP_STRIPE_PUBLISHABLE_KEY | Stripe payments |
| REACT_APP_VAPID_PUBLIC_KEY | Web push notifications |
| ENABLE_HEALTH_CHECK | Feature flag |
| WDS_SOCKET_PORT | Dev server WebSocket |

---

## 4. Architecture Requirements

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  Web/PWA │  │ Desktop  │  │ Mobile (iOS/Droid)│  │
│  │ React 19 │  │ Electron │  │ Expo SDK 54       │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       └──────────────┼─────────────────┘              │
│                      │ HTTPS + WSS                    │
├──────────────────────┼────────────────────────────────┤
│              Kubernetes Ingress                        │
│         /api/* → :8001  |  /* → :3000                │
├──────────────────────┼────────────────────────────────┤
│                 Backend Layer                          │
│  ┌────────────────────────────────────────────────┐  │
│  │            FastAPI (server.py)                  │  │
│  │  ┌────────┐ ┌──────────┐ ┌─────────────────┐  │  │
│  │  │131 Route│ │71 Service│ │ AI Supervisor   │  │  │
│  │  │ Modules │ │ Modules  │ │ Dragon Scheduler│  │  │
│  │  │         │ │          │ │ Rate Limiter    │  │  │
│  │  └────────┘ └──────────┘ └─────────────────┘  │  │
│  └───────────────────┬────────────────────────────┘  │
│                      │                                │
├──────────────────────┼────────────────────────────────┤
│                 Data Layer                             │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  MongoDB 7.0 │  │ Redis 7.x │  │ In-Memory    │  │
│  │ 173 collections│ │  Cache    │  │ FastAPI Cache│  │
│  └──────────────┘  └───────────┘  └──────────────┘  │
├───────────────────────────────────────────────────────┤
│              External Services                         │
│  OpenAI · Gemini · Claude · Stripe · PayPal ·         │
│  Resend · Xirsys · ORCID · LinkedIn · Google ·        │
│  Microsoft Graph · Apple · Dropbox · OneDrive          │
└───────────────────────────────────────────────────────┘
```

### 4.2 Backend Architecture Pattern

- **Framework:** FastAPI with async I/O (Motor for MongoDB)
- **Pattern:** Modular router architecture — each feature domain has its own route file
- **Auth:** JWT tokens (python-jose) with bcrypt password hashing
- **Caching:** FastAPI-Cache2 with in-memory backend (prefix: `medmatch-cache`)
- **Rate Limiting:** Custom global rate limiter (SlowAPI)
- **Background Jobs:** APScheduler (Dragon Scheduler) for recurring tasks
- **WebSocket:** Socket.IO via python-socketio at `/api/lumi/ws/{user_id}`
- **AI Orchestration:** LiteLLM for multi-provider LLM routing (OpenAI, Gemini, Claude)
- **ML Pipeline:** scikit-learn models with custom training/prediction pipeline

### 4.3 Frontend Architecture Pattern

- **Framework:** React 19 with Create React App (via Craco)
- **Styling:** Tailwind CSS 3.4 + Shadcn/UI component library
- **Routing:** React Router v7 with nested routes
- **State:** React hooks (useState, useEffect, useContext) — no external state manager
- **HTTP Client:** Axios with REACT_APP_BACKEND_URL base
- **Charts:** Recharts for data visualization
- **Forms:** React Hook Form + Zod validation
- **Markdown:** react-markdown + remark-gfm
- **Icons:** Lucide React

### 4.4 Multi-Platform Architecture

| Platform | Technology | Status |
|----------|-----------|--------|
| Web (PWA) | React 19 + service worker | Implemented |
| Desktop (Windows) | Electron | Scaffolded |
| Desktop (macOS) | Electron | Scaffolded |
| Desktop (Linux) | Electron | Scaffolded |
| Mobile (iOS) | Expo SDK 54 + React Native | Scaffolded |
| Mobile (Android) | Expo SDK 54 + React Native | Scaffolded |
| Teams App | Microsoft Graph API + MSAL | Partially implemented |
| Outlook Add-in | Microsoft Graph API | Partially implemented |

---

## 5. Backend Requirements

### 5.1 Dependencies by Category

#### Web Framework
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.110.1 | ASGI web framework |
| uvicorn | 0.25.0 | ASGI server |
| starlette | 0.37.2 | HTTP toolkit (FastAPI dependency) |
| python-multipart | 0.0.21 | Form data parsing |
| httpx | 0.28.1 | Async HTTP client |

#### Database
| Package | Version | Purpose |
|---------|---------|---------|
| motor | 3.3.1 | Async MongoDB driver |
| pymongo | 4.5.0 | Sync MongoDB driver |
| redis | 7.1.0 | Redis client |

#### Authentication & Security
| Package | Version | Purpose |
|---------|---------|---------|
| python-jose | 3.5.0 | JWT token handling |
| PyJWT | 2.10.1 | JWT alternative |
| passlib | 1.7.4 | Password hashing |
| bcrypt | 4.1.3 | Bcrypt hashing |
| webauthn | 2.7.0 | FIDO2/WebAuthn passkeys |
| msal | 1.35.1 | Microsoft auth library |
| pyotp | 2.9.0 | TOTP/HOTP for 2FA |
| cbor2 | 5.8.0 | CBOR encoding (WebAuthn) |
| cryptography | 46.0.3 | Cryptographic primitives |
| pyOpenSSL | 25.3.0 | TLS/SSL toolkit |

#### AI/ML
| Package | Version | Purpose |
|---------|---------|---------|
| openai | 1.99.9 | OpenAI API client |
| litellm | 1.80.0 | Multi-LLM routing proxy |
| google-genai | 1.57.0 | Google Gemini API client |
| scikit-learn | 1.8.0 | ML model training/prediction |
| numpy | 2.4.1 | Numerical computing |
| pandas | 2.3.3 | Data analysis |
| emergentintegrations | 0.1.1 | Emergent LLM key management |

#### Payments
| Package | Version | Purpose |
|---------|---------|---------|
| stripe | 14.1.0 | Stripe payments |
| paypalrestsdk | 1.13.3 | PayPal payments (deprecated SDK) |

#### Email & Communications
| Package | Version | Purpose |
|---------|---------|---------|
| resend | 2.21.0 | Transactional email |
| pywebpush | 2.2.0 | Web push notifications |
| py-vapid | 1.9.4 | VAPID key management |
| python-socketio | 5.16.0 | WebSocket (Socket.IO) |

#### Media Processing
| Package | Version | Purpose |
|---------|---------|---------|
| moviepy | 2.2.1 | Video editing |
| pillow | 11.3.0 | Image processing |
| imageio | 2.37.2 | Image I/O |
| imageio-ffmpeg | 0.6.0 | FFmpeg binding |
| reportlab | 4.4.9 | PDF generation |
| weasyprint | 68.1 | HTML-to-PDF |
| qrcode | 8.2 | QR code generation |

#### NLP & Text
| Package | Version | Purpose |
|---------|---------|---------|
| beautifulsoup4 | 4.14.3 | HTML parsing |
| lxml | 6.0.2 | XML/HTML processing |
| markdownify | 0.13.1 | HTML-to-Markdown |
| edge-tts | 7.2.7 | Microsoft Edge text-to-speech |

#### Job Search
| Package | Version | Purpose |
|---------|---------|---------|
| python-jobspy | 1.1.82 | Multi-site job scraping |
| tls-client | 1.0.1 | TLS fingerprint client |

#### Testing
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 9.0.2 | Test framework |
| pytest-asyncio | 1.3.0 | Async test support |

**Total backend packages: 212**

### 5.2 API Route Modules (131 files)

Organized by domain:

**Authentication & Users (4 modules)**
- `auth.py` (1,544 LOC) — Login, register, OAuth, passkeys, SSO
- `orcid_oauth.py` (429 LOC) — ORCID researcher auth
- `linkedin.py` (271 LOC) — LinkedIn OAuth
- `biometric.py` (588 LOC) — Biometric authentication

**Jobs & Recruitment (15 modules)**
- `jobs.py` (1,158 LOC) — Job CRUD, search, matching
- `smart_apply.py` (298 LOC) — Automated job applications
- `recruiter.py` (551 LOC) — Recruiter features
- `recruiter_rbac.py` (913 LOC) — Role-based access control
- `ats.py` (664 LOC) — Applicant tracking system
- `resume.py` (355 LOC) — Resume management
- `interview.py` (507 LOC) — Interview preparation
- `interview_calendar.py` (722 LOC) — Interview scheduling
- `skills.py` (1,501 LOC) — Skill assessments
- `mutual_match.py` (589 LOC) — Mutual matching
- `talent_crm.py` (372 LOC) — Talent CRM
- `talent_tools.py` (220 LOC) — Talent tools
- `taxonomy.py` (550 LOC) — Career taxonomy
- `employer_reviews.py` (430 LOC) — Company reviews
- `companies.py` (333 LOC) — Company profiles

**AI & Intelligence (8 modules)**
- `ai_features.py` (1,061 LOC) — Core AI features
- `ai_productivity.py` (1,434 LOC) — AI productivity tools
- `ai_qa.py` (490 LOC) — AI quality assurance
- `ai_talent.py` (277 LOC) — AI talent matching
- `ai_compliance.py` (190 LOC) — AI compliance monitoring
- `lumi_ai.py` (224 LOC) — ENZI AI features
- `enzi_ai.py` (111 LOC) — ENZI AI assistant
- `karau_ai.py` (189 LOC) — KARAU AI features

**KARAU Meeting Platform (28 modules)**
- `karau_meet.py` (1,227 LOC) — Core meeting management
- `karau_webinar.py` (1,077 LOC) — Webinar management
- `karau_extended.py` (727 LOC) — Extended meeting features
- `karau_replay.py` (582 LOC) — Meeting replay/director cuts
- `karau_organizations.py` (963 LOC) — Organization management
- `karau_collaboration.py` (417 LOC) — Collaborative tools
- `karau_calendar.py` (367 LOC) — Calendar integration
- `karau_security.py` (323 LOC) — Security features
- `karau_scheduling.py` (301 LOC) — Meeting scheduling
- `karau_sso.py` (339 LOC) — Enterprise SSO
- `karau_recordings.py` (315 LOC) — Recording management
- `karau_guest_verification.py` (305 LOC) — Guest verification
- `karau_intelligence.py` (297 LOC) — Meeting intelligence
- `karau_simulation.py` (287 LOC) — Simulation features
- `karau_slam_spatial.py` (284 LOC) — SLAM spatial tracking
- `karau_beamforming.py` (285 LOC) — Audio beamforming
- `karau_polls_challenges.py` (259 LOC) — Polls and challenges
- `karau_iot_control.py` (247 LOC) — IoT room control
- `karau_enhanced_sentiment.py` (243 LOC) — Sentiment analysis
- `karau_breakout_lounges.py` (219 LOC) — Breakout rooms
- `karau_accessibility.py` (219 LOC) — Accessibility
- `karau_webxr.py` (208 LOC) — XR/Vision Pro support
- `karau_hardware_discovery.py` (197 LOC) — Hardware detection
- `karau_biometric_verify.py` (193 LOC) — Biometric verification
- `karau_analytics.py` (341 LOC) — Meeting analytics
- `karau_gamification.py` (161 LOC) — Gamification
- `karau_ghost_booking.py` (156 LOC) — Ghost booking prevention
- `karau_director.py` (131 LOC) — Director mode
- `karau_qr_entry.py` (135 LOC) — QR code entry
- `karau_webrtc.py` (137 LOC) — WebRTC signaling
- `karau_sharing.py` (115 LOC) — Meeting sharing

**ENZI Messenger (12 modules)**
- `lumi_messenger.py` (2,466 LOC) — Core messenger
- `enzi_bots.py` (880 LOC) — Bot marketplace
- `enzi_automation.py` (278 LOC) — Automation rules
- `enzi_invites.py` (271 LOC) — Invite system
- `enzi_meetings.py` (164 LOC) — Meeting integration
- `enzi_payments.py` (153 LOC) — Premium packages
- `enzi_channel_templates.py` (130 LOC) — Channel templates
- `enzi_notifications.py` (120 LOC) — Notification prefs
- `enzi_webhook_templates.py` (115 LOC) — Webhook templates
- `enzi_sentiment.py` (100 LOC) — Sentiment analysis
- `enzi_domain.py` (90 LOC) — Custom domains
- `lumi_predict.py` (154 LOC) — Behavioral predictions
- `lumi_buckets.py` (211 LOC) — Message buckets
- `lumi_calendar.py` (187 LOC) — Calendar integration
- `lumi_templates.py` (129 LOC) — Message templates
- `lumi_files.py` (139 LOC) — File sharing

**Compliance & Security (8 modules)**
- `psv.py` (1,105 LOC) — Professional source verification
- `privacy.py` (687 LOC) — Privacy management (GDPR)
- `admin_audit.py` (685 LOC) — Admin audit logging
- `credentials.py` (926 LOC) — Credential management
- `audit_reports.py` (524 LOC) — Audit report generation
- `persona_verification.py` (499 LOC) — Persona verification
- `id_verification.py` (322 LOC) — ID verification
- `global_compliance.py` (158 LOC) — Global compliance
- `compliance_alerts.py` (298 LOC) — Compliance alerts
- `data_integrity.py` (212 LOC) — Data integrity checks

**Analytics & ML (8 modules)**
- `analytics.py` (253 LOC) — Core analytics
- `analytics_funnel.py` (339 LOC) — Funnel analytics
- `ml_data.py` (266 LOC) — ML data pipeline
- `ml_model.py` (149 LOC) — ML model management
- `ml_predictor.py` (172 LOC) — ML predictions
- `behavioral.py` (298 LOC) — Behavioral analysis
- `production_metrics.py` (300 LOC) — Production metrics
- `search_engine.py` (280 LOC) — Semantic search

**Translation & i18n (2 modules)**
- `translation.py` (1,957 LOC) — Translation management
- `translation_qa.py` (990 LOC) — Translation quality assurance

**Media & Content (6 modules)**
- `video_analysis.py` (572 LOC) — Video analysis
- `video_interview.py` (323 LOC) — Video interview
- `video_translation.py` (294 LOC) — Video translation
- `video_assets.py` (217 LOC) — Video asset management
- `tutorials.py` (988 LOC) — Video tutorials
- `avatar.py` (127 LOC) — Avatar generation

**Other (12 modules)**
- `advanced_features.py` (590 LOC) — Advanced features
- `meeting_notes.py` (605 LOC) — Meeting notes
- `meeting_channel_sync.py` (420 LOC) — Meeting-channel sync
- `meeting_intelligence.py` (549 LOC) — Meeting intelligence
- `meeting_infrastructure.py` (188 LOC) — Meeting infrastructure
- `payments.py` (801 LOC) — Payment processing
- `cloud.py` (549 LOC) — Cloud storage
- `feedback.py` (333 LOC) — Feedback system
- `push.py` (324 LOC) — Push notifications
- `push_notifications.py` (318 LOC) — Push notification management
- `webpush.py` (677 LOC) — Web push
- `dragon.py` (682 LOC) — Dragon scheduler
- `dragon_automator.py` (1,352 LOC) — Dragon automation
- `platform_features.py` (243 LOC) — Platform features
- `portal_access.py` (253 LOC) — Portal access control
- `e2ee.py` (146 LOC) — End-to-end encryption
- `email_settings.py` (118 LOC) — Email configuration
- `notifications.py` (160 LOC) — Notification management
- `messages.py` (166 LOC) — Legacy messages
- `batch.py` (144 LOC) — Batch operations
- `autofill.py` (402 LOC) — Resume autofill
- `realtime_stt.py` (417 LOC) — Real-time STT
- `qa_practice.py` (708 LOC) — QA practice
- `digest.py` (321 LOC) — Email digests
- `scheduling.py` (540 LOC) — General scheduling
- `geolocation.py` (219 LOC) — Geolocation
- `job_verification.py` (109 LOC) — Job verification
- `dei_analytics.py` (96 LOC) — DEI analytics
- `enterprise_api.py` (846 LOC) — Enterprise API

### 5.3 Service Modules (71 files)

| Service | LOC | Purpose |
|---------|-----|---------|
| tutorial_subtitles.py | 1,663 | Video subtitle generation |
| dragon_scheduler.py | 1,012 | Background job scheduling |
| audit_reports.py | 996 | Audit report generation |
| edge_tts_service.py | 969 | Text-to-speech |
| data_integrity_service.py | 868 | Data integrity checks |
| global_compliance_service.py | 859 | Global compliance |
| karau_meet/meeting_service.py | 817 | Meeting management |
| pdf_export.py | 730 | PDF export |
| psv_service.py | 724 | Professional verification |
| karau_meet/webrtc_signaling.py | 692 | WebRTC signaling |
| karau_meet/security_service.py | 652 | Meeting security |
| capa_service.py | 635 | CAPA management |
| ai_supervisor.py | 620 | AI orchestration |
| ai_qa/core_service.py | 612 | AI QA core |
| video_asset_manager.py | 597 | Video asset management |
| ai_compliance_service.py | 585 | AI compliance |
| ml_issue_predictor.py | 559 | ML issue prediction |
| translation_qa.py | 556 | Translation QA |
| search_engine.py | 529 | Semantic search |
| karau_meet/ai_transcription_service.py | 504 | AI transcription |
| email_service.py | 499 | Email service |
| trust_score.py | 495 | Trust score calculation |
| ml_data_collector.py | 491 | ML data collection |
| ml_model_trainer.py | 482 | ML model training |
| question_bank.py | 475 | Interview questions |
| did_avatar_service.py | 471 | Avatar generation |
| ai_qa/oversight_service.py | 471 | AI oversight |
| geolocation.py | 461 | Geolocation |
| smart_notifications.py | 457 | Smart notifications |
| karau_meet/scheduling_service.py | 445 | Meeting scheduling |
| career_pivot.py | 441 | Career pivot analysis |
| karau_meet/collaboration_service.py | 429 | Collaboration |
| web_job_crawler.py | 408 | Web job crawling |
| ai_qa/transparency_service.py | 400 | AI transparency |
| video_with_highlights.py | 397 | Video highlights |
| gual_integration.py | 387 | GUAL integration |
| global_rate_limiter.py | 379 | Rate limiting |
| taxonomy.py | 571 | Taxonomy engine |
| job_sources.py | 897 | Job source aggregation |
| job_liveness.py | 407 | Job liveness monitoring |
| (+ 31 more service files) | | |

### 5.4 Test Files (10 files)

| Test File | LOC | Coverage |
|-----------|-----|----------|
| test_phase1_functional.py | 839 | 59 tests — Core functional (Gate G1) |
| test_phase3_regression.py | 826 | 41 tests — Regression (Gate G3) |
| test_phase2_reliability.py | 618 | 31 tests — Reliability (Gate G2) |
| test_phase4_deployment_readiness.py | 488 | 54 tests — Deployment readiness (Gate G4) |
| test_iteration220_features.py | 417 | 19 tests — CI/CD + features |
| test_iteration_210.py | 318 | Feature iteration tests |
| test_smart_apply_iteration215.py | 258 | Smart Apply feature tests |
| test_smart_apply_iteration214.py | 207 | Smart Apply v1 tests |
| test_phases_2_4.py | 144 | Combined phase tests |
| test_passkeys_iteration213.py | 117 | Passkey/WebAuthn tests |

**Grand Total: 204/204 tests passing**

---

## 6. Frontend Requirements

### 6.1 Dependencies

#### Core Framework
| Package | Version | Purpose |
|---------|---------|---------|
| react | ^19.0.0 | UI framework |
| react-dom | ^19.0.0 | DOM rendering |
| react-router-dom | ^7.5.1 | Client-side routing |
| react-scripts | 5.0.1 | CRA build toolchain |
| @craco/craco | ^7.1.0 | CRA configuration override |

#### UI Components & Styling
| Package | Version | Purpose |
|---------|---------|---------|
| tailwindcss | ^3.4.17 | Utility-first CSS |
| tailwindcss-animate | ^1.0.7 | Animation utilities |
| class-variance-authority | ^0.7.1 | Component variants |
| clsx | ^2.1.1 | Conditional classnames |
| tailwind-merge | ^3.2.0 | Tailwind class merging |
| lucide-react | ^0.507.0 | Icon library |
| sonner | ^2.0.3 | Toast notifications |
| vaul | ^1.1.2 | Drawer component |
| cmdk | ^1.1.1 | Command palette |
| @radix-ui/* | Various | 28 Radix UI primitives |

#### Data & Forms
| Package | Version | Purpose |
|---------|---------|---------|
| axios | ^1.8.4 | HTTP client |
| react-hook-form | ^7.56.2 | Form management |
| @hookform/resolvers | ^5.0.1 | Form validation resolvers |
| zod | ^3.24.4 | Schema validation |
| recharts | ^3.6.0 | Data visualization |

#### Content & Media
| Package | Version | Purpose |
|---------|---------|---------|
| react-markdown | ^10.1.0 | Markdown rendering |
| remark-gfm | ^4.0.1 | GitHub-flavored Markdown |
| react-syntax-highlighter | ^16.1.1 | Code highlighting |
| jspdf | ^4.0.0 | PDF generation |
| jspdf-autotable | ^5.0.7 | PDF tables |
| react-dropzone | ^14.3.8 | File uploads |

#### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| date-fns | ^4.1.0 | Date manipulation |
| idb | ^8.0.3 | IndexedDB wrapper (offline) |
| next-themes | ^0.4.6 | Dark/light mode |
| embla-carousel-react | ^8.6.0 | Carousel |
| input-otp | ^1.4.2 | OTP input |
| react-resizable-panels | ^3.0.1 | Resizable layouts |
| @shiguredo/rnnoise-wasm | ^2025.1.5 | Noise cancellation |

### 6.2 Pages (92 page components)

**MedMatch Pages (68)**
- Dashboard, LoginPage, ResumePage, ResumeProfilesPage, JobSearchPage
- SavedJobsPage, ApplicationsPage, CoverLetterPage, InterviewPrepPage
- QAPracticePage, VoiceCoachPage, VideoInterviewPage, SkillAssessmentsPage
- SmartApplyPage, MembershipPage, CompaniesPage, CompanyProfilePage
- MessagesPage, NotificationsPage, AnalyticsDashboard, AnalyticsFunnelPage
- SalaryInsightsPage, JobAlertsPage, LocationSettingsPage, PrivacySettingsPage
- IDVerificationPage, CredentialsPage, PSVVerificationPage
- RecruiterDashboard, RecruiterJobsPage, RecruiterVerificationPage
- ApplicantTracker, BlindScreeningDashboard, ATSManagementPage
- CandidateScoringPage, CandidateSearch, ContactRequestScreen
- DEIAnalyticsPage, HiringMetricsPage, TalentCRMPage, TeamOutreachPage
- OfferManagementPage, JobDescriptionGenerator, ReportBuilderPage
- AdminDashboard, AdminAICompliancePage, AdminDataIntegrityPage
- AdminRecruiterVerificationPage, AdminReviewModerationPage
- AdminTranslationCoveragePage, GlobalCompliancePage
- DragonAutomatorPage, EnterpriseAPIPage, InterviewCalendarPage
- InterviewSchedulingPage, MeetingNotesPage, PlatformDownloadsPage
- PlatformSettingsPage, ProductionMetricsPage, PublicApplicationPage
- RealTimeSTTPage, SemanticSearchPage, SuccessPredictorPage
- TaxonomyExplorerPage, TrackApplicationPage, TranslationAnalyticsPage
- VideoTutorialsPage, WebinarPage, PortalSelector

**KARAU Pages (14)**
- KarauMeetPortal, KarauMeetDashboard, KarauMeetLanding, KarauMeetLogin
- KarauMeetGuidePage, KarauSettingsPage, KarauRecordingsPage
- WebinarPage, WebinarManagementPage, WebinarLiveRoom, WebinarAnalyticsPage
- MeetingReplayPage, GuestJoinPage
- Settings tabs: AccessibilityTab, CalendarTab, ComplianceTab, EmailSettingsTab, SecurityTab, SSOTab, TSRTab, WebhookTab

**ENZI Pages (2 — integrated into LumiMessenger)**
- LumiMessenger (main messenger container)
- PortalSelector (portal switching)

### 6.3 Custom Hooks (11)

| Hook | Purpose |
|------|---------|
| useWebRTC | WebRTC connection management |
| useWebRTCService | WebRTC service abstraction |
| useSpatialAudio | Spatial audio with HRTF |
| useSpeakerDetection | Active speaker detection |
| useNoiseCancellation | RNNoise WASM noise cancellation |
| useLiveTranscription | Real-time transcription |
| useDirectorMode | AI director camera switching |
| useGhostBooking | Ghost booking prevention |
| useWebinarActions | Webinar action handlers |
| useEnziData | ENZI messenger data management |
| use-toast | Toast notification management |

### 6.4 Shadcn/UI Components (pre-installed)

Located at `/app/frontend/src/components/ui/`:
accordion, alert-dialog, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, chart, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input, input-otp, label, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, switch, table, tabs, textarea, toast, toaster, toggle, toggle-group, tooltip

---

## 7. Security Requirements

### 7.1 Authentication Methods

| Method | Implementation | Status |
|--------|---------------|--------|
| Email/Password | bcrypt hashing + JWT | Active |
| Google OAuth | Emergent-managed | Active |
| Microsoft OAuth | MSAL + Azure AD | Partial (needs Azure AD registration) |
| Apple Sign-In | Apple authentication services | Implemented |
| GitHub OAuth | GitHub OAuth Apps | Implemented |
| ORCID OAuth | ORCID OAuth2 | Implemented |
| LinkedIn OAuth | LinkedIn OAuth2 | Implemented |
| Passkeys/WebAuthn | FIDO2 compliant | Implemented |
| Biometric | Device-native biometric | Implemented |

### 7.2 Data Protection

| Control | Implementation |
|---------|---------------|
| Encryption in transit | HTTPS/TLS enforced |
| Encryption at rest | MongoDB encryption at rest (Atlas) |
| End-to-end encryption | E2EE for ENZI messenger (client-side key exchange) |
| Password storage | bcrypt with salt rounds |
| JWT tokens | Signed with configurable secret, expiry enforced |
| Rate limiting | Global rate limiter + per-endpoint limits (SlowAPI) |
| CORS | Configurable origin whitelist |
| Input validation | Pydantic models for all API inputs |
| XSS prevention | React auto-escaping + CSP headers |
| CSRF protection | SameSite cookies + CORS |

### 7.3 Compliance Features

| Feature | Module |
|---------|--------|
| GDPR privacy controls | privacy.py |
| Audit logging | admin_audit.py |
| Data integrity monitoring | data_integrity.py |
| AI compliance monitoring | ai_compliance.py |
| Bias detection | ai_qa/ (4 modules) |
| PSV credential verification | psv.py |
| ID verification | id_verification.py |
| Compliance alerts | compliance_alerts.py |
| Global compliance | global_compliance.py |

---

## 8. Data Requirements

### 8.1 Database: MongoDB 7.0

- **Database name:** `MedMatch`
- **Total collections:** 173
- **Connection:** Async via Motor (pymongo for sync operations)
- **Connection pooling:** Configurable pool size (default: 100)

### 8.2 Key Collections by Domain

**User Management (5 collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| users | 232 | User accounts |
| user_sessions | 2,848 | Active sessions |
| user_settings | 1 | User preferences |
| user_consents | 1 | GDPR consents |
| user_credentials | 24 | Stored credentials |

**Authentication (7 collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| passkey_challenges | 14 | WebAuthn challenges |
| webauthn_challenges | 5 | FIDO2 challenges |
| github_auth_states | 6 | GitHub OAuth states |
| orcid_oauth_states | 57 | ORCID OAuth states |
| karau_email_verification_codes | 1 | Email verification |
| karau_guest_otps | 24 | Guest OTP codes |
| karau_verified_guests | 8 | Verified guests |

**Jobs & Recruitment (15 collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| posted_jobs | 15 | Job postings |
| applications | 22 | Job applications |
| application_links | 8 | Public application links |
| resumes | 2 | User resumes |
| saved_jobs | 9 | Bookmarked jobs |
| interview_preps | 64 | Interview preparation |
| interview_questions | 7 | Question bank |
| skill_assessments | 63 | Skill tests |
| smart_apply_configs | 1 | Smart Apply settings |
| smart_apply_runs | 11 | Smart Apply executions |
| job_alerts | 1 | Alert subscriptions |
| job_applicants | 4 | Applicant records |
| job_verifications | 2 | Job verification records |
| recruiter_profiles | 5 | Recruiter profiles |
| recruiter_verifications | 1 | Recruiter verifications |

**KARAU Meetings (20+ collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| karau_meetings | 315 | Meeting records |
| karau_organizations | 6 | Organizations |
| karau_employees | 17 | Org members |
| karau_recordings | 7 | Recordings |
| karau_transcripts | 2 | Transcriptions |
| webinars | 63 | Webinar records |
| meeting_polls | 10 | Live polls |
| meeting_replays | 1 | Replay data |
| hardware_devices | 26 | Discovered devices |
| breakout_lounges | 3 | Breakout rooms |
| (+ 10 more) | | |

**ENZI Messenger (20+ collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| lumi_channels | 96 | Channels |
| lumi_messages | 253 | Messages |
| lumi_read_receipts | 14 | Read tracking |
| lumi_presence | 6 | Online status |
| lumi_files | 3 | Shared files |
| enzi_installed_bots | 11 | Installed bots |
| enzi_invites | 34 | Invitations |
| enzi_webhooks | 9 | Webhooks |
| e2ee_keys | 1 | Encryption keys |
| (+ 11 more) | | |

**ML Pipeline (2 collections)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| ml_training_data | 80,807 | Training dataset |
| trust_score_history | 1,849 | Trust score records |

**Payments (1 collection)**
| Collection | Est. Docs | Purpose |
|------------|-----------|---------|
| payment_transactions | 10 | Transaction records |

---

## 9. Third-Party Integrations

### 9.1 Active Integrations

| Service | Purpose | Auth Method | Status |
|---------|---------|-------------|--------|
| **OpenAI (GPT-4o)** | AI text generation, analysis | Emergent LLM Key | Active |
| **Google Gemini** | AI text generation | Emergent LLM Key | Active |
| **Claude (Anthropic)** | AI text generation | Emergent LLM Key | Active |
| **Stripe** | Payment processing | API Key | Active (test mode) |
| **PayPal** | Payment processing | Client ID/Secret | Active (sandbox) |
| **Resend** | Transactional email | API Key | Configurable |
| **Google OAuth** | Social login | Emergent-managed | Active |
| **ORCID** | Researcher authentication | OAuth2 | Active |
| **LinkedIn** | Profile sync + OAuth | OAuth2 | Active |
| **Xirsys** | TURN/STUN servers for WebRTC | API Key | Active |
| **Microsoft Edge TTS** | Text-to-speech | Free API | Active |
| **python-jobspy** | Multi-site job scraping | No auth | Active |

### 9.2 Configured but Pending Validation

| Service | Purpose | Blocker |
|---------|---------|---------|
| **Microsoft Graph** | Teams/Outlook integration | Azure AD registration needed |
| **Apple Sign-In** | Apple authentication | Developer account validation |
| **GitHub OAuth** | GitHub login | Redirect URI verification |
| **Dropbox** | Cloud storage | OAuth flow testing |
| **OneDrive** | Cloud storage | Azure AD integration |
| **D-ID** | AI avatar video generation | API key validation |

---

## 10. Testing & Quality Assurance

### 10.1 Test Gates

| Gate | Name | Tests | Status |
|------|------|-------|--------|
| G1 | Functional Complete | 59/59 pass | PASSED |
| G2 | Reliability Validated | 31/31 pass | PASSED |
| G3 | Regression Clean | 41/41 pass | PASSED |
| G4 | Platform Certification | 54/54 pass | PASSED |
| G5 | Security Sign-Off | - | PENDING (CISO review) |

### 10.2 CI/CD Pipeline

**Platform:** GitHub Actions  
**Trigger:** Push to `main` or `develop`, pull requests  
**File:** `.github/workflows/test.yml`

Pipeline stages:
1. Phase 1: Functional Testing (Gate G1) — 59 tests
2. Phase 3: Post-Reliability Regression (Gate G3) — 41 tests
3. Gate Summary — Pass/fail determination

**Known issue:** Dependency conflict between `numpy==2.4.1` and `python-jobspy==1.1.82` (requires `numpy==1.26.3`). Resolved in CI via `sed`-based pin relaxation.

### 10.3 Test Credentials

| Account | Email | Role |
|---------|-------|------|
| Admin | admin@medmatch.com | System administrator |
| Test User | test@medmatch.io | Recruiter |

---

## 11. File Inventory

### 11.1 Python Files (228 total — 96,680 LOC)

#### Route Modules (`/app/backend/routes/`) — 131 files
```
admin_audit.py (685)            karau_beamforming.py (285)
advanced_features.py (590)      karau_biometric_verify.py (193)
ai_compliance.py (190)          karau_breakout_lounges.py (219)
ai_features.py (1061)           karau_calendar.py (367)
ai_productivity.py (1434)       karau_collaboration.py (417)
ai_qa.py (490)                  karau_director.py (131)
ai_talent.py (277)              karau_enhanced_sentiment.py (243)
analytics.py (253)              karau_extended.py (727)
analytics_funnel.py (339)       karau_gamification.py (161)
ats.py (664)                    karau_ghost_booking.py (156)
audit_reports.py (524)          karau_guest_verification.py (305)
auth.py (1544)                  karau_hardware_discovery.py (197)
autofill.py (402)               karau_intelligence.py (297)
avatar.py (127)                 karau_iot_control.py (247)
batch.py (144)                  karau_meet.py (1227)
behavioral.py (298)             karau_organizations.py (963)
biometric.py (588)              karau_polls_challenges.py (259)
capa.py (372)                   karau_qr_entry.py (135)
cloud.py (549)                  karau_recordings.py (315)
companies.py (333)              karau_replay.py (582)
compliance_alerts.py (298)      karau_scheduling.py (301)
credentials.py (926)            karau_security.py (323)
data_integrity.py (212)         karau_sharing.py (115)
dei_analytics.py (96)           karau_simulation.py (287)
digest.py (321)                 karau_slam_spatial.py (284)
dragon.py (682)                 karau_sso.py (339)
dragon_automator.py (1352)      karau_webinar.py (1077)
e2ee.py (146)                   karau_webrtc.py (137)
email_settings.py (118)         karau_webxr.py (208)
employer_reviews.py (430)       linkedin.py (271)
enterprise_api.py (846)         lumi_ai.py (224)
enzi_ai.py (111)                lumi_buckets.py (211)
enzi_automation.py (278)        lumi_calendar.py (187)
enzi_bots.py (880)              lumi_files.py (139)
enzi_channel_templates.py (130) lumi_messenger.py (2466)
enzi_domain.py (90)             lumi_predict.py (154)
enzi_invites.py (271)           lumi_templates.py (129)
enzi_meetings.py (164)          meeting_channel_sync.py (420)
enzi_notifications.py (120)     meeting_infrastructure.py (188)
enzi_payments.py (153)          meeting_intelligence.py (549)
enzi_sentiment.py (100)         meeting_notes.py (605)
enzi_webhook_templates.py (115) messages.py (166)
feedback.py (333)               ml_data.py (266)
geolocation.py (219)            ml_model.py (149)
global_compliance.py (158)      ml_predictor.py (172)
id_verification.py (322)        mutual_match.py (589)
interview.py (507)              notifications.py (160)
interview_calendar.py (722)     orcid_oauth.py (429)
job_verification.py (109)       payments.py (801)
jobs.py (1158)                  persona_verification.py (499)
karau_accessibility.py (219)    platform_features.py (243)
karau_ai.py (189)               portal_access.py (253)
karau_analytics.py (341)        privacy.py (687)
                                production_metrics.py (300)
psv.py (1105)                   talent_tools.py (220)
push.py (324)                   taxonomy.py (550)
push_notifications.py (318)     translation.py (1957)
qa_practice.py (708)            translation_qa.py (990)
realtime_stt.py (417)           tutorials.py (988)
recruiter.py (551)              video_analysis.py (572)
recruiter_rbac.py (913)         video_assets.py (217)
resume.py (355)                 video_interview.py (323)
scheduling.py (540)             video_translation.py (294)
search_engine.py (280)          webpush.py (677)
skills.py (1501)
smart_apply.py (298)
talent_crm.py (372)
```

#### Service Modules (`/app/backend/services/`) — 71 files
```
__init__.py (0)                       karau_meet/__init__.py (32)
ai_compliance_service.py (585)        karau_meet/accessibility_service.py (329)
ai_qa/__init__.py (86)                karau_meet/ai_assistant_service.py (252)
ai_qa/audit_service.py (762)          karau_meet/ai_transcription_service.py (504)
ai_qa/core_service.py (612)           karau_meet/collaboration_service.py (429)
ai_qa/oversight_service.py (471)      karau_meet/email_service.py (304)
ai_qa/transparency_service.py (400)   karau_meet/meeting_service.py (817)
ai_supervisor.py (620)                karau_meet/scheduling_service.py (445)
ai_translation_generator.py (177)     karau_meet/security_service.py (652)
audit_reports.py (996)                karau_meet/translation_service.py (101)
capa_service.py (635)                 karau_meet/turn_service.py (83)
capa_video_regen.py (75)              karau_meet/webrtc_signaling.py (692)
career_pivot.py (441)                 meeting_notes_service.py (56)
compliance_alerts.py (301)            ml_data_collector.py (491)
credly_service.py (317)               ml_data_generator.py (285)
data_integrity_service.py (868)       ml_issue_predictor.py (559)
did_avatar_service.py (471)           ml_model_trainer.py (482)
dragon_scheduler.py (1012)            object_storage.py (58)
edge_tts_service.py (969)             pdf_export.py (730)
email_service.py (499)                presentation_service.py (94)
fresh_video_regen.py (329)            production_metrics.py (477)
geolocation.py (461)                  psv_service.py (724)
global_compliance_service.py (859)    question_bank.py (475)
global_rate_limiter.py (379)          regen_videos_v2.py (189)
gual_integration.py (387)             regenerate_regional_tutorials.py (176)
job_liveness.py (407)                 regenerate_videos.py (329)
job_sources.py (897)                  regenerate_with_presenter.py (359)
                                      search_engine.py (529)
smart_notifications.py (457)          video_faq.py (194)
taxonomy.py (571)                     video_generator.py (79)
transcription_service.py (109)        video_pip.py (257)
translation_qa.py (556)               video_storage.py (155)
trust_score.py (495)                  video_with_highlights.py (397)
tutorial_subtitles.py (1663)          video_with_screenshots.py (237)
video_3_tutorials.py (210)            video_with_voice.py (191)
video_asset_manager.py (597)          web_job_crawler.py (408)
```

#### Test Files (`/app/backend/tests/`) — 10 files
```
test_phase1_functional.py (839)
test_phase2_reliability.py (618)
test_phase3_regression.py (826)
test_phase4_deployment_readiness.py (488)
test_iteration220_features.py (417)
test_iteration_210.py (318)
test_smart_apply_iteration215.py (258)
test_smart_apply_iteration214.py (207)
test_phases_2_4.py (144)
test_passkeys_iteration213.py (117)
```

#### Other Backend Python Files
```
server.py (828)                    utils/__init__.py (3)
models/__init__.py (2)             utils/config.py (45)
models/schemas.py (165)            utils/database.py (38)
routes/__init__.py (152)           utils/push_service.py (262)
digest_scheduler.py (65)
scripts/seed_data.py (334)
scripts/sync_translations.py (113)
scripts/translate_missing_keys.py (214)
scripts/translate_priority_keys.py (373)
util/batch_translate.py (127)
util/propagate_i18n.py (49)
util/retry_translate.py (95)
util/translate_locales_v5.py (134)
```

### 11.2 Markdown Files (44 total)

#### Documentation (`/app/docs/`) — 9 files
```
DEPLOYMENT_READINESS.md (278)
DEVELOPMENT_ANALYST_REPORT_22_03_2026.md (139)
GAP_ASSESSMENT.md (434)
PAYPAL_INTEGRATION.md (270)
PRODUCTION_LAUNCH_PLAYBOOK.md (204)
STRIPE_WEBHOOK_GUIDE.md (265)
TESTING_STRATEGY_RESULTS.md (159)
guides/AVATAR_VIDEO_LIBRARY.md (183)
guides/AVATAR_VIDEO_SCRIPTS.md (106)
guides/EXPO_BUILD_GUIDE.md (150)
guides/NAVIGATION_GUIDE.md (243)
guides/PENDING_INTEGRATIONS_GUIDE.md (502)
```

#### Memory & Planning (`/app/memory/`) — 13 files
```
PRD.md (72)
CHANGELOG.md (170)
ROADMAP.md (155)
EXECUTIVE_SUMMARY.md (439)
FUNCTIONAL_ASSESSMENT.md (221)
GAP_ASSESSMENT.md (92)
OAUTH_SETUP_GUIDE.md (397)
REFACTORING_GUIDE.md (198)
DEPLOYMENT_RUNBOOK.md (154)
STRESS_TEST_REPORT.md (152)
CAPA-002-video-translation.md (154)
CAPA/CAPA-2026-001-AI-Translation.md (232)
CAPA/CAPA-Tracker.md (40)
docs/i18n-best-practices.md (199)
docs/live-test-guide.md (63)
```

#### Mobile Docs (`/app/mobile/`) — 4 files
```
README.md (141)
IOS_DEPLOYMENT_GUIDE.md (409)
ios-build-guide.md (223)
testflight-setup-guide.md (352)
```

#### Other Markdown Files
```
/app/CHANGELOG.md (48)
/app/README.md (1)
/app/ROADMAP.md (24)
/app/backend/PRODUCTION_CONFIG.md (222)
/app/desktop/README.md (160)
/app/desktop/assets/README.md (54)
/app/frontend/README.md (70)
/app/image_testing.md (16)
/app/test_reports/comprehensive_assessment_feb5_2026.md (256)
/app/test_reports/functional_assessment_report.md (225)
/app/test_result.md (102)
```

---

*End of System Requirements Document*
