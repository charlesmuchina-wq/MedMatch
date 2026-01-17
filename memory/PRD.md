# MedMatch - AI-Powered Remote Job Search Application

## Original Problem Statement
Create a comprehensive job search application where users can upload their resume, search for matching jobs, and apply directly. The app should support multiple authentication methods and automatically track applications.

## Core Features

### Authentication
- ✅ **Google Login** - Emergent-managed OAuth (working)
- ✅ **Apple Login** - Configured (requires Apple Developer Console redirect URL setup)
- ✅ **Email/Password** - Traditional registration and login with secure hashing
- ⚙️ **Phone/SMS** - Requires Twilio credentials (endpoints ready)

### Job Search
- ✅ Resume upload and AI-powered parsing
- ✅ Multi-source job search (RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas)
- ✅ JobSpy integration for LinkedIn, Indeed, Glassdoor
- ✅ Google Custom Search Engine integration
- ✅ AI-powered job matching and relevance scoring

### Application Tracking
- ✅ **Quick Apply** - Click apply → Opens job URL → Auto-marks as "Applied"
- ✅ Application status tracking (Applied, Interview, Offer, Rejected)
- ✅ Job status tracking (Active, Closed, Filled, Still Accepting)
- ✅ Duplicate detection - Won't re-apply to same job URL

### AI Features
- ✅ AI Cover Letter Generator with PDF Export
- ✅ Application Success Predictor
- ✅ Interview Preparation with PDF Export
- ✅ Voice Interview Coach with Recording Playback
- ✅ Video Interview Practice with AI Body Language Analysis
- ✅ Salary Insights and Negotiation Tips
- ✅ **AI Prescreening** - Analyzes candidate vs job fit with transferable skills (NEW)

### User Management
- ✅ Save/bookmark jobs
- ✅ Multiple resume profiles
- ✅ Email alerts for matching jobs
- ✅ Automated daily digest (8 AM UTC)
- ✅ Job application analytics dashboard
- ✅ **In-App Messaging** - Recruiter ↔ Job Seeker communication (NEW)

### Membership System
- ✅ Job Seekers: $1 lifetime membership with 15-day free trial
- ✅ Recruiters: Free forever with job posting capabilities
- ✅ Stripe payment integration
- ⏸️ PayPal integration (deprioritized, backend ready)

### Cloud Storage Integration
- ✅ **Google Drive** - Fully integrated with OAuth Picker API
- ⚙️ **Dropbox** - UI ready, requires API key
- ⚙️ **OneDrive** - UI ready, requires API key

### Recruiter Features (NEW - Jan 17, 2026)
- ✅ **Applicant Tracking System** - View/manage applicants per job posting
- ✅ **Applicant Status Pipeline** - new → reviewing → shortlisted → interviewing → offered → hired/rejected
- ✅ **Applicant Notes** - Recruiters can add notes to applicants
- ✅ **Candidate Search** - Search job seekers by skills, keywords
- ✅ **AI Prescreening** - Match score, transferable skills, interview questions
- ✅ **Recruiter Dashboard** - Stats, quick actions, recent applicants
- ✅ **Role-Based Navigation** - Different sidebar for recruiters vs job seekers

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB
- **Frontend**: React with shadcn/ui
- **AI**: Emergent LLM Key (GPT models)
- **Auth**: Emergent Google OAuth, Apple Sign In, Email/Password, Twilio SMS (optional)
- **Payments**: Stripe
- **Email**: Gmail SMTP
- **Cloud Storage**: Google Drive API

## Bug Fixes (Jan 16, 2026)

### ✅ Session Expiration Bug (P0) - FIXED
**Problem**: Sessions were expiring rapidly during testing, causing repeated logouts.

**Root Cause**: 
1. Many axios API calls were missing `withCredentials: true`
2. CORS was configured with wildcard `*` which doesn't work with credentials

**Fix Applied**:
1. Added `axios.defaults.withCredentials = true` globally in `/app/frontend/src/index.js`
2. Updated `CORS_ORIGINS` in `/app/backend/.env` to specific domains instead of wildcard

**Files Modified**:
- `/app/frontend/src/index.js` - Added axios.defaults.withCredentials = true
- `/app/backend/.env` - Changed CORS_ORIGINS to specific domains

**Test Results**: 100% pass rate (10/10 backend tests, all frontend tests passed)

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register with email/password |
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/google/session` | POST | Process Google OAuth callback |
| `/api/auth/apple/config` | GET | Get Apple Sign In configuration |
| `/api/auth/apple/callback` | POST | Process Apple Sign In callback |
| `/api/auth/phone/send-otp` | POST | Send OTP via Twilio |
| `/api/auth/phone/verify-otp` | POST | Verify OTP and login |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/logout` | POST | Logout and clear session |

### Cloud Storage
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cloud/google-drive/download` | POST | Download file from Google Drive (proxy) |

### Applications
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/applications` | GET/POST | List/create applications |
| `/api/applications/quick-apply` | POST | Apply and get redirect URL |
| `/api/applications/check/{url}` | GET | Check if already applied |
| `/api/applications/{id}/job-status` | PUT | Update job posting status |

### Payments
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payments/create-checkout` | POST | Create Stripe checkout session |
| `/api/payments/status/{session_id}` | GET | Check payment status |
| `/api/membership/status` | GET | Get current membership status |

## Configuration

### Already Configured
- `MONGO_URL` - MongoDB connection
- `EMERGENT_LLM_KEY` - AI features
- `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` - Email alerts
- `GOOGLE_API_KEY` / `GOOGLE_CSE_ID` - Web search
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` - Google Drive
- `JWT_SECRET_KEY` - Session encryption
- `STRIPE_API_KEY` - Payment processing
- `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_SERVICE_ID`, `APPLE_PRIVATE_KEY` - Apple Sign In
- `CORS_ORIGINS` - https://job-finder-pro-4.preview.emergentagent.com,http://localhost:3000

### Optional Configuration
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE` - Phone login
- `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` - PayPal payments

## Test Reports
- `/app/test_reports/iteration_11.json` - Session persistence tests (100% pass)
- `/app/test_reports/iteration_10.json` - Auth tests (100% pass)
- `/app/tests/test_session_persistence.py` - Session persistence test suite

## What's Working
✅ Backend: FastAPI on port 8001
✅ Frontend: React on port 3000
✅ Database: MongoDB
✅ All auth methods (Google, Email) - FULLY WORKING
✅ Session persistence - FIXED (Jan 16, 2026)
✅ Last Login Tracking - Added (Jan 17, 2026)
✅ Membership system with roles
✅ Job search from multiple sources
✅ AI-powered features
✅ Payment processing (Stripe)
✅ PremiumGate component
✅ Onboarding Tour
✅ Recruiter Job Posting UI
✅ Quick Actions Widget
✅ PWA Support
✅ Google Drive integration for resume upload

## Gap Assessment Summary
Full analysis at `/app/memory/GAP_ASSESSMENT.md`

### Critical Gaps (P0 - Need for Recruiter Value)
- ❌ No Candidate Search/Database for Recruiters
- ❌ No Applicant Tracking per Job Posting
- ❌ No In-App Messaging
- ❌ No Company Profiles/Pages

### Important Gaps (P1)
- ❌ No Skill Assessments/Certifications
- ❌ No Company Reviews (like Glassdoor)
- ❌ No Interview Scheduling/Calendar
- ❌ No Native Mobile App (App Store)
- ❌ No Job Feedback for AI Learning

### MedMatch Strengths vs Competitors
- ✅ AI Cover Letter Generator (unique)
- ✅ Voice Interview Coach (unique)
- ✅ Video Interview Practice (unique)
- ✅ Callback Success Predictor (unique)
- ✅ $1 Lifetime (vs $30+/month competitors)

## Pending / Blocked Items

### Apple Sign In
- **Status**: Backend configured, frontend ready
- **Blocked**: Requires user to add redirect URL in Apple Developer Console
- **Redirect URL**: `https://job-finder-pro-4.preview.emergentagent.com/api/auth/apple/redirect`

### Android SHA-1 Fingerprint
- **Status**: User requested keytool command execution
- **Blocked**: Java/keytool not available in this environment
- **Action**: User needs to run `keytool -keystore path-to-keystore -list -v` locally

## Upcoming Tasks
- [ ] Complete server.py refactoring (guide at /app/memory/REFACTORING_GUIDE.md)
- [ ] Dropbox integration (requires API key from user)
- [ ] OneDrive integration (requires API key from user)
- [ ] Native Windows widget (requires Electron/MSIX packaging)
- [ ] Push notifications

## Test Credentials
- **Admin**: admin@medmatch.com / MedMatch2026!
- **Recruiter**: recruiter@medmatch-test.com / test123
