# MedMatch iOS TestFlight Configuration Guide

## Overview

This guide covers setting up TestFlight beta testing for the MedMatch iOS app using Expo EAS Submit.

## Prerequisites

1. **Apple Developer Account** (enrolled in Apple Developer Program)
2. **App Store Connect Access** (Admin or App Manager role)
3. **EAS CLI** installed and logged in
4. **iOS Build Ready** (production or preview profile)

---

## Part 1: App Store Connect Setup

### Step 1: Create the App in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" → "+" → "New App"
3. Fill in the details:
   - **Platform:** iOS
   - **Name:** MedMatch AI Job Search
   - **Primary Language:** English (US)
   - **Bundle ID:** com.medmatch.app
   - **SKU:** medmatch-ios-app-001
   - **User Access:** Full Access

### Step 2: Configure App Information

Navigate to "App Information" and fill:
- **Category:** Business
- **Subcategory:** Productivity
- **Content Rights:** "This app does not contain third-party content"
- **Age Rating:** 4+ (No objectionable content)

### Step 3: Set Up TestFlight

1. Go to the "TestFlight" tab
2. Click "Internal Testing" → "+" to create a group
3. Name it "MedMatch Internal Testers"
4. Add team members by email

---

## Part 2: EAS Submit Configuration

### eas.json Submit Profile

The submit configuration is already in `/app/mobile/eas.json`:

```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "cmuchina@hotmail.com",
        "ascAppId": "YOUR_APP_STORE_CONNECT_APP_ID",
        "appleTeamId": "96879J9FZY"
      }
    }
  }
}
```

### Get Your App Store Connect App ID

1. Go to App Store Connect → Your App
2. Look at the URL: `https://appstoreconnect.apple.com/apps/XXXXXXXXXX`
3. The number (XXXXXXXXXX) is your `ascAppId`
4. Update eas.json with this ID

---

## Part 3: Build and Submit to TestFlight

### Step 1: Create a Production Build

```bash
cd /app/mobile

# Build for App Store (production)
npx eas build --platform ios --profile production
```

### Step 2: Submit to TestFlight

```bash
# Submit the latest build
npx eas submit --platform ios --latest

# Or submit a specific build
npx eas submit --platform ios --id YOUR_BUILD_ID
```

### Step 3: Authenticate

When prompted, enter:
- **Apple ID:** cmuchina@hotmail.com
- **App-Specific Password:** Generate at https://appleid.apple.com (Security → App-Specific Passwords)

---

## Part 4: Internal Testing Setup

### Add Internal Testers

Internal testers are members of your Apple Developer team.

1. Go to App Store Connect → Your App → TestFlight
2. Click "Internal Testing" → Your Group
3. Click "+" → Add testers by email
4. Testers will receive an invitation email

### Internal Tester Limits
- Up to 100 internal testers
- Must be Apple Developer team members
- Builds available immediately (no review required)

---

## Part 5: External Testing Setup

### Create External Testing Group

1. Go to TestFlight → "External Testing"
2. Click "+" to create a group
3. Name it "MedMatch Beta Testers"

### Add External Testers

External testers can be anyone with an iOS device.

**Option 1: Email Invitations**
1. Click "+" in your external group
2. Enter email addresses
3. Testers receive TestFlight invitation

**Option 2: Public Link**
1. Click "Enable Public Link"
2. Share the link publicly
3. Anyone can join up to your limit

### External Tester Limits
- Up to 10,000 external testers
- Requires Beta App Review (usually 24-48 hours)
- Builds expire after 90 days

---

## Part 6: Beta App Review

### What Gets Reviewed

Apple reviews:
- App functionality
- Privacy policy
- Content guidelines compliance
- Metadata (description, screenshots)

### Prepare for Review

1. **Test Information:**
   - Sign-in credentials for reviewers
   - Contact information
   - Notes about what to test

2. **Required Metadata:**
   - App description
   - What to test
   - Privacy policy URL

### Submit for Beta Review

1. Select your build in TestFlight
2. Click "Submit for Beta App Review"
3. Fill in the test information
4. Submit

Review typically takes 24-48 hours.

---

## Part 7: Managing Builds

### Version and Build Numbers

- **Version:** Visible to users (1.0.0, 1.1.0)
- **Build:** Internal identifier (1, 2, 3...)

EAS auto-increments builds with `autoIncrement: true`.

### Expire/Remove Builds

1. Go to TestFlight → Builds
2. Click on the build
3. Click "Expire Build" or "Remove from Testing"

### Build Groups

You can add the same build to multiple groups:
1. Select the build
2. Click "Groups"
3. Add to Internal and/or External groups

---

## Part 8: Automation with GitHub Actions

### Automated TestFlight Deployment

Add to `/app/mobile/.github/workflows/build-mobile.yml`:

```yaml
jobs:
  build-and-submit-ios:
    name: Build & Submit iOS to TestFlight
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
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

### Required Secrets

Add to GitHub repository settings:
- `EXPO_TOKEN`: Your Expo access token
- `APPLE_ID`: Your Apple Developer ID
- `APPLE_APP_SPECIFIC_PASSWORD`: Generated app-specific password

---

## Part 9: Tester Experience

### What Testers See

1. Invitation email from TestFlight
2. "Open in TestFlight" button
3. Install TestFlight app if needed
4. Accept beta testing invitation
5. Install MedMatch app
6. Provide feedback via TestFlight

### Collecting Feedback

- Testers can submit feedback directly in TestFlight
- Screenshots and crash logs are attached automatically
- View feedback in App Store Connect → TestFlight → Feedback

---

## Part 10: Best Practices

### Version Strategy

1. **Internal Testing:** All builds, frequent updates
2. **External Testing:** Stable builds, weekly updates
3. **Production:** Thoroughly tested, monthly releases

### Communication

1. Include release notes with each build
2. Notify testers of new builds via TestFlight
3. Respond to feedback promptly

### Testing Checklist

Before submitting to external testers:
- [ ] Core features working
- [ ] No crashes on startup
- [ ] Login/logout functional
- [ ] Network error handling
- [ ] Offline functionality
- [ ] Push notifications
- [ ] Performance acceptable

---

## Troubleshooting

### "Invalid credentials" Error
- Verify Apple ID is correct
- Generate new app-specific password
- Check 2FA is enabled on Apple account

### "Build rejected" by Beta Review
- Check rejection reason in App Store Connect
- Common issues: missing privacy policy, placeholder content
- Fix issues and resubmit

### "Unable to process submission"
- Ensure bundle ID matches App Store Connect
- Check provisioning profile is valid
- Verify team ID is correct

### Tester not receiving invitation
- Check spam folder
- Verify email address
- Resend invitation from App Store Connect

---

## Quick Reference Commands

```bash
# Build for TestFlight
npx eas build --platform ios --profile production

# Submit latest build
npx eas submit --platform ios --latest

# Check submission status
npx eas submit:list --platform ios

# View builds
npx eas build:list --platform ios

# Configure iOS credentials
npx eas credentials -p ios
```

---

## Support Resources

- **Expo EAS Submit:** https://docs.expo.dev/submit/ios/
- **App Store Connect Help:** https://help.apple.com/app-store-connect/
- **TestFlight Help:** https://developer.apple.com/testflight/
- **Apple Developer Support:** https://developer.apple.com/support/

---

Last Updated: February 1, 2026
