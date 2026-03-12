# AI Suite - Multi-Platform Deployment Readiness

Complete deployment guide for all supported platforms.

---

## Platform Status Overview

| Platform | Status | Build Tool | Output |
|----------|--------|------------|--------|
| Web (PWA/TWA) | READY | `yarn build` | Static bundle |
| Desktop - Windows | READY | `electron-builder --win` | NSIS Installer + Portable |
| Desktop - macOS | READY | `electron-builder --mac` | DMG + ZIP (x64/arm64) |
| Desktop - Linux | READY | `electron-builder --linux` | AppImage |
| Mobile - Android | READY | `eas build --platform android` | APK / AAB |
| Mobile - iOS | READY | `eas build --platform ios` | IPA (TestFlight/App Store) |
| Microsoft Teams | CONFIGURED | Teams Admin Center upload | Teams App Package |
| Microsoft Outlook | CONFIGURED | Centralized Deployment | Outlook Add-in |

---

## 1. Web (PWA / TWA)

### Build
```bash
cd /app/frontend
yarn build
```

### PWA Features
- Full offline support via service worker
- Push notifications (VAPID configured)
- Install prompt for Add to Home Screen
- App shortcuts (KARAU, ENZI, MedMatch, Schedule)
- Share target (receive shared content)
- Protocol handlers (`web+karau://`, `web+enzi://`)
- Background sync for offline actions

### TWA (Trusted Web Activity) for Android
The enhanced `manifest.json` supports TWA wrapping. To create a TWA:
1. Use [Bubblewrap](https://github.com/nicholasgasior/nicholasgasior.github.io/issues/24) or [PWABuilder](https://www.pwabuilder.com/)
2. Point to `https://ai-suite-test.preview.emergentagent.com`
3. The manifest includes `related_applications` for Play Store listing

### Deployment
```bash
# Build production bundle
cd /app/frontend && yarn build

# Output in /app/frontend/build/
# Deploy to any static hosting (Vercel, Netlify, S3+CloudFront)
```

---

## 2. Desktop (Electron)

### Location: `/app/desktop/`

### Prerequisites
- Node.js 18+
- For cross-compilation: Wine (Windows on Linux/Mac), Xcode CLI (macOS)

### Build Commands
```bash
cd /app/desktop
yarn install

# Build for specific platform
./build.sh win      # Windows (NSIS + Portable)
./build.sh mac      # macOS (DMG + ZIP, x64/arm64)
./build.sh linux    # Linux (AppImage)
./build.sh all      # All platforms

# Output in /app/desktop/dist/
```

### Features
- System tray with portal quick-access (KARAU, ENZI, MedMatch)
- Auto-updates via GitHub Releases
- Offline detection with graceful fallback
- Native notifications
- Deep linking (`medmatch://` protocol)
- Keyboard shortcuts for all portal navigation
- macOS: hiddenInset title bar, Apple Silicon support
- Windows: NSIS installer with Start Menu shortcut
- Linux: AppImage (no installation needed)

### Auto-Update Configuration
Update the `publish` section in `desktop/package.json`:
```json
{
  "publish": {
    "provider": "github",
    "owner": "charlesmuchina-wq",
    "repo": "MedMatch",
    "releaseType": "release"
  }
}
```

### Code Signing (Production)
- **Windows:** Requires EV code signing certificate
- **macOS:** Requires Apple Developer ID certificate + notarization
- **Linux:** No signing required for AppImage

---

## 3. Mobile - Android

### Location: `/app/mobile/`

### Build Commands
```bash
cd /app/mobile
yarn install

# Development (APK for testing)
npx eas build --platform android --profile development

# Preview (APK for internal distribution)
npx eas build --platform android --profile preview

# Production (AAB for Play Store)
npx eas build --platform android --profile production
```

### Play Store Submission
```bash
# Submit to Google Play (requires google-services.json)
npx eas submit --platform android --latest
```

### Permissions Configured
- Camera (ID verification, video interviews)
- Microphone (voice coaching, interviews)
- Storage (resume upload)
- Vibration (notifications)
- Biometric (fingerprint auth)

---

## 4. Mobile - iOS

### Location: `/app/mobile/`
### Detailed Guide: `/app/mobile/IOS_DEPLOYMENT_GUIDE.md`

### Build Commands
```bash
cd /app/mobile
yarn install

# Development (Simulator)
npx eas build --platform ios --profile development

# Preview (Internal testing on devices)
npx eas build --platform ios --profile preview

# Production (TestFlight / App Store)
npx eas build --platform ios --profile production
```

### Certificates Available
| File | Location |
|------|----------|
| APNs Key | `/app/mobile/ios_certs/AuthKey_CG3QVGRB45.p8` |
| Distribution Cert | `/app/mobile/ios_certs/distribution.cer` |
| P12 Bundle | `/app/mobile/ios_certs/ios_distribution.p12` |
| Provisioning Profile | `/app/mobile/MedMatch_Distribution.mobileprovision` |

### TestFlight Submission
```bash
npx eas submit --platform ios --latest
```

### Key iOS Info
- Bundle ID: `com.cmuchina.medmatch`
- Apple Team: `96879J9FZY`
- Apple ID: `cmuchina@hotmail.com`

---

## 5. Microsoft Teams

### Location: `/app/frontend/public/msteams-app.json`

### Features Configured
- **Personal Tabs:** ENZI Messenger, AI KARAU Meetings, MedMatch Jobs
- **Configurable Tabs:** For team channels and meeting side panels
- **Compose Extensions:** Schedule KARAU meetings and search jobs from Teams compose box
- **Valid Domains:** ai-suite-test, aikarau.com, enzilink.com

### Deployment Steps

1. **Package the Teams App:**
   ```bash
   # Create a ZIP containing:
   # - msteams-app.json (renamed to manifest.json)
   # - color-icon.png (192x192 full-color icon)
   # - outline-icon.png (32x32 outline icon)
   
   cd /app/frontend/public
   mkdir -p teams-package
   cp msteams-app.json teams-package/manifest.json
   cp icons/icon-192x192.png teams-package/color-icon.png
   cp icons/icon-96x96.png teams-package/outline-icon.png
   cd teams-package && zip ../ai-suite-teams.zip *
   ```

2. **Upload to Teams Admin Center:**
   - Go to https://admin.teams.microsoft.com
   - Navigate to Teams Apps -> Manage Apps -> Upload
   - Upload `ai-suite-teams.zip`

3. **Or Sideload for Testing:**
   - In Teams, go to Apps -> Manage your apps -> Upload a custom app
   - Select `ai-suite-teams.zip`

### Azure AD Configuration
- **App ID:** `lumi-ai-hub-1` (from backend `.env` AZURE_CLIENT_ID)
- **Tenant ID:** Update in Azure Portal for production
- **API Permissions:** User.Read, ChannelMessage.Read.Group

---

## 6. Microsoft Outlook

### Location: `/app/frontend/public/outlook-addin.xml`

### Features Configured
- **Appointment Compose:** "Add AI KARAU Meeting" button when creating events
- **Appointment Read:** "Join AI KARAU Meeting" button for existing events  
- **Message Read:** "Create KARAU Meeting" from email conversations

### Deployment Steps

1. **Centralized Deployment (Recommended):**
   - Go to Microsoft 365 Admin Center -> Settings -> Integrated Apps
   - Click "Upload custom apps"
   - Upload `outlook-addin.xml`
   - Assign to users/groups

2. **Sideload for Testing:**
   - In Outlook Web, go to Settings -> Manage Integrations
   - Click "My add-ins" -> "Add a custom add-in" -> "Add from file"
   - Upload `outlook-addin.xml`

3. **Verify Functionality:**
   - Create a new calendar event -> Look for "AI KARAU" group in ribbon
   - Read an email -> Look for "Create KARAU Meeting" button

---

## Pre-Deployment Checklist

### Environment Variables to Update for Production

| Variable | Current (Preview) | Production |
|----------|-------------------|------------|
| `REACT_APP_BACKEND_URL` | `https://ai-suite-test.preview.emergentagent.com` | Your production URL |
| `EXPO_PUBLIC_API_URL` | Same as above | Your production URL |
| `APP_URL` (Electron) | Same as above | Your production URL |
| `CORS_ORIGINS` | Includes preview URL | Update to production domains |
| `WEBAUTHN_RP_ID` | Preview domain | Production domain |

### Assets Needed for Store Submissions

| Asset | Spec | For |
|-------|------|-----|
| App Icon | 1024x1024 PNG | iOS App Store, Google Play |
| Feature Graphic | 1024x500 PNG | Google Play |
| Screenshots | Various sizes | Both stores |
| Privacy Policy URL | Public URL | Both stores, Microsoft |
| Terms of Service URL | Public URL | Both stores, Microsoft |

---

Last Updated: February 2026
