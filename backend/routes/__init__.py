"""
Routes Package
All API route modules are exported from here
"""
from routes.auth import router as auth_router
from routes.messages import router as messages_router
from routes.recruiter import router as recruiter_router
from routes.cloud import router as cloud_router
from routes.companies import router as companies_router
from routes.skills import router as skills_router

# Helper functions that may be needed across modules
from routes.auth import get_current_user, check_membership_status

__all__ = [
    'auth_router',
    'messages_router', 
    'recruiter_router',
    'cloud_router',
    'companies_router',
    'skills_router',
    'get_current_user',
    'check_membership_status'
]
