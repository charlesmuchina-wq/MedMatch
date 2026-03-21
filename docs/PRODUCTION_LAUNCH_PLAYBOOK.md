# AI Suite — Production Launch Playbook

> **Key Dependency:** G5 sign-off (Task 3) and Azure AD validation (Task 2) must both complete **before** the first Wave production submission (Task 1).

---

## Task 1 — Submit Platform Builds per Wave Deployment Schedule

### Prerequisites
- Final release branch
- Signing certificates: Apple Distribution cert + provisioning profile; Android Keystore
- Wave schedule document
- App Store Connect access
- Google Play Console access

### Step 1 — Confirm Wave Schedule Alignment
- Pull the Wave deployment schedule and map each wave to a calendar date
- Document which build version corresponds to each wave (e.g., Wave 1 = v1.2.0, Wave 2 = v1.3.0)
- Lock feature freeze dates per wave **at least 5 business days** before submission to allow review time

### Step 2 — Build and Sign the Release Artifact
- **iOS:** Archive the app in Xcode using the Distribution scheme, select "App Store Connect" distribution method, and export the signed `.ipa`
- **Android:** Generate a signed `.aab` (Android App Bundle) using your Keystore in Android Studio or via Gradle (`./gradlew bundleRelease`)
- Store artifacts with wave version tags in your artifact repository

### Step 3 — Internal Testing Before Submission
- Upload the iOS build to **TestFlight** and distribute to the internal testing group
- Upload the Android build to the **Play Console Internal Testing** track
- Allow **24–48 hours** for internal validation and smoke testing against wave acceptance criteria

### Step 4 — Submit to Store Review
- **App Store Connect:** Create a new app version, upload the `.ipa`, complete all metadata (screenshots, release notes referencing the wave), and submit for review
- **Play Console:** Promote from Internal Testing → Production and configure a staged rollout percentage aligned with your wave plan (e.g., Wave 1 = 10%)

### Step 5 — Monitor and Promote per Wave
- Use App Store Connect's **phased release** (7-day rollout toggle) or Play Console's **staged rollout** to throttle distribution
- Monitor crash rates and ANR data in both consoles after each wave promotion before increasing rollout percentage

---

## Task 2 — Register Azure AD for Microsoft Teams/Outlook Functionality

### Prerequisites
- Azure subscription with **Global Admin** or **Application Administrator** role
- Your app's redirect URIs
- Tenant ID

### Step 1 — Create the App Registration
- In the Azure portal: **Azure Active Directory → App registrations → New registration**
- Name the app, select supported account types (single-tenant or multi-tenant)
- Add redirect URIs:
  - Web: `https://yourapp.com/auth/callback`
  - Mobile: your custom scheme

### Step 2 — Configure API Permissions for Teams and Outlook
Under **API permissions → Add a permission → Microsoft Graph**, add:

| Permission | Type | Purpose |
|------------|------|---------|
| `User.Read` | Delegated | Read user profile |
| `Mail.ReadWrite` | Delegated | Read/write Outlook mail |
| `Mail.Send` | Delegated | Send Outlook mail |
| `Calendars.ReadWrite` | Delegated | Outlook calendar access |
| `ChannelMessage.Send` | Delegated | Send Teams channel messages |
| `Chat.ReadWrite` | Delegated | Read/write Teams chats |
| `TeamsActivity.Send` | Delegated | Send Teams activity notifications |

> If your app acts as a daemon/service, use **Application permissions** instead of Delegated.

### Step 3 — Grant Admin Consent
- Click **Grant admin consent for [your tenant]**
- Required for application-level permissions
- Strongly recommended for delegated permissions in enterprise deployments
- A **Global Admin** must approve this step

### Step 4 — Create a Client Secret or Configure Certificates
- Under **Certificates & secrets → New client secret**, create a secret
- **Immediately copy the value** — it is only shown once
- Store in Azure Key Vault or your secrets manager
- Alternative: upload a certificate for stronger credential security

### Step 5 — Configure Authentication Flows
- Enable the appropriate platform under **Authentication → Add a platform** (Web, SPA, or Mobile)
- Enable **ID tokens** and **Access tokens** under implicit grant if needed
- Integrate **MSAL** (Microsoft Authentication Library) into your app using:
  - `client_id`
  - `tenant_id`
  - Your chosen scopes
- Test the OAuth2 authorization code flow end-to-end

### Step 6 — Validate Teams and Outlook Functionality
- Authenticate as a test user and verify token acquisition
- Test Teams message sending via Graph API:
  ```
  POST /teams/{team-id}/channels/{channel-id}/messages
  ```
- Test Outlook mail sending:
  ```
  POST /me/sendMail
  ```
- Validate that all permission scopes are honored and no consent prompts unexpectedly block users

---

## Task 3 — Obtain CISO Security Sign-Off (Gate G5)

### Prerequisites
- Completed threat model
- Penetration test report
- Vulnerability scan results (SAST/DAST)
- Data flow diagrams
- Privacy impact assessment
- Incident response plan

### Step 1 — Assemble the Security Evidence Pack
Compile all required artifacts into a single submission package:
1. **Threat model** (STRIDE or DREAD-based)
2. **Static analysis results** (SAST — tools like SonarQube or Checkmarx)
3. **Dynamic analysis results** (DAST — tools like OWASP ZAP or Burp Suite)
4. **Penetration test report** with findings and remediation status
5. **Dependency vulnerability scan** (e.g., OWASP Dependency-Check or Snyk report)

### Step 2 — Remediate All Critical and High Findings
- Work through the pen test and scan findings
- **Critical and High** severity issues: must be **fully remediated** before G5
- **Medium** findings: require a documented remediation plan with timelines
- **Low** findings: can be accepted with a risk acknowledgment
- Produce a **finding tracker** showing: original finding → remediation applied → re-test result

### Step 3 — Complete the Risk Assessment
- Document residual risks with **likelihood and impact** ratings
- Map each risk to a **compensating control**
- If any risk requires formal acceptance, prepare a **Risk Acceptance Form** signed by the application/business owner

### Step 4 — Prepare the G5 Submission
Create the G5 gate submission document including:
- Executive summary of security posture
- Summary of testing performed and dates
- Finding disposition table (fixed / accepted / deferred)
- Residual risk register
- Confirmation of compliance with organizational security policies:
  - Encryption at rest/in transit
  - Secrets management
  - Authentication standards

### Step 5 — Schedule the G5 Review Meeting
- Book a review session with the **CISO** (or their designated security architect)
- Present the evidence pack
- Be prepared to walk through the threat model and demonstrate critical attack vector mitigation
- Allow **at least 5 business days** lead time for the CISO to review documents before the meeting

### Step 6 — Obtain Signed Sign-Off
- After a successful review, obtain the **signed G5 sign-off document** (physical or e-signature)
- File it in your project governance repository
- The signed G5 is a **hard prerequisite gate** — no production deployment occurs without it
- If the CISO raises blockers, enter a remediation cycle and reschedule

---

## Execution Order & Timeline

```
Week 1-2:  Task 3 (CISO prep) + Task 2 (Azure AD registration)
           ├── Assemble security evidence pack
           ├── Create Azure AD app registration
           └── Configure API permissions & admin consent

Week 2-3:  Task 3 (CISO review) + Task 2 (Validation)
           ├── Remediate findings, schedule G5 review
           ├── Integrate MSAL, test OAuth2 flow
           └── Validate Teams/Outlook functionality

Week 3-4:  Task 1 (Store submissions — Wave 1)
           ├── G5 sign-off obtained (hard prerequisite)
           ├── Azure AD validated (hard prerequisite)
           ├── Build & sign release artifacts
           ├── Internal testing via TestFlight / Play Console
           └── Submit to App Store + Play Store

Week 4+:   Task 1 (Wave rollout monitoring)
           ├── Monitor crash rates & ANR data
           ├── Staged rollout: 10% → 25% → 50% → 100%
           └── Subsequent waves per schedule
```

## Current Gate Status

| Gate | Name | Status | Blocker |
|------|------|--------|---------|
| G1 | Functional Complete | PASSED | — |
| G2 | Reliability Validated | PASSED | — |
| G3 | Regression Clean | PASSED | — |
| G4 | Platform Certification | PREREQUISITES MET | Store submissions pending (Task 1) |
| G5 | Security Sign-Off | PREREQUISITES MET | CISO review pending (Task 3) |

## CSS View Transition Configuration (for app)
```css
::view-transition-group(*),
::view-transition-old(*),
::view-transition-new(*) {
  animation-duration: 0.25s;
  animation-timing-function: cubic-bezier(0.19, 1, 0.22, 1);
}
```
