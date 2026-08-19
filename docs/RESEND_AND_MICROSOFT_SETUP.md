# Setup Instructions — Resend Domain & Microsoft Publisher (June 2026)

## 1. Resend Domain Verification (unlocks attendee emails)

Currently your Resend account is in **testing mode**: it can only send to your own
account email. Verifying `aikarau.com` removes that limit.

### Steps (~10 minutes)
1. Log in at **resend.com** → left sidebar → **Domains** → **Add Domain**
2. Enter `aikarau.com` (choose region closest to your users) → Add
3. Resend shows DNS records to add — typically:
   - **TXT** record `resend._domainkey` (DKIM) — long `p=...` value
   - **TXT** record for SPF, e.g. `send` → `v=spf1 include:amazonses.com ~all`
   - **MX** record `send` → `feedback-smtp.<region>.amazonses.com` priority 10
4. Open **Bluehost → Domains → aikarau.com → DNS (Zone Editor)**
   - Add each record exactly as shown by Resend (Host/Name, Type, Value, TTL default)
   - Note: Bluehost sometimes auto-appends the domain to the Host field — if Resend
     says host `resend._domainkey.aikarau.com`, enter only `resend._domainkey`
5. Back in Resend click **Verify DNS Records** (propagation: 5 min – 1 hour)
6. When status = **Verified**, tell the agent — we will set
   `SENDER_EMAIL=notifications@aikarau.com` and summary emails will reach every
   registered attendee.

## 2. Microsoft Partner Center + Entra ID (publish Teams/Outlook add-ins)

### A. Microsoft Partner Center account (gives you the Publisher ID)
1. Go to **partner.microsoft.com/dashboard** → sign in with a Microsoft work account
   (create one free via **account.microsoft.com** if needed)
2. Enroll in the **Microsoft AI Cloud Partner Program** (free basic enrollment):
   Dashboard → Enroll → fill company/legal details → verification (1–3 business days)
3. Then add the **Office Store / Commercial Marketplace** program:
   Partner Center → Settings → Programs → **Office Store** → one-time fee may apply
4. Your **Publisher ID** (also called Seller ID) is under
   **Settings → Account settings → Identifiers**
5. Paste the Publisher ID to the agent.

### B. Microsoft Entra (Azure AD) app registration (gives you the client ID)
1. Go to **entra.microsoft.com** (or portal.azure.com → Microsoft Entra ID)
2. **App registrations → New registration**
   - Name: `AI KARAU Suite`
   - Supported account types: **Accounts in any organizational directory and personal
     Microsoft accounts** (multitenant + personal)
   - Redirect URI (Web): `https://aikarau.com/auth/callback` (adjust after deploy)
3. After creation copy the **Application (client) ID** — this is the production Entra
   client ID
4. Under **Certificates & secrets** create a client secret (copy the VALUE immediately)
5. Under **API permissions** add Microsoft Graph → delegated: `openid`, `profile`,
   `email`, `User.Read` → Grant admin consent
6. Paste the client ID (and secret, privately) to the agent — we will wire it into the
   Teams/Outlook manifest + attestation docs.

### What the agent does once you provide the IDs
- Update the Teams/Outlook add-in manifests with your Publisher ID + client ID
- Complete Publisher Attestation content (privacy/terms pages already live at
  /legal/privacy and /legal/terms)
- Prepare store submission packages
