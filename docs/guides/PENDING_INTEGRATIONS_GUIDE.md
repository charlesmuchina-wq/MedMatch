# MedMatch - Pending Integrations & Setup Guide

This guide provides step-by-step instructions for all pending/blocked integrations and builds.

---

## Table of Contents
1. [Expo/EAS Mobile Builds](#1-expoeas-mobile-builds)
2. [Video Generation (Sora 2)](#2-video-generation-sora-2)
3. [AI Avatar (D-ID)](#3-ai-avatar-d-id-integration)
4. [Primary Source Verification (PSV)](#4-primary-source-verification-psv-apis)
5. [LinkedIn Integration](#5-linkedin-integration)
6. [Cloud Storage Integrations](#6-cloud-storage-integrations)
7. [Payment Integrations](#7-payment-integrations)

---

## 1. Expo/EAS Mobile Builds

### Prerequisites
- Expo account (free or paid)
- EAS CLI installed
- Apple Developer account (for iOS)
- Google Play Console account (for Android)

### Step 1: Create Expo Account & Get Token

1. **Create Expo Account:**
   - Go to: https://expo.dev/signup
   - Sign up with email or GitHub

2. **Generate EXPO_TOKEN:**
   - Go to: https://expo.dev/accounts/[your-username]/settings/access-tokens
   - Click "Create Token"
   - Name it: `medmatch-ci-token`
   - Copy the token (starts with `expo_...`)

3. **Set Token in Environment:**
   ```bash
   # Add to your CI/CD or local environment
   export EXPO_TOKEN=expo_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 2: Link Project to EAS

```bash
cd /app/mobile

# Install EAS CLI globally
npm install -g eas-cli

# Login to Expo
eas login

# Initialize/link project (if not already done)
eas init --id be604cc0-241c-44b4-b2d2-77d933214c9d
```

### Step 3: Android Build (APK/AAB)

**Option A: Development Build (APK)**
```bash
cd /app/mobile
eas build --platform android --profile development
```

**Option B: Production Build (AAB for Play Store)**
```bash
cd /app/mobile
eas build --platform android --profile production
```

**Android Credentials Setup:**
- EAS can auto-generate a keystore for you
- Or provide your own:
  1. Go to: https://expo.dev/accounts/[username]/projects/medmatch-ai-job-search-aid/credentials
  2. Upload keystore file
  3. Enter keystore password, key alias, key password

**Google Play Console Setup:**
1. Go to: https://play.google.com/console
2. Create new app → "MedMatch AI Job Search"
3. Complete store listing
4. For automated submissions, create a Service Account:
   - Go to: https://console.cloud.google.com/
   - Create service account with "Service Account User" role
   - Download JSON key → save as `/app/mobile/google-services.json`

### Step 4: iOS Build

**Requirements:**
- Apple Developer Account ($99/year): https://developer.apple.com/programs/
- Mac computer OR EAS Build (cloud)

**Apple Developer Setup:**

1. **Create App ID:**
   - Go to: https://developer.apple.com/account/resources/identifiers/list
   - Click "+" → Register App ID
   - Bundle ID: `com.cmuchina.medmatch`
   - Enable capabilities: Push Notifications, Sign in with Apple

2. **Create Distribution Certificate:**
   - Go to: https://developer.apple.com/account/resources/certificates/list
   - Click "+" → "Apple Distribution"
   - Upload CSR (or let EAS generate)

3. **Create Provisioning Profile:**
   - Go to: https://developer.apple.com/account/resources/profiles/list
   - Click "+" → "App Store Connect" (for distribution)
   - Select your App ID and certificate
   - Download and install

4. **App Store Connect Setup:**
   - Go to: https://appstoreconnect.apple.com/
   - Click "+" → "New App"
   - Fill in app details
   - Get `ascAppId` from URL (numbers after `/app/`)

**Build iOS:**
```bash
cd /app/mobile

# Development (simulator)
eas build --platform ios --profile preview-simulator

# Production (App Store)
eas build --platform ios --profile production
```

### Step 5: Running EAS Workflows

**Create workflow file:**
```bash
mkdir -p /app/mobile/.eas/workflows
```

Create `/app/mobile/.eas/workflows/create-production-builds.yml`:
```yaml
name: Production Builds
on:
  workflow_dispatch:
  
jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform android --profile production --non-interactive

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform ios --profile production --non-interactive
```

**Run workflow:**
```bash
# Requires EXPO_TOKEN to be set
npx eas-cli@latest workflow:run create-production-builds.yml

# Or trigger via GitHub Actions (if using GitHub)
# Add EXPO_TOKEN as a repository secret
```

### Expo/EAS Quick Links Summary

| Purpose | URL |
|---------|-----|
| Expo Dashboard | https://expo.dev/ |
| Create Access Token | https://expo.dev/accounts/[username]/settings/access-tokens |
| Project Credentials | https://expo.dev/accounts/cmuchina/projects/medmatch-ai-job-search-aid/credentials |
| EAS Build Status | https://expo.dev/accounts/cmuchina/projects/medmatch-ai-job-search-aid/builds |
| Apple Developer | https://developer.apple.com/account |
| App Store Connect | https://appstoreconnect.apple.com/ |
| Google Play Console | https://play.google.com/console |
| Google Cloud Console | https://console.cloud.google.com/ |

---

## 2. Video Generation (Sora 2)

### Issue
Video generation via OpenAI Sora 2 requires sufficient balance on your Emergent Universal Key.

### Solution

1. **Check Current Balance:**
   - Go to Emergent Dashboard → Profile → Universal Key

2. **Add Balance:**
   - Go to: Profile → Universal Key → Add Balance
   - Or enable "Auto Top-up" for uninterrupted service

3. **Pricing Reference:**
   - Sora 2 video generation costs vary by duration/quality
   - Typical: $0.05-0.15 per second of video

### Implementation Status
- Backend service ready: `/app/backend/services/video_service.py`
- API endpoint: `POST /api/tutorials/generate-video`

---

## 3. AI Avatar (D-ID) Integration

### What is D-ID?
D-ID creates AI-powered talking head videos from text and images.

### Setup Steps

1. **Create D-ID Account:**
   - Go to: https://www.d-id.com/
   - Sign up for account

2. **Get API Key:**
   - Go to: https://studio.d-id.com/account
   - Navigate to API Keys section
   - Create new API key

3. **Pricing:**
   - Free tier: 5 minutes of video/month
   - Lite: $5.99/month (10 minutes)
   - Pro: $49.99/month (unlimited)
   - API pricing: https://www.d-id.com/pricing

4. **Add to Environment:**
   ```bash
   # Add to /app/backend/.env
   D_ID_API_KEY=your_api_key_here
   ```

### Quick Links

| Purpose | URL |
|---------|-----|
| D-ID Homepage | https://www.d-id.com/ |
| D-ID Studio | https://studio.d-id.com/ |
| API Documentation | https://docs.d-id.com/ |
| Pricing | https://www.d-id.com/pricing |

---

## 4. Primary Source Verification (PSV) APIs

### Overview
PSV verifies professional credentials directly from issuing authorities.

### Provider Setup

#### 4.1 Propelus (Medical Licenses)
- Website: https://www.propelus.com/
- Contact: Sales team for API access
- Credentials verified: Medical licenses, DEA, state licenses

#### 4.2 Verisys (Healthcare Verification)
- Website: https://www.verisys.com/
- Contact: https://www.verisys.com/contact/
- Services: Sanctions screening, license verification

#### 4.3 FSMB (Federation of State Medical Boards)
- Website: https://www.fsmb.org/
- Services: Physician credential verification
- Contact: https://www.fsmb.org/contact-us/

#### 4.4 Credly (Digital Badges) - INTEGRATED
- Website: https://info.credly.com/
- API Docs: https://www.credly.com/docs/api
- Status: ✅ OAuth flow implemented

#### 4.5 IAF CertSearch (ISO Certifications)
- Website: https://www.iaf.nu/articles/IAF_CertSearch/300
- Access: Public search available

#### 4.6 ASQ Registry (Quality Certifications)
- Website: https://asq.org/cert/registry
- Certifications: CQE, CQI, CSSBB, CMQ/OE

### Implementation
```bash
# Add to /app/backend/.env (when obtained)
PROPELUS_API_KEY=your_key
VERISYS_API_KEY=your_key
FSMB_API_KEY=your_key
```

---

## 5. LinkedIn Integration

### Setup Steps

1. **Create LinkedIn App:**
   - Go to: https://www.linkedin.com/developers/apps
   - Click "Create App"
   - Fill in details:
     - App name: MedMatch AI Job Search
     - LinkedIn Page: Create or link company page
     - App logo: Upload logo

2. **Configure Products:**
   - Go to "Products" tab
   - Request access to:
     - "Sign In with LinkedIn using OpenID Connect"
     - "Share on LinkedIn" (optional)

3. **Get Credentials:**
   - Go to "Auth" tab
   - Copy:
     - Client ID
     - Client Secret

4. **Set Redirect URLs:**
   - Add: `https://lumi-ai-hub.preview.emergentagent.com/api/linkedin/callback`

5. **Add to Environment:**
   ```bash
   # Add to /app/backend/.env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   ```

### Quick Links

| Purpose | URL |
|---------|-----|
| LinkedIn Developers | https://www.linkedin.com/developers/ |
| Create App | https://www.linkedin.com/developers/apps/new |
| API Documentation | https://learn.microsoft.com/en-us/linkedin/ |
| OAuth 2.0 Guide | https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow |

---

## 6. Cloud Storage Integrations

### 6.1 Dropbox Integration

1. **Create Dropbox App:**
   - Go to: https://www.dropbox.com/developers/apps
   - Click "Create app"
   - Choose "Scoped access" → "Full Dropbox"
   - Name: "MedMatch Integration"

2. **Get Credentials:**
   - Copy App key and App secret
   - Set OAuth 2 redirect: `https://lumi-ai-hub.preview.emergentagent.com/api/cloud/dropbox/callback`

3. **Add to Environment:**
   ```bash
   DROPBOX_APP_KEY=your_app_key
   DROPBOX_APP_SECRET=your_app_secret
   ```

### 6.2 OneDrive/Microsoft Integration

1. **Register Azure App:**
   - Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   - Click "New registration"
   - Name: "MedMatch Integration"
   - Redirect URI: `https://lumi-ai-hub.preview.emergentagent.com/api/cloud/onedrive/callback`

2. **Configure Permissions:**
   - API permissions → Add → Microsoft Graph
   - Add: `Files.Read`, `Files.ReadWrite`, `User.Read`

3. **Get Credentials:**
   - Copy Application (client) ID
   - Create client secret under "Certificates & secrets"

4. **Add to Environment:**
   ```bash
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_client_secret
   ```

### Quick Links

| Service | Developer Portal |
|---------|-----------------|
| Dropbox | https://www.dropbox.com/developers |
| Microsoft Azure | https://portal.azure.com/ |
| OneDrive API Docs | https://learn.microsoft.com/en-us/onedrive/developer/ |

---

## 7. Payment Integrations

### 7.1 Stripe - INTEGRATED ✅

Stripe is already configured in the pod environment.

**Test Keys Location:**
- Available in pod environment
- Test mode enabled for development

**Dashboard:** https://dashboard.stripe.com/

### 7.2 PayPal Integration

1. **Create PayPal Developer Account:**
   - Go to: https://developer.paypal.com/
   - Sign up or log in

2. **Create App:**
   - Go to: https://developer.paypal.com/dashboard/applications/sandbox
   - Click "Create App"
   - Name: "MedMatch"

3. **Get Credentials:**
   - Copy Client ID and Secret
   - Note: Use Sandbox credentials for testing

4. **Add to Environment:**
   ```bash
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_CLIENT_SECRET=your_client_secret
   PAYPAL_MODE=sandbox  # or 'live' for production
   ```

### Quick Links

| Service | URL |
|---------|-----|
| Stripe Dashboard | https://dashboard.stripe.com/ |
| PayPal Developer | https://developer.paypal.com/ |
| PayPal Sandbox | https://developer.paypal.com/dashboard/applications/sandbox |

---

## Summary: All Required Credentials

```bash
# /app/backend/.env additions needed:

# Expo/EAS (set as environment variable, not in .env)
# export EXPO_TOKEN=expo_xxxxxxxx

# AI Services
D_ID_API_KEY=                    # D-ID AI Avatar
# OPENAI key already configured via Emergent

# Professional Verification
PROPELUS_API_KEY=                # Medical license verification
VERISYS_API_KEY=                 # Healthcare verification
FSMB_API_KEY=                    # Physician credentials

# Social/Professional
LINKEDIN_CLIENT_ID=              # LinkedIn integration
LINKEDIN_CLIENT_SECRET=

# Cloud Storage
DROPBOX_APP_KEY=                 # Dropbox integration
DROPBOX_APP_SECRET=
MICROSOFT_CLIENT_ID=             # OneDrive integration
MICROSOFT_CLIENT_SECRET=

# Payments
PAYPAL_CLIENT_ID=                # PayPal (Stripe already configured)
PAYPAL_CLIENT_SECRET=
PAYPAL_MODE=sandbox
```

---

## Status Dashboard

| Integration | Status | Blocker | Action Required |
|------------|--------|---------|-----------------|
| Android Build | 🔴 Blocked | EXPO_TOKEN | Create token at expo.dev |
| iOS Build | 🔴 Blocked | Apple Developer + Mac | Setup certificates |
| Video Generation | 🔴 Blocked | Universal Key Balance | Add funds |
| D-ID Avatar | 🔴 Blocked | D_ID_API_KEY | Create D-ID account |
| LinkedIn | 🔴 Blocked | API Credentials | Create LinkedIn app |
| PSV APIs | 🔴 Blocked | Multiple API keys | Contact providers |
| Dropbox | 🔴 Blocked | App credentials | Create Dropbox app |
| OneDrive | 🔴 Blocked | Azure credentials | Register Azure app |
| PayPal | 🔴 Blocked | API credentials | Create PayPal app |
| Stripe | ✅ Ready | None | Already configured |
| Credly | ✅ Ready | None | OAuth implemented |
| Google Auth | ✅ Ready | None | Already configured |

---

## Next Steps

1. **Priority 1:** Get EXPO_TOKEN for mobile builds
2. **Priority 2:** Add Universal Key balance for video generation
3. **Priority 3:** Set up LinkedIn integration
4. **Priority 4:** D-ID for AI avatars

For questions, refer to the official documentation links provided above.
