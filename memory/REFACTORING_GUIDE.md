# Server.py Refactoring Guide

## Current State
- Single file: `/app/backend/server.py` (~4,800 lines)
- All routes, models, and utilities in one file

## Target Architecture

```
/app/backend/
├── server.py              # Main app entry, minimal code
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication (register, login, Google, Apple, phone)
│   ├── payments.py       # Stripe, PayPal, membership
│   ├── recruiter.py      # Recruiter job posting
│   ├── jobs.py           # Job search, saved jobs
│   ├── applications.py   # Application tracking
│   ├── ai_features.py    # Cover letter, interview prep, voice/video coach
│   ├── alerts.py         # Job alerts & digest
│   ├── analytics.py      # Analytics dashboard
│   └── resume.py         # Resume upload & profiles
├── models/
│   ├── __init__.py
│   └── schemas.py        # Pydantic models
├── utils/
│   ├── __init__.py
│   ├── database.py       # MongoDB connection
│   ├── config.py         # Environment variables
│   ├── auth_helpers.py   # Password hashing, JWT, sessions
│   ├── email.py          # Email sending utilities
│   └── ai.py             # LLM chat utilities
└── tests/
    └── test_*.py
```

## Route Mapping

### auth.py (Lines 458-1010)
- POST `/auth/register`
- POST `/auth/login`
- POST `/auth/google/session`
- POST `/auth/apple/callback`
- GET `/auth/apple/config`
- POST `/auth/apple/redirect`
- POST `/auth/phone/send-otp`
- POST `/auth/phone/verify-otp`
- GET `/auth/me`
- POST `/auth/logout`

### payments.py (Lines 1013-1395)
- POST `/payments/create-checkout`
- GET `/payments/status/{session_id}`
- POST `/webhook/stripe`
- GET `/membership/status`
- POST `/payments/paypal/create`
- POST `/payments/paypal/execute`
- GET `/membership/check-access/{feature}`

### recruiter.py (Lines 1396-1490)
- POST `/recruiter/jobs`
- GET `/recruiter/jobs`
- PUT `/recruiter/jobs/{job_id}`
- DELETE `/recruiter/jobs/{job_id}`

### jobs.py (Lines 2550-2890)
- POST `/resume/upload`
- GET `/resume`
- PUT `/resume/skills`
- GET `/jobs/search`
- GET `/jobs/google-search`
- POST `/jobs/deep-search`
- GET `/jobs/presets`
- POST `/jobs/analyze`
- POST `/jobs/save`
- GET `/jobs/saved`
- DELETE `/jobs/saved/{job_id}`
- POST `/jobs/manual`

### applications.py
- POST `/applications`
- POST `/applications/quick-apply`
- GET `/applications`
- GET `/applications/check/{job_url:path}`
- PUT `/applications/{app_id}`
- PUT `/applications/{app_id}/job-status`
- DELETE `/applications/{app_id}`

### alerts.py
- POST `/alerts`
- GET `/alerts`
- DELETE `/alerts/{alert_id}`
- POST `/alerts/send-now`
- POST `/digest/settings`
- GET `/digest/settings`
- DELETE `/digest/settings/{email}`
- POST `/digest/send-daily`
- GET `/digest/history`
- DELETE `/digest/history/{email}`
- GET `/digest/scheduler-status`
- POST `/digest/trigger-now`
- POST `/digest/run-scheduled`

### ai_features.py
- POST `/cover-letter/generate`
- GET `/cover-letter/history`
- DELETE `/cover-letter/{letter_id}`
- POST `/jobs/predict-callback`
- GET `/jobs/prediction-history`
- DELETE `/jobs/prediction-history/{prediction_id}`
- POST `/jobs/quick-probability`
- POST `/interview/generate-questions`
- GET `/interview/cached-questions`
- POST `/interview/generate-answer`
- POST `/interview/polish-star`
- POST `/interview/research-company`
- POST `/interview/mock-feedback`
- POST `/interview/voice-feedback`
- POST `/interview/video-feedback`
- GET `/interview/video-recordings`
- DELETE `/interview/video-recordings/{recording_id}`
- POST `/interview/analyze-video-frame`
- POST `/export/cover-letter-html`
- POST `/export/interview-prep-html`

### analytics.py
- GET `/analytics/dashboard`

### resume.py
- GET `/resume/profiles`
- POST `/resume/profiles`
- PUT `/resume/profiles/{profile_id}`
- DELETE `/resume/profiles/{profile_id}`
- POST `/resume/profiles/{profile_id}/set-default`
- POST `/resume/profiles/upload`

## Refactoring Steps

1. **Create utility modules first** (database.py, config.py) ✅
2. **Extract shared models** (schemas.py) ✅
3. **Extract auth routes** - Start with isolated functionality
4. **Extract payment routes**
5. **Extract remaining routes one at a time**
6. **Update server.py to import routers**
7. **Run tests after each extraction**

## Example Router Implementation

```python
# routes/auth.py
from fastapi import APIRouter, HTTPException, Response
from models.schemas import RegisterRequest, LoginRequest
from utils.database import db
from utils.config import JWT_SECRET_KEY
import hashlib
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(request: RegisterRequest):
    # ... implementation
    pass

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    # ... implementation
    pass
```

## Main Server.py After Refactoring

```python
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routes import auth, payments, jobs, applications, ai_features, alerts, analytics, resume, recruiter

app = FastAPI()

# CORS
app.add_middleware(CORSMiddleware, ...)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(ai_features.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(recruiter.router, prefix="/api")
```

## Priority
- Medium priority refactoring task
- Recommend doing during a dedicated refactoring session
- Current monolith works but harder to maintain
