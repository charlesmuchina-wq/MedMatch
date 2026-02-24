#!/usr/bin/env python3
"""
Add comprehensive translation keys for all remaining hardcoded strings
"""

import json
import os
import re

LOCALES_DIR = "/app/frontend/src/locales"

# Comprehensive translation keys to add
NEW_KEYS = {
    "notifications": {
        "title": "Notifications",
        "markAllRead": "Mark all as read",
        "noNotifications": "No notifications",
        "allRead": "All notifications marked as read",
        "newApplication": "New Application",
        "interviewInvite": "Interview Invitation",
        "statusUpdate": "Status Update",
        "message": "Message",
        "jobAlert": "Job Alert",
        "systemAlert": "System Alert",
        "today": "Today",
        "yesterday": "Yesterday",
        "earlier": "Earlier",
        "clearAll": "Clear All",
        "settings": "Notification Settings",
        "emailNotifications": "Email Notifications",
        "pushNotifications": "Push Notifications",
        "smsNotifications": "SMS Notifications",
        "dailyDigest": "Daily Digest",
        "weeklyDigest": "Weekly Digest",
        "instantAlerts": "Instant Alerts"
    },
    "jobAlerts": {
        "title": "Job Alerts",
        "subtitle": "Get notified about new opportunities",
        "createAlert": "Create Alert",
        "editAlert": "Edit Alert",
        "deleteAlert": "Delete Alert",
        "alertName": "Alert Name",
        "keywords": "Keywords",
        "location": "Location",
        "jobType": "Job Type",
        "salaryRange": "Salary Range",
        "frequency": "Frequency",
        "daily": "Daily",
        "weekly": "Weekly",
        "instant": "Instant",
        "noAlerts": "No job alerts set up yet",
        "createFirst": "Create your first alert to get notified",
        "activeAlerts": "Active Alerts",
        "pausedAlerts": "Paused Alerts",
        "pause": "Pause",
        "resume": "Resume",
        "matchingJobs": "Matching Jobs",
        "lastSent": "Last Sent",
        "automatedDaily": "Automated Daily Digest",
        "automatedDesc": "Automatically receive new job postings every day at 8:00 AM UTC"
    },
    "salaryInsights": {
        "title": "Salary Insights",
        "subtitle": "Understand your market value",
        "yourEstimate": "Your Estimated Salary",
        "marketAverage": "Market Average",
        "percentile": "Percentile",
        "experience": "Experience Level",
        "location": "Location",
        "industry": "Industry",
        "skills": "Skills",
        "compareBy": "Compare By",
        "aboveMarket": "Above Market",
        "atMarket": "At Market Rate",
        "belowMarket": "Below Market",
        "salaryRange": "Salary Range",
        "baseSalary": "Base Salary",
        "totalCompensation": "Total Compensation",
        "bonus": "Bonus",
        "equity": "Equity",
        "benefits": "Benefits",
        "negotiationTips": "Negotiation Tips",
        "marketTrends": "Market Trends",
        "demandIndex": "Demand Index",
        "growthRate": "Growth Rate"
    },
    "voiceCoach": {
        "title": "AI Interview Coach",
        "subtitle": "Practice speaking your answers and get real-time AI feedback",
        "practice": "Voice Interview Practice",
        "practiceDesc": "Speak your answers out loud and receive AI-powered feedback",
        "voiceAnalysis": "Voice Analysis",
        "realtimeFeedback": "Real-time Feedback",
        "startPractice": "Start Practice Session",
        "tips": "Voice Interview Tips",
        "idealLength": "Ideal Length",
        "idealLengthDesc": "Aim for 1-2 minute answers (150-300 words)",
        "clearSpeech": "Clear Speech",
        "clearSpeechDesc": "Speak clearly and at a moderate pace",
        "beSpecific": "Be Specific",
        "beSpecificDesc": "Use concrete examples and metrics",
        "stayFocused": "Stay Focused",
        "stayFocusedDesc": "Answer the question directly, then elaborate",
        "notSupported": "Speech Recognition Not Supported",
        "useChrome": "Your browser doesn't support voice input. Please use Chrome, Edge, or Safari.",
        "avgScore": "Avg Score",
        "totalTime": "Total Time",
        "answered": "Answered",
        "listening": "Listening... Speak your answer",
        "clickToRecord": "Click the microphone to start recording",
        "playback": "Recording Playback",
        "playRecording": "Play Recording",
        "confidence": "Confidence",
        "clarity": "Clarity",
        "relevance": "Relevance",
        "pacing": "Pacing"
    },
    "messages": {
        "title": "Messages",
        "newMessage": "New Message",
        "sendMessage": "Send Message",
        "typeMessage": "Type your message...",
        "noMessages": "No messages yet",
        "startConversation": "Start a conversation",
        "searchMessages": "Search messages...",
        "inbox": "Inbox",
        "sent": "Sent",
        "archived": "Archived",
        "unread": "Unread",
        "markRead": "Mark as Read",
        "markUnread": "Mark as Unread",
        "archive": "Archive",
        "delete": "Delete",
        "reply": "Reply",
        "forward": "Forward",
        "attachFile": "Attach File",
        "recruiter": "Recruiter",
        "candidate": "Candidate",
        "anonymous": "Anonymous",
        "contactAccepted": "Contact accepted! You can now chat.",
        "contactRequestSent": "Contact request sent!"
    },
    "companies": {
        "title": "Companies",
        "subtitle": "Explore employers",
        "searchCompanies": "Search companies...",
        "allIndustries": "All Industries",
        "allSizes": "All Sizes",
        "verified": "Verified",
        "reviews": "Reviews",
        "openPositions": "Open Positions",
        "about": "About",
        "benefits": "Benefits",
        "culture": "Culture",
        "salaries": "Salaries",
        "interviews": "Interviews",
        "photos": "Photos",
        "noCompanies": "No companies found",
        "beFirst": "Be the first to create a company profile",
        "writeReview": "Write a Review",
        "followCompany": "Follow Company",
        "viewJobs": "View Jobs"
    },
    "resume": {
        "title": "My Resume",
        "uploadResume": "Upload Resume",
        "createNew": "Create New Resume",
        "editResume": "Edit Resume",
        "downloadPdf": "Download PDF",
        "preview": "Preview",
        "sections": "Sections",
        "personalInfo": "Personal Information",
        "summary": "Summary",
        "experience": "Experience",
        "education": "Education",
        "skills": "Skills",
        "certifications": "Certifications",
        "languages": "Languages",
        "projects": "Projects",
        "publications": "Publications",
        "awards": "Awards",
        "volunteer": "Volunteer Experience",
        "references": "References",
        "addSection": "Add Section",
        "removeSection": "Remove Section",
        "reorderSections": "Reorder Sections",
        "autoFill": "Auto-Fill",
        "aiSuggestions": "AI Suggestions",
        "parseResume": "Parse Resume",
        "lastUpdated": "Last Updated"
    },
    "applications": {
        "title": "Applications",
        "myApplications": "My Applications",
        "applied": "Applied",
        "inReview": "In Review",
        "interview": "Interview",
        "offer": "Offer",
        "rejected": "Rejected",
        "withdrawn": "Withdrawn",
        "noApplications": "No applications yet",
        "startApplying": "Start applying to jobs",
        "trackProgress": "Track your application progress",
        "applicationStatus": "Application Status",
        "appliedOn": "Applied On",
        "lastActivity": "Last Activity",
        "nextSteps": "Next Steps",
        "withdrawApplication": "Withdraw Application",
        "viewJob": "View Job",
        "contactRecruiter": "Contact Recruiter"
    },
    "calendar": {
        "title": "Interview Calendar",
        "schedule": "Schedule",
        "upcoming": "Upcoming",
        "past": "Past",
        "today": "Today",
        "thisWeek": "This Week",
        "thisMonth": "This Month",
        "noInterviews": "No interviews scheduled",
        "scheduleInterview": "Schedule Interview",
        "reschedule": "Reschedule",
        "cancel": "Cancel",
        "addToCalendar": "Add to Calendar",
        "addToGoogleCalendar": "Add to Google Calendar",
        "joinMeeting": "Join Meeting",
        "interviewDetails": "Interview Details",
        "interviewer": "Interviewer",
        "duration": "Duration",
        "location": "Location",
        "virtual": "Virtual",
        "inPerson": "In-Person",
        "phone": "Phone",
        "notes": "Notes",
        "prepare": "Prepare",
        "feedback": "Feedback"
    },
    "analytics": {
        "title": "Analytics",
        "overview": "Overview",
        "performance": "Performance",
        "trends": "Trends",
        "insights": "Insights",
        "totalViews": "Total Views",
        "profileViews": "Profile Views",
        "searchAppearances": "Search Appearances",
        "applicationRate": "Application Rate",
        "responseRate": "Response Rate",
        "interviewRate": "Interview Rate",
        "conversionRate": "Conversion Rate",
        "timeToHire": "Time to Hire",
        "avgResponseTime": "Avg Response Time",
        "topSkills": "Top Skills",
        "topLocations": "Top Locations",
        "topCompanies": "Top Companies",
        "weeklyReport": "Weekly Report",
        "monthlyReport": "Monthly Report",
        "exportData": "Export Data"
    },
    "recruiter": {
        "dashboard": {
            "title": "Recruiter Dashboard",
            "welcome": "Welcome back",
            "activeJobs": "Active Jobs",
            "totalApplications": "Total Applications",
            "pendingReview": "Pending Review",
            "interviewsScheduled": "Interviews Scheduled",
            "recentActivity": "Recent Activity",
            "topCandidates": "Top Candidates",
            "viewAll": "View All",
            "createJob": "Create New Job",
            "manageJobs": "Manage Jobs",
            "candidateSearch": "Candidate Search",
            "analytics": "Analytics",
            "hiringPipeline": "Hiring Pipeline",
            "newApplicants": "New Applicants",
            "screening": "Screening",
            "interview": "Interview",
            "offer": "Offer",
            "hired": "Hired"
        },
        "jobs": {
            "createJob": "Create Job Posting",
            "editJob": "Edit Job Posting",
            "deleteJob": "Delete Job Posting",
            "jobTitle": "Job Title",
            "department": "Department",
            "location": "Location",
            "jobType": "Job Type",
            "salaryRange": "Salary Range",
            "description": "Description",
            "requirements": "Requirements",
            "benefits": "Benefits",
            "applicationDeadline": "Application Deadline",
            "publish": "Publish",
            "saveDraft": "Save Draft",
            "preview": "Preview",
            "shareLink": "Share Link",
            "applicants": "Applicants",
            "views": "Views",
            "status": "Status",
            "active": "Active",
            "paused": "Paused",
            "closed": "Closed",
            "draft": "Draft"
        },
        "candidates": {
            "searchCandidates": "Search Candidates",
            "filterBy": "Filter By",
            "skills": "Skills",
            "experience": "Experience",
            "location": "Location",
            "availability": "Availability",
            "sortBy": "Sort By",
            "relevance": "Relevance",
            "recent": "Most Recent",
            "matchScore": "Match Score",
            "viewProfile": "View Profile",
            "shortlist": "Shortlist",
            "contact": "Contact",
            "scheduleInterview": "Schedule Interview",
            "reject": "Reject",
            "notes": "Notes",
            "addNote": "Add Note",
            "history": "History",
            "blindMode": "Blind Screening Mode",
            "revealIdentity": "Reveal Identity"
        }
    },
    "dataIntegrity": {
        "title": "Data Integrity",
        "compliance": "Compliance",
        "security": "Security",
        "privacy": "Privacy",
        "audit": "Audit",
        "regional": "Regional Compliance",
        "modelHealth": "Model Health",
        "biasAudits": "Bias Audits",
        "securityScore": "Security Score",
        "modelsPerformingWell": "Models performing well",
        "protectedCharacteristics": "Protected characteristics",
        "redTeamAssessment": "Red team assessment",
        "complianceStatus": "Compliance Status",
        "automatedAlerts": "Automated alerts when model accuracy degrades",
        "hallucinationDetection": "Hallucination Detection",
        "groundingChecks": "Grounding checks for AI outputs",
        "adversarialTesting": "Adversarial attack testing",
        "algorithmicBias": "Algorithmic Bias Detection",
        "disparateImpact": "Disparate impact monitoring",
        "auditReports": "Audit Reports",
        "generateReport": "Generate Report",
        "reportHistory": "Report History"
    },
    "verification": {
        "title": "Verification",
        "identityVerification": "Identity Verification",
        "documentVerification": "Document Verification",
        "emailVerification": "Email Verification",
        "phoneVerification": "Phone Verification",
        "linkedinVerification": "LinkedIn Verification",
        "companyVerification": "Company Verification",
        "pending": "Pending",
        "verified": "Verified",
        "rejected": "Rejected",
        "uploadDocument": "Upload Document",
        "verifyNow": "Verify Now",
        "verificationComplete": "Verification Complete",
        "verificationFailed": "Verification Failed",
        "tryAgain": "Try Again",
        "businessInfo": "Business Info",
        "legitimateOrg": "Company is legitimate organization",
        "hrFunction": "Job title indicates HR/recruiting function"
    },
    "settings": {
        "title": "Settings",
        "account": "Account",
        "profile": "Profile",
        "privacy": "Privacy",
        "notifications": "Notifications",
        "security": "Security",
        "language": "Language",
        "theme": "Theme",
        "darkMode": "Dark Mode",
        "lightMode": "Light Mode",
        "systemDefault": "System Default",
        "changePassword": "Change Password",
        "twoFactor": "Two-Factor Authentication",
        "sessions": "Active Sessions",
        "deleteAccount": "Delete Account",
        "exportData": "Export My Data",
        "dataPrivacy": "Data Privacy",
        "cookieSettings": "Cookie Settings",
        "consentManagement": "Consent Management"
    },
    "errors": {
        "generic": "Something went wrong",
        "tryAgain": "Please try again",
        "networkError": "Network error",
        "serverError": "Server error",
        "notFound": "Not found",
        "unauthorized": "Unauthorized",
        "forbidden": "Access denied",
        "validation": "Validation error",
        "required": "This field is required",
        "invalidEmail": "Invalid email address",
        "invalidPhone": "Invalid phone number",
        "passwordMismatch": "Passwords do not match",
        "sessionExpired": "Session expired",
        "loginRequired": "Login required"
    },
    "success": {
        "saved": "Changes saved",
        "deleted": "Successfully deleted",
        "updated": "Successfully updated",
        "created": "Successfully created",
        "sent": "Successfully sent",
        "copied": "Copied to clipboard",
        "uploaded": "Successfully uploaded",
        "downloaded": "Download started"
    }
}

def deep_merge(base, updates):
    """Recursively merge updates into base"""
    for key, value in updates.items():
        if key not in base:
            base[key] = value
        elif isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
    return base

def main():
    # Load English locale
    en_path = f"{LOCALES_DIR}/en.json"
    with open(en_path, 'r', encoding='utf-8') as f:
        en = json.load(f)
    
    # Merge new keys
    en = deep_merge(en, NEW_KEYS)
    
    # Save English
    with open(en_path, 'w', encoding='utf-8') as f:
        json.dump(en, f, ensure_ascii=False, indent=2)
    
    print(f"Added new keys to en.json")
    
    # Sync to all locales
    locales = [f.replace('.json', '') for f in os.listdir(LOCALES_DIR) 
               if f.endswith('.json') and f not in ['en.json', 'pseudo.json']]
    
    for lang in locales:
        path = f"{LOCALES_DIR}/{lang}.json"
        with open(path, 'r', encoding='utf-8') as f:
            locale = json.load(f)
        locale = deep_merge(locale, en)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(locale, f, ensure_ascii=False, indent=2)
    
    print(f"Synced to {len(locales)} locales")

if __name__ == "__main__":
    main()
