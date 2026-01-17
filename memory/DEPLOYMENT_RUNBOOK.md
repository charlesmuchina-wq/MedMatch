# MedMatch Deployment Runbook

## Pre-Deployment Checklist

### 1. Environment Variables

#### Backend Required Variables
```bash
# Database
MONGO_URL=mongodb+srv://[user]:[pass]@[cluster].mongodb.net/medmatch?retryWrites=true&w=majority
DB_NAME=medmatch_production

# Authentication
JWT_SECRET_KEY=[generate: openssl rand -hex 32]
EMERGENT_LLM_KEY=[from Emergent Platform]

# WebAuthn/Biometric
WEBAUTHN_RP_ID=[your-domain.com]
WEBAUTHN_RP_NAME=MedMatch

# Payment
STRIPE_SECRET_KEY=[production key from Stripe Dashboard]

# OAuth
GOOGLE_CLIENT_ID=[from Google Cloud Console]
APPLE_TEAM_ID=[from Apple Developer Console]
APPLE_KEY_ID=[from Apple Developer Console]
APPLE_SERVICE_ID=[from Apple Developer Console]
APPLE_PRIVATE_KEY=[base64 encoded .p8 file]

# SMS (Twilio)
TWILIO_ACCOUNT_SID=[from Twilio Console]
TWILIO_AUTH_TOKEN=[from Twilio Console]
TWILIO_VERIFY_SERVICE=[from Twilio Console]
```

#### Frontend Required Variables
```bash
REACT_APP_BACKEND_URL=https://api.[your-domain.com]
REACT_APP_GOOGLE_CLIENT_ID=[same as backend]
REACT_APP_GOOGLE_API_KEY=[from Google Cloud Console]
REACT_APP_STRIPE_PUBLISHABLE_KEY=[from Stripe Dashboard]
```

### 2. Database Setup

```javascript
// Connect to MongoDB and run:
use medmatch_production

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "user_id": 1 }, { unique: true })
db.jobs.createIndex({ "posted_at": -1 })
db.jobs.createIndex({ "location": 1, "posted_at": -1 })
db.jobs.createIndex({ "source": 1 })
db.applications.createIndex({ "user_id": 1, "job_id": 1 })
db.webauthn_credentials.createIndex({ "email": 1 })
db.webauthn_credentials.createIndex({ "webauthn_credential_id": 1 })
db.webauthn_challenges.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })
db.user_sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })
db.messages.createIndex({ "conversation_id": 1, "created_at": -1 })

// Create TTL indexes for automatic cleanup
db.webauthn_challenges.createIndex({ "created_at": 1 }, { expireAfterSeconds: 600 })
```

### 3. SSL/TLS Configuration

Ensure SSL certificates are configured for:
- `medmatch.com` (main domain)
- `api.medmatch.com` (API subdomain)
- `*.medmatch.com` (wildcard for future subdomains)

### 4. CORS Configuration

Update backend CORS for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://medmatch.com",
        "https://www.medmatch.com",
        "https://app.medmatch.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Deployment Steps

### Step 1: Build Frontend
```bash
cd /app/frontend
yarn build
# Output in /app/frontend/build
```

### Step 2: Deploy Backend
```bash
# Using Emergent Platform deployment
# Or Docker:
docker build -t medmatch-backend:latest ./backend
docker push [registry]/medmatch-backend:latest
```

### Step 3: Database Migration
```bash
# No schema migration needed - MongoDB is schemaless
# Run index creation script above
```

### Step 4: Health Checks
```bash
# Backend health
curl https://api.medmatch.com/health

# API smoke test
curl https://api.medmatch.com/api/translate/languages
```

---

## Rollback Procedure

1. **Identify issue**: Check error logs, APM dashboards
2. **Notify team**: Alert on-call engineer
3. **Rollback deployment**: Use Emergent Platform rollback feature
4. **Verify rollback**: Run health checks
5. **Post-mortem**: Document issue and resolution

---

## Monitoring Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| High Error Rate | >1% 5xx errors | Page on-call |
| Slow Response | P95 > 2s | Investigate |
| Database Connection | Failed connections | Page on-call |
| Memory Usage | >85% | Scale up pods |
| Disk Usage | >80% | Clean logs/cache |

---

## Support Contacts

- **Emergent Platform Support**: support@emergent.sh
- **Stripe Support**: dashboard.stripe.com/support
- **MongoDB Atlas Support**: cloud.mongodb.com/support
