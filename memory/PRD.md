# MedMatch - Remote Job Finder with AI Matching

## Original Problem Statement
Create an application that uses the user's resume to find remote jobs that match their skills and experience. Features include job search, AI matching, email alerts, cover letter generation, callback prediction, interview preparation, voice coaching, and video interview practice.

## User Personas
- **Job Seekers**: Professionals in Quality/Medical Device fields looking for remote positions
- **Target Roles**: Supplier Quality Manager, Quality Director, Lead Auditor, Medical Device professionals

## Core Requirements
- ✅ Resume upload and AI-powered parsing
- ✅ Multi-source job search (RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas)
- ✅ JobSpy integration for LinkedIn, Indeed, Glassdoor
- ✅ Google Custom Search Engine integration
- ✅ AI-powered job matching and relevance scoring
- ✅ Save/bookmark jobs
- ✅ Application tracking with status updates
- ✅ Email alerts for matching jobs
- ✅ Automated Daily Digest Scheduler (8 AM UTC)
- ✅ AI Cover Letter Generator with PDF Export
- ✅ Application Success Predictor
- ✅ Interview Preparation with PDF Export
- ✅ AI Interview Coach with Voice + Recording Playback
- ✅ **Video Interview Practice with AI Body Language Analysis** (NEW - Jan 2026)
- ✅ Dark Mode with Inverted Batik Theme
- ✅ Job Application Analytics Dashboard
- ✅ Multiple Resume Profiles

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB (motor)
- **Frontend**: React with shadcn/ui components
- **AI**: Emergent LLM Key (GPT models via emergentintegrations)
- **Vision AI**: OpenAI Vision API for body language analysis
- **Voice**: Web Speech API + MediaRecorder API
- **Video**: MediaRecorder API with canvas frame capture
- **Email**: Gmail SMTP
- **Scheduler**: APScheduler (AsyncIOScheduler)
- **Theming**: CSS custom properties with localStorage persistence

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- APScheduler for automated daily digest
- AI Vision integration for video frame analysis
- PDF export endpoints for Cover Letters and Interview Prep

### Frontend Pages (13 Total)
```
├── pages/
│   ├── Dashboard.jsx              # Overview with stats
│   ├── ResumePage.jsx             # Resume upload
│   ├── ResumeProfilesPage.jsx     # Multiple resume profiles
│   ├── JobSearchPage.jsx          # Job search with filters
│   ├── SavedJobsPage.jsx          # Saved jobs list
│   ├── ApplicationsPage.jsx       # Application tracker
│   ├── SuccessPredictorPage.jsx   # AI callback prediction
│   ├── InterviewPrepPage.jsx      # Interview prep + PDF export
│   ├── VoiceCoachPage.jsx         # Voice coach + playback
│   ├── VideoInterviewPage.jsx     # Video practice + AI analysis (NEW)
│   ├── CoverLetterPage.jsx        # Cover letter + PDF export
│   ├── JobAlertsPage.jsx          # Email alerts & scheduler
│   └── AnalyticsDashboard.jsx     # Application analytics
```

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume` | GET | Get user's resume |
| `/api/resume/upload` | POST | Upload and parse resume |
| `/api/resume/profiles` | GET/POST | Get/create resume profiles |
| `/api/jobs/search` | GET | Search jobs with filters |
| `/api/jobs/deep-search` | POST | AI-powered comprehensive search |
| `/api/analytics/dashboard` | GET | Get application analytics |
| `/api/interview/generate-questions` | POST | Generate interview questions |
| `/api/interview/voice-feedback` | POST | AI voice interview feedback |
| `/api/interview/analyze-video-frame` | POST | AI body language analysis (NEW) |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |
| `/api/export/cover-letter-html` | POST | Export cover letter to PDF |
| `/api/export/interview-prep-html` | POST | Export interview prep to PDF |

## Video Interview Features (NEW)
- **Webcam Recording**: Record practice interviews with MediaRecorder
- **AI Body Language Analysis**: Using OpenAI Vision API
  - Eye Contact Score (0-100)
  - Posture Score (0-100)
  - Confidence Score (0-100)
  - Facial Expression Analysis
  - Improvement Tips
- **Video Playback**: Review recorded responses
- **Session History**: Track previous practice sessions

## PDF Export Features (NEW)
- **Cover Letter Export**: Professional PDF with candidate info, date, formatted letter
- **Interview Prep Export**: PDF with all questions, categories, difficulty levels

## Design System - Batik B Theme

### Color Palette
**Light Mode:**
- Background: #f8f8f8
- Cards: #ffffff
- Accent: Turquoise #20b2aa

**Dark Mode (Inverted):**
- Background: #1a1a1a
- Cards: #2d2d2d
- Accent: Turquoise #20b2aa

## Implementation Status

### Completed Features (January 2026)
1. ✅ Core MVP - Resume upload, parsing, job search
2. ✅ Multi-source Integration - 6+ job boards + Google CSE
3. ✅ AI Features - Job matching, cover letter, callback prediction
4. ✅ User Management - Save jobs, track applications
5. ✅ Email Features - Alerts, automated daily digest
6. ✅ Interview Preparation - Questions, answers, mock interviews
7. ✅ Voice Coach - Speech-to-text with AI feedback + playback
8. ✅ Video Interview Practice - AI body language analysis
9. ✅ Dark Mode - Inverted batik theme with toggle
10. ✅ Analytics Dashboard - Application analytics with charts
11. ✅ Multiple Resume Profiles - Manage different resumes
12. ✅ PDF Export - Cover letters and interview prep

## Future Enhancements (Backlog)
- [ ] Real-time video analysis during recording
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Custom schedule options for digest

## Test Reports
- `/app/test_reports/iteration_5.json` - Frontend refactor tests
- `/app/test_reports/iteration_6.json` - Analytics, Profiles, Voice Playback
- `/app/test_reports/iteration_7.json` - Video Interview, PDF Export (100% pass)
