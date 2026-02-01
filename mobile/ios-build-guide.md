# MedMatch iOS Build Guide

## Prerequisites

1. **Apple Developer Account** (enrolled in Apple Developer Program - $99/year)
2. **Xcode** (macOS only) - for local builds
3. **Expo EAS CLI** - for cloud builds

## Build Options

### Option 1: EAS Cloud Build (Recommended)

EAS Build handles iOS provisioning and code signing automatically in the cloud.

#### Step 1: Unlock Apple Account
If your Apple Developer account was locked, unlock it at:
https://iforgot.apple.com

#### Step 2: Login to EAS
```bash
cd /app/mobile
npx eas login
```

#### Step 3: Configure iOS Credentials
```bash
# This will prompt for Apple ID and password
npx eas credentials -p ios
```

**When prompted:**
- Apple ID: `cmuchina@hotmail.com`
- Password: Your Apple ID password (NOT app-specific password)
- If 2FA is enabled, enter the verification code sent to your device

#### Step 4: Build for iOS
```bash
# Development build (for testing on physical devices)
npx eas build --platform ios --profile development

# Preview build (for internal distribution)
npx eas build --platform ios --profile preview

# Production build (for App Store)
npx eas build --platform ios --profile production
```

### Option 2: Local Build (macOS Required)

#### Step 1: Generate native iOS project
```bash
cd /app/mobile
npx expo prebuild --platform ios
```

#### Step 2: Open in Xcode
```bash
open ios/MedMatchAIJobSearch.xcworkspace
```

#### Step 3: Configure Signing in Xcode
1. Select the project in the navigator
2. Select "Signing & Capabilities" tab
3. Check "Automatically manage signing"
4. Select your team (Apple Developer account)
5. Xcode will create/download necessary provisioning profiles

#### Step 4: Build and Archive
- Select "Any iOS Device" as the destination
- Product → Archive
- Once archived, distribute through App Store Connect or TestFlight

---

## Current EAS Configuration

### app.json (iOS section)
```json
{
  "expo": {
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.medmatch.app",
      "infoPlist": {
        "NSCameraUsageDescription": "MedMatch needs camera access for ID verification and video interviews",
        "NSMicrophoneUsageDescription": "MedMatch needs microphone access for voice coaching and interviews",
        "NSPhotoLibraryUsageDescription": "MedMatch needs photo access to upload your resume documents"
      }
    }
  }
}
```

### eas.json (iOS build profiles)
```json
{
  "build": {
    "development": {
      "ios": {
        "resourceClass": "m-medium",
        "simulator": true
      }
    },
    "preview": {
      "ios": {
        "resourceClass": "m-medium",
        "credentialsSource": "local"
      }
    },
    "production": {
      "ios": {
        "resourceClass": "m-medium",
        "autoIncrement": true
      }
    }
  }
}
```

---

## Apple App Store Connect Setup

### Step 1: Create App in App Store Connect
1. Go to https://appstoreconnect.apple.com
2. My Apps → "+" → New App
3. Fill in:
   - Platform: iOS
   - Name: MedMatch AI Job Search
   - Primary Language: English (US)
   - Bundle ID: com.medmatch.app
   - SKU: medmatch-ios-2026

### Step 2: Configure App Information
- Category: Business
- Subcategory: Productivity
- Content Rights: No third-party content
- Age Rating: 4+ (no objectionable content)

### Step 3: Prepare for Submission
Required assets:
- App Icon (1024x1024 PNG, no transparency)
- Screenshots for each device size:
  - iPhone 6.7" (1290x2796)
  - iPhone 6.5" (1284x2778)
  - iPhone 5.5" (1242x2208)
  - iPad Pro 12.9" (2048x2732)

---

## Troubleshooting

### "Apple ID locked" Error
1. Go to https://iforgot.apple.com
2. Enter your Apple ID email
3. Follow password reset or unlock instructions
4. Wait 24 hours before retrying if account was locked for security

### "Code signing failed" Error
```bash
# Reset iOS credentials
npx eas credentials -p ios --clear

# Reconfigure
npx eas credentials -p ios
```

### "Provisioning profile not found" Error
- Make sure your Apple Developer account is active ($99/year subscription)
- Check that the bundle identifier matches in App Store Connect

### Build fails with "No valid signing identity"
For local builds:
1. Open Keychain Access
2. Check that your Apple Development certificate is valid
3. If expired, revoke and recreate in Apple Developer portal

---

## Quick Commands Reference

```bash
# Check current credentials
npx eas credentials -p ios

# Build for simulator (development)
npx eas build --platform ios --profile development

# Build for physical devices (internal testing)
npx eas build --platform ios --profile preview

# Build for App Store
npx eas build --platform ios --profile production

# Submit to App Store
npx eas submit --platform ios

# View build status
npx eas build:list --platform ios
```

---

## App-Specific Password (for submitting to App Store)

If you need to submit to the App Store using EAS Submit:
1. Go to https://appleid.apple.com
2. Sign In → Security → App-Specific Passwords → Generate
3. Name it "EAS Submit"
4. Copy the generated password
5. Use when prompted during `eas submit`

---

## Contact

For build issues:
- Expo EAS Support: https://expo.dev/support
- Apple Developer Support: https://developer.apple.com/support/

---

Last Updated: February 1, 2026
