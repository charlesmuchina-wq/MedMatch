"""
Routes Package
All API route modules are exported from here
"""
from routes.auth import router as auth_router
from routes.auth import get_current_user, check_membership_status

from routes.jobs import router as jobs_router
from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.ai_features import router as ai_features_router
from routes.analytics import router as analytics_router
from routes.digest import router as digest_router

from routes.messages import router as messages_router
from routes.recruiter import router as recruiter_router
from routes.cloud import router as cloud_router
from routes.companies import router as companies_router
from routes.skills import router as skills_router

from routes.payments import router as payments_router
from routes.payments import membership_router

from routes.scheduling import router as scheduling_router
from routes.scheduling import notifications_router

from routes.push import router as push_router
from routes.dragon import router as dragon_router
from routes.translation import router as translation_router
from routes.biometric import router as biometric_router
from routes.qa_practice import router as qa_practice_router
from routes.video_interview import router as video_interview_router
from routes.push_notifications import router as push_notifications_router
from routes.id_verification import router as id_verification_router

# New routes for LinkedIn, Feedback, and AutoFill
from routes.linkedin import router as linkedin_router
from routes.feedback import router as feedback_router
from routes.autofill import router as autofill_router

# Real-time Speech-to-Text
from routes.realtime_stt import router as realtime_stt_router

# Real Web Push
from routes.webpush import router as webpush_router

# Video Facial Expression Analysis
from routes.video_analysis import router as video_analysis_router

__all__ = [
    # Core routes
    'auth_router',
    'jobs_router',
    'resume_router',
    'interview_router',
    'ai_features_router',
    'analytics_router',
    'digest_router',
    
    # Feature routes
    'messages_router',
    'recruiter_router',
    'cloud_router',
    'companies_router',
    'skills_router',
    
    # Payment routes
    'payments_router',
    'membership_router',
    
    # Scheduling routes
    'scheduling_router',
    'notifications_router',
    
    # Push routes
    'push_router',
    
    # Dragon AI
    'dragon_router',
    
    # Translation
    'translation_router',
    
    # Biometric Authentication
    'biometric_router',
    
    # Q&A Practice
    'qa_practice_router',
    
    # Video Interview
    'video_interview_router',
    
    # Push Notifications
    'push_notifications_router',
    
    # ID Verification
    'id_verification_router',
    
    # LinkedIn Integration
    'linkedin_router',
    
    # Feedback Learning
    'feedback_router',
    
    # Resume Auto-Fill
    'autofill_router',
    
    # Real-time Speech-to-Text
    'realtime_stt_router',
    
    # Real Web Push
    'webpush_router',
    
    # Video Facial Expression Analysis
    'video_analysis_router',
    
    # Helper functions
    'get_current_user',
    'check_membership_status'
]
