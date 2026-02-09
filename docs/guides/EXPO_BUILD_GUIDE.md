# MedMatch Expo Build - Step-by-Step Guide

## 🎯 Prerequisites Completed
- ✅ Expo Token: `tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez`
- ✅ Project ID: `be604cc0-241c-44b4-b2d2-77d933214c9d`
- ✅ Project configured in `/app/mobile/`

---

## 📱 Option A: Build from YOUR Local Computer (Recommended)

### Step 1: Install Prerequisites
```bash
# Install Node.js (if not installed)
# Download from: https://nodejs.org/en/download/

# Install EAS CLI globally
npm install -g eas-cli

# Verify installation
eas --version
```

### Step 2: Clone/Download the Mobile Folder
Download the `/app/mobile/` folder to your local computer.

### Step 3: Set Up Environment
```bash
# Navigate to mobile folder
cd mobile

# Install dependencies
yarn install

# Set your Expo token
export EXPO_TOKEN=tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez

# On Windows PowerShell:
$env:EXPO_TOKEN="tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez"

# On Windows CMD:
set EXPO_TOKEN=tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez
```

### Step 4: Login to Expo
```bash
eas login
# Enter your Expo credentials (email: cmuchina@hotmail.com)
```

### Step 5: Build Android APK (Development)
```bash
# Development build (for testing)
eas build --platform android --profile development

# This will:
# 1. Bundle your JavaScript code
# 2. Upload to EAS Build servers
# 3. Build an APK file
# 4. Provide a download link when complete
```

### Step 6: Build Android AAB (Production - Play Store)
```bash
eas build --platform android --profile production
```

### Step 7: Build iOS (Requires Apple Developer Account)
```bash
# Simulator build (no Apple account needed)
eas build --platform ios --profile preview-simulator

# Production build (requires Apple Developer)
eas build --platform ios --profile production
```

---

## 📱 Option B: Build from This Development Environment

### Quick Commands
```bash
cd /app/mobile

# Set token
export EXPO_TOKEN=tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez

# Login (interactive)
npx eas-cli login

# Build Android
npx eas-cli build --platform android --profile development --non-interactive

# Check build status
npx eas-cli build:list
```

---

## 🔗 Important Links

| Purpose | URL |
|---------|-----|
| View Build Status | https://expo.dev/accounts/cmuchina/projects/medmatch-ai-job-search-aid/builds |
| Expo Dashboard | https://expo.dev/ |
| Download APK | (Link provided after build completes) |

---

## 📋 Build Profiles Available

| Profile | Platform | Output | Use Case |
|---------|----------|--------|----------|
| `development` | Android | APK | Testing on device |
| `preview` | Both | APK/IPA | Internal testing |
| `preview-simulator` | iOS | Simulator | iOS testing without device |
| `production` | Both | AAB/IPA | App Store submission |

---

## 🔧 Troubleshooting

### "Not logged in" Error
```bash
eas logout
eas login
```

### Token Not Working
```bash
# Verify token is set
echo $EXPO_TOKEN

# Should output: tbeqKzrtQzTxyLSAhAPhC-vfkd7_Egmegr-On6Ez
```

### Build Failed
1. Check build logs at: https://expo.dev/accounts/cmuchina/projects/medmatch-ai-job-search-aid/builds
2. Look for specific error messages
3. Common fixes:
   - Run `yarn install` again
   - Clear cache: `npx expo start --clear`

---

## 📞 Need More Help?

1. **Expo Documentation**: https://docs.expo.dev/build/introduction/
2. **EAS Build Reference**: https://docs.expo.dev/eas/
3. **Build Troubleshooting**: https://docs.expo.dev/build-reference/troubleshooting/
