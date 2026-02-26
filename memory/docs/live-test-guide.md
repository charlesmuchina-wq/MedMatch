# AI KARAU - Live Multi-User Meeting Test Guide

## Prerequisites
- 2+ devices/browsers (incognito windows count as separate sessions)
- Admin account: `admin@medmatch.com` / `Swampdrainer2026!`
- Test account: `test@medmatch.io` / `TestPassword123!`
- Guest access: use any email (OTP will be sent)

## Test Scenarios

### 1. Meeting Creation & Join (5 min)
- [ ] Host: Login as admin, create a new meeting from Dashboard
- [ ] Host: Click "Start Meeting" — verify lobby loads with camera/mic preview
- [ ] Host: Enable/disable camera and mic from lobby
- [ ] Guest: Open meeting join link in incognito — complete 3-step guest verification (name+email → OTP → age declaration)
- [ ] Guest: Verify lobby waiting room appears after verification

### 2. Lobby & Admission (5 min)
- [ ] Host: Click "Join Meeting" from lobby
- [ ] Guest: Should appear in host's waiting room list
- [ ] Host: Admit guest — guest should enter the meeting
- [ ] Verify both participants see each other's video tiles

### 3. Host Moderation (5 min)
- [ ] Host: Click "Mute All" — verify all participants are muted
- [ ] Host: Unmute self — verify only host is unmuted
- [ ] Host: Use "Pass Mic" on guest — verify guest is auto-unmuted
- [ ] Guest: Verify mute/unmute state reflects host actions

### 4. Active Speaker (3 min)
- [ ] Have one person speak — verify their tile gets highlighted
- [ ] Switch speakers — verify highlight moves to new speaker
- [ ] Both silent — verify no highlight

### 5. Breakout Rooms (5 min)
- [ ] Host: Open Breakout Room Manager
- [ ] Host: Create 2 rooms, assign participants
- [ ] Host: Start breakout rooms — verify participants move to assigned rooms
- [ ] Host: Close breakout rooms — verify all return to main room

### 6. Calendar & Sharing (3 min)
- [ ] Click "Share" in meeting header — verify social sharing dialog
- [ ] Click "Download .ics" — verify calendar file downloads
- [ ] Click LinkedIn/Twitter share buttons — verify share windows open
- [ ] Copy meeting link — verify clipboard contains correct URL

### 7. Enterprise Admin (5 min)
- [ ] Navigate to Organization Admin panel
- [ ] Verify tier selection, domain management, conference rooms
- [ ] Navigate to Employee Directory — verify CSV import and employee list
- [ ] Check Calendar tab in Settings — verify Microsoft/Apple/Google providers shown
- [ ] Check SSO/SAML tab — verify SP details and IdP configuration form

### 8. Screen Sharing (3 min)
- [ ] Host: Click screen share button
- [ ] Verify screen share is visible to all participants
- [ ] Host: Stop screen sharing — verify it returns to camera view

## Expected Results
- All WebRTC connections should be stable throughout
- No audio/video dropouts during normal usage
- Host controls should reflect in real-time across all participants
- Guest verification should complete in under 60 seconds
