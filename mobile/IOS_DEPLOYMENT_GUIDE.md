# AI Suite - iOS Deployment Guide

Complete guide for building, testing, and deploying the MedMatch iOS app to the App Store via TestFlight.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Certificate & Provisioning Setup](#certificate--provisioning-setup)
4. [Build Configurations](#build-configurations)
5. [Building for iOS](#building-for-ios)
6. [TestFlight Distribution](#testflight-distribution)
7. [App Store Submission](#app-store-submission)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference Commands](#quick-reference-commands)

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Apple Developer Account | Enrolled in Apple Developer Program ($99/year) |
| Apple ID | `cmuchina@hotmail.com` |
| Apple Team ID | `96879J9FZY` |
| Bundle Identifier | `com.cmuchina.medmatch` |
| EAS Project ID | `be604cc0-241c-44b4-b2d2-77d933214c9d` |
| Node.js | v18+ |
| EAS CLI | v12+ (`npm install -g eas-cli`) |

---

## Environment Setup

### Step 1: Install EAS CLI

```bash
npm install -g eas-cli
```

### Step 2: Login to Expo

```bash
cd /app/mobile
npx eas login
# Enter your Expo account credentials
```

### Step 3: Verify Project Configuration

```bash
# Check that eas.json and app.json are properly configured
cat app.json | python3 -c "import sys,json; d=json.load(sys.stdin)['expo']; print(f'App: {d[\"name\"]}'); print(f'Bundle ID: {d[\"ios\"][\"bundleIdentifier\"]}'); print(f'Version: {d[\"version\"]}')"
```

### Step 4: Verify API URL

All build profiles in `eas.json` use:
```
EXPO_PUBLIC_API_URL=https://medmatch-jobs-dev.preview.emergentagent.com
```

Update this to your production URL before App Store submission.

---

## Certificate & Provisioning Setup

### Existing Credentials (Located in `/app/mobile/ios_certs/`)

| File | Purpose |
|------|---------|
| `AuthKey_CG3QVGRB45.p8` | Apple Push Notification (APNs) key |
| `distribution.cer` | iOS Distribution certificate |
| `ios_distribution.csr` | Certificate Signing Request |
| `ios_distribution.key` | Private key for distribution |
| `ios_distribution.p12` | PKCS12 bundle (cert + key) |

### Option A: Let EAS Manage Credentials (Recommended)

```bash
npx eas credentials -p ios
```

EAS will:
- Create/download distribution certificates
- Generate provisioning profiles  
- Store them securely in the cloud

When prompted:
- **Apple ID:** `cmuchina@hotmail.com`
- **Password:** Your Apple ID password
- **2FA:** Enter verification code sent to your trusted device

### Option B: Use Local Credentials

If you prefer using the existing certificates:

1. Set `credentialsSource` to `"local"` in `eas.json`:
```json
{
  "build": {
    "production": {
      "ios": {
        "credentialsSource": "local"
      }
    }
  }
}
```

2. Create `credentials.json` in `/app/mobile/`:
```json
{
  "ios": {
    "provisioningProfilePath": "./MedMatch_Distribution.mobileprovision",
    "distributionCertificate": {
      "path": "./ios_certs/ios_distribution.p12",
      "password": "YOUR_P12_PASSWORD"
    }
  }
}
```

---

## Build Configurations

### Development (Simulator Testing)

```bash
npx eas build --platform ios --profile development
```
- Runs on iOS Simulator only
- No real device signing needed
- Fast iteration for testing

### Preview (Internal Device Testing)

```bash
npx eas build --platform ios --profile preview
```
- Installable on registered devices
- Uses Ad Hoc provisioning
- Distribute via QR code or direct link

### Production (App Store / TestFlight)

```bash
npx eas build --platform ios --profile production
```
- App Store-signed build
- Auto-increments build number
- Ready for TestFlight or App Store submission

---

## Building for iOS

### Full Build Flow

```bash
cd /app/mobile

# 1. Ensure dependencies are installed
yarn install

# 2. Run the production build
npx eas build --platform ios --profile production

# 3. Monitor build status
npx eas build:list --platform ios --limit 5
```

### Build Output

After a successful build, EAS provides:
- **Build URL:** Direct download link for the `.ipa` file
- **Build ID:** Unique identifier for submission
- **QR Code:** Scan to install (preview builds only)

### Local Build (macOS Only)

```bash
# Generate native iOS project
npx expo prebuild --platform ios --clean

# Open in Xcode
open ios/MedMatchAIJobSearch.xcworkspace

# In Xcode:
# 1. Select "Any iOS Device" as destination
# 2. Product -> Archive
# 3. Distribute -> App Store Connect
```

---

## TestFlight Distribution

### Step 1: Submit Build to App Store Connect

```bash
# Submit the latest build
npx eas submit --platform ios --latest

# Or submit a specific build
npx eas submit --platform ios --id BUILD_ID
```

When prompted:
- **Apple ID:** `cmuchina@hotmail.com`
- **App-Specific Password:** Generate at https://appleid.apple.com
  (Security -> App-Specific Passwords -> Generate -> Name it "EAS Submit")
- **App Store Connect App ID:** Found in your app's URL on App Store Connect

### Step 2: Configure in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Navigate to **My Apps** -> **MedMatch AI Job Search**
3. Go to **TestFlight** tab

### Step 3: Set Up Internal Testing

1. Click **Internal Testing** -> **+** -> Create group
2. Name: "AI Suite Internal Testers"
3. Add team members by email
4. Builds are available immediately (no review needed)
5. Limit: 100 internal testers

### Step 4: Set Up External Testing

1. Click **External Testing** -> **+** -> Create group
2. Name: "AI Suite Beta Testers"
3. Add testers by email OR enable **Public Link**
4. **Important:** External builds require Beta App Review (24-48 hours)
5. Limit: 10,000 external testers

### Step 5: Provide Test Information

For Beta App Review:
- **Test Account:** `test@medmatch.io` / `TestPassword123!`
- **Contact:** Your email for review communication
- **What to Test:** Describe key features to test

---

## App Store Submission

### Required App Information

| Field | Value |
|-------|-------|
| App Name | MedMatch AI Job Search |
| Primary Language | English (US) |
| Category | Business |
| Subcategory | Productivity |
| Bundle ID | `com.cmuchina.medmatch` |
| SKU | `medmatch-ios-2026` |
| Content Rating | 4+ |
| Price | Free (with in-app purchases) |

### Required Screenshots

| Device | Resolution |
|--------|------------|
| iPhone 6.7" (15 Pro Max) | 1290 x 2796 |
| iPhone 6.5" (14 Plus) | 1284 x 2778 |
| iPhone 5.5" (8 Plus) | 1242 x 2208 |
| iPad Pro 12.9" | 2048 x 2732 |

### App Privacy Details

Declare data collection in App Store Connect:
- **Contact Info:** Email (for account creation)
- **Identifiers:** User ID
- **Usage Data:** Analytics
- **Location:** Approximate location (for job search)

### Submission Command

```bash
npx eas submit --platform ios --latest --non-interactive
```

---

## Troubleshooting

### Apple ID Locked
1. Go to https://iforgot.apple.com
2. Follow unlock instructions
3. Wait 24 hours before retrying

### Code Signing Failed
```bash
# Clear all iOS credentials
npx eas credentials -p ios --clear

# Reconfigure from scratch
npx eas credentials -p ios
```

### Build Fails: "No valid signing identity"
- Ensure Apple Developer subscription is active
- Revoke and recreate certificates if expired
- For local builds, check Keychain Access

### Provisioning Profile Not Found
- Verify bundle ID matches App Store Connect
- Check that device UDIDs are registered (for preview builds)

### "Requires Xcode 16" Error
- EAS Cloud builds use the latest Xcode automatically
- For local builds, update Xcode from the Mac App Store

### Push Notifications Not Working
- Verify APNs key (`AuthKey_CG3QVGRB45.p8`) is configured
- Check `expo-notifications` plugin in `app.json`
- Test with: `npx eas credentials -p ios` (verify push key)

---

## Quick Reference Commands

```bash
# === Account & Auth ===
npx eas login                                    # Login to Expo
npx eas whoami                                   # Check current account

# === Credentials ===
npx eas credentials -p ios                       # Manage iOS credentials
npx eas credentials -p ios --clear               # Clear credentials

# === Build ===
npx eas build --platform ios --profile development  # Simulator build
npx eas build --platform ios --profile preview      # Device testing
npx eas build --platform ios --profile production   # App Store build
npx eas build:list --platform ios --limit 5         # List recent builds
npx eas build:view BUILD_ID                         # View build details

# === Submit ===
npx eas submit --platform ios --latest           # Submit latest build
npx eas submit --platform ios --id BUILD_ID      # Submit specific build
npx eas submit:list --platform ios               # List submissions

# === Local Development ===
npx expo prebuild --platform ios --clean         # Generate native project
npx expo start --ios                             # Start dev server for iOS
npx expo run:ios                                 # Build and run locally

# === Updates (OTA) ===
npx eas update --branch production               # Push OTA update
npx eas update:list                               # List OTA updates
```

---

## CI/CD: GitHub Actions Workflow

Save as `.github/workflows/ios-build.yml`:

```yaml
name: iOS Build & Deploy
on:
  push:
    branches: [main]
    paths:
      - 'mobile/**'

jobs:
  build-ios:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18

      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - run: yarn install --frozen-lockfile
        working-directory: mobile

      - name: Build iOS
        run: npx eas build --platform ios --profile production --non-interactive
        working-directory: mobile

      - name: Submit to TestFlight
        run: npx eas submit --platform ios --latest --non-interactive
        working-directory: mobile
        env:
          EXPO_APPLE_ID: ${{ secrets.APPLE_ID }}
          EXPO_APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
```

Required GitHub Secrets:
- `EXPO_TOKEN`: Expo access token
- `APPLE_ID`: `cmuchina@hotmail.com`
- `APPLE_APP_SPECIFIC_PASSWORD`: Generated from appleid.apple.com

---

Last Updated: February 2026
