# MedMatch - AI-Powered Remote Job Search Application

## Original Problem Statement
Create a comprehensive job search application where users can upload their resume, search for matching jobs, and apply directly. The app should support multiple authentication methods and automatically track applications.

## Core Features

### Authentication
- ✅ **Google Login** - Emergent-managed OAuth (working)
- ✅ **Apple Login** - Apple Sign In implemented (Backend complete, requires Apple Developer Console URL registration)
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

### User Management
- ✅ Save/bookmark jobs
- ✅ Multiple resume profiles
- ✅ Email alerts for matching jobs
- ✅ Automated daily digest (8 AM UTC)
- ✅ Job application analytics dashboard

### Membership System
- ✅ Job Seekers: $1 lifetime membership with 15-day free trial
- ✅ Recruiters: Free forever with job posting capabilities
- ✅ Stripe payment integration
- ⏸️ PayPal integration (deprioritized, backend ready)

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB
- **Frontend**: React with shadcn/ui
- **AI**: Emergent LLM Key (GPT models)
- **Auth**: Emergent Google OAuth, Apple Sign In, Email/Password, Twilio SMS (optional)
- **Payments**: Stripe
- **Email**: Gmail SMTP

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

## Pages (14 Total)
1. **Login** - Google, Apple, Email, Phone options
2. **Dashboard** - Overview with stats
3. **My Resume** - Upload and view resume
4. **Resume Profiles** - Multiple resume management
5. **Job Search** - Search with filters
6. **Saved Jobs** - Bookmarked jobs
7. **Applications** - Application tracker
8. **Success Predictor** - AI callback prediction
9. **Interview Prep** - Questions with PDF export
10. **Voice Coach** - Voice practice with playback
11. **Video Practice** - Video interview with AI analysis
12. **Cover Letter** - AI generator with PDF export
13. **Job Alerts** - Email alerts setup
14. **Analytics** - Application analytics dashboard
15. **Membership** - Subscription management

## Configuration

### Already Configured
- `MONGO_URL` - MongoDB connection
- `EMERGENT_LLM_KEY` - AI features
- `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` - Email alerts
- `GOOGLE_API_KEY` / `GOOGLE_CSE_ID` - Web search
- `JWT_SECRET_KEY` - Session encryption
- `STRIPE_API_KEY` - Payment processing
- `APPLE_TEAM_ID` - 96879J9FZY
- `APPLE_KEY_ID` - PJCYWKB3TU
- `APPLE_SERVICE_ID` - com.medmatch.signin.web
- `APPLE_PRIVATE_KEY` - Configured

### Apple Sign In Setup (Action Required)
To complete Apple Sign In, register redirect URL in Apple Developer Console:
- Services ID: `com.medmatch.signin.web`
- Redirect URL: `https://remotematch.preview.emergentagent.com/login`

### Optional Configuration (for Phone Login)
- `TWILIO_ACCOUNT_SID` - Twilio account
- `TWILIO_AUTH_TOKEN` - Twilio auth
- `TWILIO_VERIFY_SERVICE` - Twilio Verify service ID

## Test Reports
- `/app/test_reports/iteration_10.json` - Latest auth tests (100% pass - 14/14 tests)
- `/app/tests/test_auth_apple.py` - Comprehensive auth test suite

## What's Working
✅ Backend: FastAPI on port 8001
✅ Frontend: React on port 3000
✅ Database: MongoDB
✅ All auth methods (Google, Apple backend, Email)
✅ Membership system with roles
✅ Job search from multiple sources
✅ AI-powered features
✅ Payment processing (Stripe)

## Upcoming Tasks
- [ ] Recruiter job posting UI implementation
- [ ] Premium feature gating with PremiumGate component
- [ ] User onboarding tour

## Future Tasks / Backlog
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Refactor server.py into modular routes
