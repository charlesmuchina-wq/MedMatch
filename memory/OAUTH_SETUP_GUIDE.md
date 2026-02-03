# MedMatch OAuth Setup Guide - All Platforms

## Overview
This guide covers setting up OAuth Client IDs for MedMatch across all platforms.

**Google Cloud Project:** `medtech-job-search`
**Service Account:** `medmatch-service-account@medtech-job-search.iam.gserviceaccount.com`

---

## Web Application ✅ (Already Configured)

**Client ID:** `598292141148-49qmcalr4lvt1lg7200o00c962g7orig.apps.googleusercontent.com`
**Client Secret:** `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`

**Authorized JavaScript Origins:**
- `https://smart-recruiter-40.preview.emergentagent.com`
- `http://localhost:3000`

**Authorized Redirect URIs:**
- `https://smart-recruiter-40.preview.emergentagent.com`
- `http://localhost:3000`

---

## Android OAuth Setup

### Step 1: Get SHA-1 Certificate Fingerprint

**For Debug Keystore:**
```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

**For Release Keystore:**
```bash
keytool -list -v -keystore your-release-key.keystore -alias your-alias
```

### Step 2: Create Android OAuth Client

1. Go to **Google Cloud Console** → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Android** application type
4. Fill in:
   - **Name:** `MedMatch Android Client`
   - **Package name:** `com.medmatch.app` (or your package name)
   - **SHA-1 certificate fingerprint:** (from Step 1)
5. Click **CREATE**

### Step 3: Configure in Android App

**build.gradle (app):**
```gradle
android {
    defaultConfig {
        manifestPlaceholders = [
            'appAuthRedirectScheme': 'com.medmatch.app'
        ]
    }
}

dependencies {
    implementation 'com.google.android.gms:play-services-auth:20.7.0'
}
```

**AndroidManifest.xml:**
```xml
<uses-permission android:name="android.permission.INTERNET"/>

<activity
    android:name="com.google.android.gms.auth.api.signin.internal.SignInHubActivity"
    android:screenOrientation="portrait"
    android:exported="true" />
```

**Kotlin Code:**
```kotlin
val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
    .requestIdToken("YOUR_ANDROID_CLIENT_ID.apps.googleusercontent.com")
    .requestEmail()
    .build()

val googleSignInClient = GoogleSignIn.getClient(this, gso)
```

---

## iOS OAuth Setup

### Step 1: Create iOS OAuth Client

1. Go to **Google Cloud Console** → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **iOS** application type
4. Fill in:
   - **Name:** `MedMatch iOS Client`
   - **Bundle ID:** `com.medmatch.app` (your iOS bundle identifier)
   - **App Store ID:** (optional, add when published)
   - **Team ID:** Your Apple Team ID (e.g., `96879J9FZY`)
5. Click **CREATE**
6. Download the `GoogleService-Info.plist` file

### Step 2: Configure in iOS App

**Install Google Sign-In SDK:**
```ruby
# Podfile
pod 'GoogleSignIn', '~> 7.0'
```

**Info.plist:**
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>com.googleusercontent.apps.YOUR_IOS_CLIENT_ID</string>
        </array>
    </dict>
</array>
<key>GIDClientID</key>
<string>YOUR_IOS_CLIENT_ID.apps.googleusercontent.com</string>
```

**AppDelegate.swift:**
```swift
import GoogleSignIn

func application(_ app: UIApplication, open url: URL, 
                 options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    return GIDSignIn.sharedInstance.handle(url)
}
```

**SwiftUI Implementation:**
```swift
import GoogleSignIn
import GoogleSignInSwift

struct ContentView: View {
    var body: some View {
        GoogleSignInButton(action: handleSignIn)
    }
    
    func handleSignIn() {
        guard let presentingVC = UIApplication.shared.windows.first?.rootViewController else { return }
        
        GIDSignIn.sharedInstance.signIn(withPresenting: presentingVC) { result, error in
            guard let user = result?.user, error == nil else { return }
            // Handle signed in user
        }
    }
}
```

---

## Desktop Application (Windows/Mac/Linux)

### Step 1: Create Desktop OAuth Client

1. Go to **Google Cloud Console** → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Desktop app** application type
4. Fill in:
   - **Name:** `MedMatch Desktop Client`
5. Click **CREATE**
6. Note your **Client ID** and **Client Secret**

### Step 2: Configure for Desktop

**Electron App (JavaScript):**
```javascript
const { BrowserWindow } = require('electron');
const { OAuth2Client } = require('google-auth-library');

const CLIENT_ID = 'YOUR_DESKTOP_CLIENT_ID.apps.googleusercontent.com';
const CLIENT_SECRET = 'YOUR_CLIENT_SECRET';
const REDIRECT_URI = 'http://localhost:8085';

const oauth2Client = new OAuth2Client(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

// Generate auth URL
const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: ['https://www.googleapis.com/auth/drive.file']
});

// Open in browser window
const authWindow = new BrowserWindow({ width: 500, height: 600 });
authWindow.loadURL(authUrl);
```

**Python (for native desktop):**
```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_desktop.json', 
    SCOPES
)
credentials = flow.run_local_server(port=8085)
```

---

## Universal Windows Platform (UWP)

### Step 1: Create UWP OAuth Client

1. Go to **Google Cloud Console** → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Universal Windows Platform** application type
4. Fill in:
   - **Name:** `MedMatch UWP Client`
   - **Store ID:** Your Microsoft Store ID (from Partner Center)
   - **Package SID:** `ms-app://s-1-15-2-XXXXXXX` (from app manifest)
5. Click **CREATE**

### Step 2: Get Package SID

1. Open **Package.appxmanifest** in Visual Studio
2. Go to **Declarations** → **Protocol**
3. Add protocol with name matching your redirect URI scheme

Or use PowerShell:
```powershell
Get-AppxPackage -Name "YourAppPackageName" | Select-Object PackageFamilyName
```

### Step 3: Configure in UWP App

**Package.appxmanifest:**
```xml
<Extensions>
    <uap:Extension Category="windows.protocol">
        <uap:Protocol Name="com.medmatch.uwp">
            <uap:DisplayName>MedMatch</uap:DisplayName>
        </uap:Protocol>
    </uap:Extension>
</Extensions>
```

**C# Code:**
```csharp
using Windows.Security.Authentication.Web;

var requestUri = new Uri(
    "https://accounts.google.com/o/oauth2/v2/auth?" +
    $"client_id={CLIENT_ID}&" +
    "response_type=code&" +
    $"redirect_uri={WebAuthenticationBroker.GetCurrentApplicationCallbackUri()}&" +
    "scope=https://www.googleapis.com/auth/drive.file"
);

var result = await WebAuthenticationBroker.AuthenticateAsync(
    WebAuthenticationOptions.None,
    requestUri
);

if (result.ResponseStatus == WebAuthenticationStatus.Success)
{
    // Parse authorization code from result.ResponseData
}
```

---

## Chrome Extension

### Step 1: Create Chrome Extension OAuth Client

1. Go to **Google Cloud Console** → **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Chrome Extension** application type
4. Fill in:
   - **Name:** `MedMatch Chrome Extension`
   - **Application ID:** Your Chrome extension ID (from `chrome://extensions/`)
5. Click **CREATE**

### Step 2: Get Extension ID

**For Development:**
1. Go to `chrome://extensions/`
2. Enable Developer mode
3. Load unpacked extension
4. Copy the **ID** shown

**For Published:**
- Use the ID from Chrome Web Store developer dashboard

### Step 3: Configure in Extension

**manifest.json:**
```json
{
    "manifest_version": 3,
    "name": "MedMatch Job Search",
    "version": "1.0",
    "permissions": [
        "identity",
        "storage"
    ],
    "oauth2": {
        "client_id": "YOUR_CHROME_CLIENT_ID.apps.googleusercontent.com",
        "scopes": [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
    },
    "key": "YOUR_PUBLIC_KEY"
}
```

**background.js:**
```javascript
chrome.identity.getAuthToken({ interactive: true }, function(token) {
    if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        return;
    }
    
    // Use token to access Google APIs
    fetch('https://www.googleapis.com/drive/v3/files', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => console.log(data));
});

// To remove cached token
chrome.identity.removeCachedAuthToken({ token: currentToken }, function() {
    console.log('Token removed');
});
```

**popup.js:**
```javascript
document.getElementById('login-btn').addEventListener('click', function() {
    chrome.identity.getAuthToken({ interactive: true }, function(token) {
        if (token) {
            // Store token and update UI
            chrome.storage.local.set({ authToken: token });
            updateUI(true);
        }
    });
});
```

---

## Summary of OAuth Client IDs Needed

| Platform | Application Type | Key Identifiers |
|----------|-----------------|-----------------|
| Web | Web application | Redirect URIs, JavaScript origins |
| Android | Android | Package name, SHA-1 fingerprint |
| iOS | iOS | Bundle ID, Team ID |
| Desktop | Desktop app | (No additional identifiers) |
| UWP | Universal Windows Platform | Store ID, Package SID |
| Chrome | Chrome Extension | Extension ID |

---

## Security Best Practices

1. **Never expose Client Secrets** in client-side code (except for desktop apps with secure storage)
2. **Use PKCE** (Proof Key for Code Exchange) for mobile and desktop apps
3. **Rotate secrets** periodically
4. **Restrict API keys** by IP, referrer, or app
5. **Use minimal scopes** - only request what you need
6. **Store tokens securely** - use Keychain (iOS), Keystore (Android), or secure storage

---

## Troubleshooting

**"redirect_uri_mismatch" Error:**
- Ensure redirect URI in code exactly matches what's in Google Cloud Console
- Check for trailing slashes
- Verify protocol (http vs https)

**"invalid_client" Error:**
- Verify Client ID is correct for the platform
- Check that the app identifier matches (package name, bundle ID, extension ID)

**"access_denied" Error:**
- User declined permissions
- App not verified (for sensitive scopes)
- Scope not enabled for the project
