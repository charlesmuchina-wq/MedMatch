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
    
    # Helper functions
    'get_current_user',
    'check_membership_status'
]
