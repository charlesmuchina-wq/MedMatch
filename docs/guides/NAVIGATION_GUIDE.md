# MedMatch Navigation Guide

## Table of Contents
1. [Job Seeker Guide](#job-seeker-guide)
2. [Recruiter Guide](#recruiter-guide)
3. [Video Tutorials](#video-tutorials)

---

## Video Tutorials 🎬

### AI-Generated Explainer Videos
The following instructional videos are available in `/app/videos/`:

| Video | Description | Duration | File |
|-------|-------------|----------|------|
| Job Seeker Introduction | Overview of MedMatch platform for job seekers | 4 seconds | `01_jobseeker_intro.mp4` |
| Recruiter Dashboard | Recruiter interface walkthrough | 4 seconds | `02_recruiter_dashboard.mp4` |
| Job Search Tutorial | How to search and filter jobs | 4 seconds | `03_job_search.mp4` |
| ATS System Overview | Applicant Tracking System for recruiters | 4 seconds | `04_ats_system.mp4` |

---

## Job Seeker Guide

### Getting Started

#### Step 1: Sign In
1. Navigate to [MedMatch](https://karau-enzi-nexus.preview.emergentagent.com)
2. Choose your sign-in method:
   - **Google** - Quick sign-in with your Google account
   - **Apple** - Sign in with Apple ID
   - **Email** - Use email and password
   - **Phone Number** - SMS verification
   - **Biometric Login** - Face ID or fingerprint

#### Step 2: Dashboard Overview
After signing in, you'll see your personalized dashboard with:
- **Quick Actions**: Upload Resume, Search Jobs, Review Saved Jobs
- **Trust Score**: Your profile credibility score (out of 440 points)
- **Score Breakdown**: Credentials, Profile, Engagement, Tenure, Reviews

### Core Features

#### 📄 My Resume
- **Upload Resume**: Drag and drop or browse files (PDF, DOC, DOCX)
- **Import from Cloud**: Connect Google Drive, Dropbox, or OneDrive
- **Auto-Fill Data**: AI extracts your information automatically
- **LinkedIn Profile**: Import your LinkedIn data

#### 🔍 Job Search
- **Search Bar**: Enter job titles, keywords, or company names
- **Filters Available**:
  - Job Type (Full-time, Part-time, Contract)
  - Location
  - Salary Range
  - Remote/On-site/Hybrid
- **Life Sciences Filters**: Specialized filters for biotech, pharma, medical devices
- **AI Deep Search**: AI-powered matching based on your profile
- **Match Percentage**: See how well each job matches your skills (shown as %)

#### 💾 Saved Jobs
- Click the bookmark icon on any job to save it
- Access all saved jobs from the sidebar
- Track application status for saved jobs

#### 📋 Applications
- View all your submitted applications
- Track status: Applied → Interviewing → Offered → Rejected
- Filter by status to see pipeline

#### 🎯 Career Explorer
- Discover career paths in life sciences
- See skill requirements for different roles
- Get AI-powered career pivot suggestions

#### 🏆 Credentials
- Add your certifications and licenses
- Import digital badges from Credly
- Verify credentials for higher Trust Score

### Applying for Jobs

#### Via Direct Application
1. Click on a job listing
2. Click "Apply" button
3. Fill out application form
4. Submit your application
5. Track status in "Applications" section

#### Via Application Link (From Recruiter)
1. Open the link provided by recruiter (e.g., `/apply/[token]`)
2. Fill out the form:
   - Full Name (required)
   - Email (required)
   - Phone Number
   - LinkedIn Profile URL
   - Portfolio/Website
   - Resume Link
   - Cover Letter
3. Click "Submit Application"
4. Save your Application ID to track status

### Tracking Your Application
1. Visit `/track-application/[your-application-id]`
2. See current status and timeline
3. View any messages from recruiter

---

## Recruiter Guide

### Getting Started

#### Step 1: Access Recruiter Dashboard
1. Sign in with your recruiter account
2. Your sidebar will show recruiter-specific options:
   - Dashboard
   - My Job Postings
   - Applicant Tracking
   - Interviews
   - Search Candidates
   - Companies
   - Messages

### Core Features

#### 📝 My Job Postings
- View all your active job listings
- Create new job postings
- Edit or deactivate existing posts
- See applicant counts per job

#### 👥 Applicant Tracking System (ATS)

##### Dashboard Overview
The ATS dashboard shows:
- **Total Applications**: All applications received
- **This Week**: Recent application activity
- **Active Links**: Number of shareable application links
- **Invitations Sent**: Email invitations to candidates

##### Creating Application Links
1. Go to "Applicant Tracking" in sidebar
2. Click "+ Create Link" button
3. Select the job posting
4. Set expiration (default: 30 days)
5. Copy the generated link
6. Share with candidates via email, LinkedIn, etc.

##### Managing Applications
Each application link shows:
- Job title and company
- Status (Active/Inactive)
- View count
- Application count
- Expiration date
- Actions: Copy, Preview, Delete

##### Application Statuses
Track candidates through the hiring pipeline:
1. **Received** - Application submitted
2. **Reviewing** - Under initial review
3. **Phone Screen** - Phone interview scheduled
4. **Interview** - In-person/video interview
5. **Technical** - Technical assessment
6. **Final Round** - Final interviews
7. **Reference Check** - Checking references
8. **Offered** - Offer extended
9. **Hired** - Candidate accepted
10. **Rejected** - Not moving forward
11. **Withdrawn** - Candidate withdrew

##### Updating Application Status
1. Go to "My Job Postings"
2. Click on a job to see applicants
3. Find the candidate
4. Select new status from dropdown
5. Toggle "Send Email Notification" if desired
6. Click update

#### 🔍 Search Candidates
- Search the candidate database
- Filter by skills, experience, location
- View candidate profiles and resumes
- Send direct messages

#### 📅 Interviews
- View scheduled interviews
- Manage interview calendar
- Send meeting invites

### Sending Invitations

#### Email Invitations
1. Go to ATS Management
2. Click "Invitations" tab
3. Click "Send Invitation"
4. Enter candidate details:
   - Email address
   - Name (optional)
   - Personal message (optional)
5. Select the job
6. Click Send

---

## Quick Reference

### Test Accounts
| Role | Email | Password |
|------|-------|----------|
| Job Seeker | `test_jobseeker_ui@test.com` | `Test123!` |
| Admin/Recruiter | `admin@medmatch.com` | `MedMatch2026!` |

### Key URLs
| Page | URL |
|------|-----|
| Login | `/` |
| Dashboard | `/dashboard` |
| Job Search | `/job-search` |
| My Resume | `/resume` |
| Applications | `/applications` |
| Recruiter Jobs | `/recruiter/jobs` |
| ATS Management | `/recruiter/ats` |
| Public Apply | `/apply/[token]` |
| Track Application | `/track-application/[id]` |

### Keyboard Shortcuts
- `Ctrl/Cmd + K` - Quick search
- `Esc` - Close modals

---

## Support

For technical support or questions:
- Email: support@medmatch.com
- Documentation: `/docs`

---

*Last updated: February 2026*
