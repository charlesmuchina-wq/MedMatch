"""
Authentication Routes
Handles: register, login, Google/Apple OAuth, phone OTP, session management
"""
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import secrets
import uuid
import logging
import jwt
import httpx
import os

from utils.database import db
from utils.config import (
    JWT_SECRET_KEY, APPLE_TEAM_ID, APPLE_KEY_ID, 
    APPLE_SERVICE_ID, APPLE_PRIVATE_KEY,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============== Models ==============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "job_seeker"

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleSessionRequest(BaseModel):
    session_id: str

class AppleAuthRequest(BaseModel):
    id_token: str
    code: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class PhoneLoginRequest(BaseModel):
    phone_number: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    code: str

class UpdatePreferencesRequest(BaseModel):
    language: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    grammatical_gender: Optional[str] = None  # 'masculine', 'feminine', 'neutral', or None (auto)

# ============== Helper Functions ==============

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(":")
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == password_hash
    except:
        return False

def create_session_token() -> str:
    """Create a secure session token"""
    return secrets.token_urlsafe(32)

async def create_session(user_id: str, session_token: str):
    """Store session in database"""
    await db.user_sessions.insert_one({
        "session_token": session_token,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    })

async def get_or_create_user(email: str, name: str = "", auth_method: str = "email"):
    """Get existing user or create new one"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if user:
        return user
    
    user_doc = {
        "user_id": f"user_{uuid.uuid4().hex[:12]}",
        "email": email,
        "name": name,
        "auth_method": auth_method,
        "role": "job_seeker",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "membership_status": "trial",
        "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
    }
    await db.users.insert_one(user_doc)
    return user_doc

async def get_current_user(request: Request):
    """Get current user from session cookie or Bearer token"""
    # First try Bearer token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Check in sessions collection
        session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
        if session:
            # Check expiration
            expires_at = session.get("expires_at")
            if expires_at:
                try:
                    if isinstance(expires_at, str):
                        expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    else:
                        expires_dt = expires_at
                    
                    if expires_dt < datetime.now(timezone.utc):
                        await db.user_sessions.delete_one({"session_token": token})
                    else:
                        user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
                        if user:
                            return user
                except Exception as e:
                    logging.warning(f"Session expiry check error: {e}")
    
    # Fallback to session cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        return None
    
    # Check expiration
    expires_at = session.get("expires_at")
    if expires_at:
        try:
            if isinstance(expires_at, str):
                expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            else:
                expires_dt = expires_at
            
            if expires_dt < datetime.now(timezone.utc):
                await db.user_sessions.delete_one({"session_token": session_token})
                return None
        except Exception as e:
            logging.warning(f"Session expiry check error: {e}")
    
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user

def check_membership_status(user: dict) -> str:
    """Check user's membership status"""
    if user.get("membership_status") == "active":
        return "active"
    
    trial_ends = user.get("trial_ends_at")
    if trial_ends:
        try:
            trial_end_dt = datetime.fromisoformat(trial_ends.replace('Z', '+00:00'))
            if trial_end_dt > datetime.now(timezone.utc):
                return "trial"
        except:
            pass
    
    return "expired"

# ============== Routes ==============

@router.post("/register")
async def register_user(request: RegisterRequest, response: Response):
    """Register new user with email/password"""
    existing = await db.users.find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_doc = {
        "user_id": f"user_{uuid.uuid4().hex[:12]}",
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "auth_method": "email",
        "role": request.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "membership_status": "active" if request.role == "recruiter" else "trial",
        "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat() if request.role == "job_seeker" else None
    }
    
    await db.users.insert_one(user_doc)
    
    session_token = create_session_token()
    await create_session(user_doc["user_id"], session_token)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_doc["user_id"],
            "email": user_doc["email"],
            "name": user_doc["name"],
            "auth_method": "email",
            "role": user_doc["role"],
            "membership_status": user_doc["membership_status"],
            "created_at": user_doc["created_at"]
        }
    }

@router.post("/login")
async def login_user(login_data: UserLogin, response: Response):
    """Login with email and password"""
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Admin bypass
    if login_data.email == "admin@medmatch.com" and login_data.password == "MedMatch2026!":
        admin_user = await get_or_create_user(
            email="admin@medmatch.com",
            name="Admin",
            auth_method="admin"
        )
        
        previous_login = admin_user.get("last_login")
        
        await db.users.update_one(
            {"user_id": admin_user["user_id"]},
            {"$set": {"last_login": current_time, "previous_login": previous_login, "is_admin": True}}
        )
        
        session_token = create_session_token()
        await create_session(admin_user["user_id"], session_token)
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,
            path="/"
        )
        
        return {
            "access_token": session_token,
            "token_type": "bearer",
            "user": {
                "user_id": admin_user["user_id"],
                "email": "admin@medmatch.com",
                "name": "Admin",
                "auth_method": "admin",
                "is_admin": True,
                "created_at": admin_user.get("created_at", ""),
                "last_login": current_time,
                "previous_login": previous_login,
                "language": admin_user.get("language", "en"),
                "theme": admin_user.get("theme", "light")
            }
        }
    
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    previous_login = user.get("last_login")
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": current_time, "previous_login": previous_login}}
    )
    
    session_token = create_session_token()
    await create_session(user["user_id"], session_token)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user.get("name", ""),
            "auth_method": user.get("auth_method", "email"),
            "role": user.get("role", "job_seeker"),
            "membership_status": check_membership_status(user),
            "trial_ends_at": user.get("trial_ends_at"),
            "created_at": user.get("created_at", ""),
            "last_login": current_time,
            "previous_login": previous_login,
            "language": user.get("language", "en"),
            "theme": user.get("theme", "light")
        }
    }

@router.post("/google/session")
async def google_session_login(auth_data: Dict[str, Any], response: Response):
    """Handle Google OAuth session"""
    if "email" not in auth_data:
        raise HTTPException(status_code=400, detail="Email required")
    
    current_time = datetime.now(timezone.utc).isoformat()
    
    user = await get_or_create_user(
        email=auth_data["email"],
        name=auth_data.get("name", ""),
        auth_method="google"
    )
    
    previous_login = user.get("last_login")
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": current_time, "previous_login": previous_login}}
    )
    
    session_token = create_session_token()
    await create_session(user["user_id"], session_token)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user.get("name", ""),
            "auth_method": "google",
            "created_at": user.get("created_at", ""),
            "last_login": current_time,
            "previous_login": previous_login
        }
    }

@router.get("/apple/config")
async def get_apple_config():
    """Return Apple Sign In configuration for frontend"""
    return {
        "client_id": APPLE_SERVICE_ID,
        "redirect_uri": f"{os.environ.get('REACT_APP_BACKEND_URL', '')}/api/auth/apple/redirect",
        "scope": "name email",
        "response_type": "code id_token",
        "response_mode": "form_post",
        "configured": bool(APPLE_SERVICE_ID and APPLE_TEAM_ID)
    }

@router.post("/apple/redirect")
async def apple_redirect(request: Request, response: Response):
    """Handle Apple Sign In form_post redirect"""
    form_data = await request.form()
    id_token = form_data.get("id_token")
    code = form_data.get("code")
    user_data = form_data.get("user")
    
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token required")
    
    try:
        import jwt
        header = jwt.get_unverified_header(id_token)
        
        async with httpx.AsyncClient() as client:
            keys_response = await client.get("https://appleid.apple.com/auth/keys")
            apple_keys = keys_response.json()["keys"]
        
        key = next((k for k in apple_keys if k["kid"] == header["kid"]), None)
        if not key:
            raise HTTPException(status_code=400, detail="Invalid token key")
        
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(key)
        
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=APPLE_SERVICE_ID,
            issuer="https://appleid.apple.com"
        )
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Apple")
        
        name = ""
        if user_data:
            import json
            user_info = json.loads(user_data)
            name_info = user_info.get("name", {})
            name = f"{name_info.get('firstName', '')} {name_info.get('lastName', '')}".strip()
        
        user = await get_or_create_user(email=email, name=name, auth_method="apple")
        
        session_token = create_session_token()
        await create_session(user["user_id"], session_token)
        
        frontend_url = os.environ.get('REACT_APP_BACKEND_URL', '').replace('/api', '')
        redirect_url = f"{frontend_url}/#session_id={session_token}"
        
        return RedirectResponse(url=redirect_url, status_code=303)
        
    except Exception as e:
        logging.error(f"Apple auth error: {e}")
        raise HTTPException(status_code=401, detail=f"Apple authentication failed: {str(e)}")

@router.post("/apple/callback")
async def apple_callback(auth_request: AppleAuthRequest, response: Response):
    """Handle Apple Sign In callback (legacy)"""
    try:
        import jwt
        header = jwt.get_unverified_header(auth_request.id_token)
        
        async with httpx.AsyncClient() as client:
            keys_response = await client.get("https://appleid.apple.com/auth/keys")
            apple_keys = keys_response.json()["keys"]
        
        key = next((k for k in apple_keys if k["kid"] == header["kid"]), None)
        if not key:
            raise HTTPException(status_code=400, detail="Invalid token key")
        
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(key)
        
        payload = jwt.decode(
            auth_request.id_token,
            public_key,
            algorithms=["RS256"],
            audience=APPLE_SERVICE_ID,
            issuer="https://appleid.apple.com"
        )
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided")
        
        name = ""
        if auth_request.user:
            name_info = auth_request.user.get("name", {})
            name = f"{name_info.get('firstName', '')} {name_info.get('lastName', '')}".strip()
        
        user = await get_or_create_user(email=email, name=name, auth_method="apple")
        
        session_token = create_session_token()
        await create_session(user["user_id"], session_token)
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,
            path="/"
        )
        
        return {
            "access_token": session_token,
            "token_type": "bearer",
            "user": {
                "user_id": user["user_id"],
                "email": email,
                "name": user.get("name", ""),
                "auth_method": "apple"
            }
        }
        
    except Exception as e:
        logging.error(f"Apple auth error: {e}")
        raise HTTPException(status_code=401, detail="Apple authentication failed")

@router.post("/phone/send-otp")
async def send_phone_otp(request: PhoneLoginRequest):
    """Send OTP to phone number via Twilio"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE]):
        raise HTTPException(status_code=500, detail="Phone authentication not configured")
    
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE).verifications.create(
            to=request.phone_number,
            channel="sms"
        )
        
        return {"status": verification.status, "message": "OTP sent successfully"}
        
    except Exception as e:
        logging.error(f"Twilio error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/phone/verify-otp")
async def verify_phone_otp(request: VerifyOTPRequest, response: Response):
    """Verify OTP and login user"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE]):
        raise HTTPException(status_code=500, detail="Phone authentication not configured")
    
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        verification_check = client.verify.v2.services(TWILIO_VERIFY_SERVICE).verification_checks.create(
            to=request.phone_number,
            code=request.code
        )
        
        if verification_check.status != "approved":
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        user = await get_or_create_user(
            email=f"{request.phone_number}@phone.medmatch.local",
            name="",
            auth_method="phone"
        )
        
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"phone_number": request.phone_number}}
        )
        
        session_token = create_session_token()
        await create_session(user["user_id"], session_token)
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,
            path="/"
        )
        
        return {
            "access_token": session_token,
            "token_type": "bearer",
            "user": {
                "user_id": user["user_id"],
                "phone_number": request.phone_number,
                "auth_method": "phone"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail="OTP verification failed")

@router.get("/me")
async def get_current_user_endpoint(request: Request):
    """Get current authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user is admin
    is_admin = (
        user.get("is_admin", False) or 
        user.get("role") == "admin" or 
        user.get("email") == "admin@medmatch.com"
    )
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "auth_method": user.get("auth_method", ""),
        "role": "admin" if is_admin else user.get("role", "job_seeker"),
        "membership_status": "admin" if is_admin else check_membership_status(user),
        "trial_ends_at": user.get("trial_ends_at"),
        "created_at": user.get("created_at", ""),
        "last_login": user.get("last_login"),
        "previous_login": user.get("previous_login"),
        "is_admin": is_admin,
        "permissions": user.get("permissions", []) if is_admin else [],
        "user_type": user.get("user_type", "job_seeker")
    }

@router.post("/logout")
async def logout_user(request: Request, response: Response):
    """Logout and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.sessions.delete_one({"token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

@router.get("/preferences")
async def get_user_preferences(request: Request):
    """Get user preferences including language"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "language": user.get("language", "en"),
        "theme": user.get("theme", "light"),
        "timezone": user.get("timezone", "UTC"),
        "user_id": user.get("user_id")
    }

@router.put("/preferences")
async def update_user_preferences(prefs: UpdatePreferencesRequest, request: Request):
    """Update user preferences including language sync"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    update_data = {}
    if prefs.language:
        update_data["language"] = prefs.language
    if prefs.theme:
        update_data["theme"] = prefs.theme
    if prefs.timezone:
        update_data["timezone"] = prefs.timezone
    
    if update_data:
        update_data["preferences_updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"user_id": user.get("user_id")},
            {"$set": update_data}
        )
    
    return {
        "message": "Preferences updated",
        "language": prefs.language or user.get("language", "en"),
        "theme": prefs.theme or user.get("theme", "light"),
        "timezone": prefs.timezone or user.get("timezone", "UTC")
    }


# ============== Google Calendar OAuth ==============

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALENDAR_SCOPES = "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events"


@router.get("/google-calendar/config")
async def get_google_calendar_config(request: Request):
    """Get Google Calendar OAuth configuration"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user already has Google Calendar connected
    cal_auth = await db.google_calendar_auth.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "access_token": 0, "refresh_token": 0}
    )
    
    return {
        "configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "client_id": GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None,
        "scopes": GOOGLE_CALENDAR_SCOPES,
        "connected": cal_auth is not None,
        "connected_email": cal_auth.get("email") if cal_auth else None,
        "connected_at": cal_auth.get("connected_at") if cal_auth else None
    }


@router.post("/google-calendar/connect")
async def connect_google_calendar(request: Request):
    """Exchange authorization code for access token and store it"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    code = body.get("code")
    redirect_uri = body.get("redirect_uri")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google Calendar not configured on server")
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if token_response.status_code != 200:
                logging.error(f"Google token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            
            tokens = token_response.json()
            
            # Get user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            
            google_email = None
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                google_email = user_info.get("email")
        
        # Calculate token expiry
        expires_in = tokens.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Store tokens
        cal_auth_doc = {
            "user_id": user["user_id"],
            "email": google_email,
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "token_type": tokens.get("token_type", "Bearer"),
            "expires_at": expires_at.isoformat(),
            "scope": tokens.get("scope", GOOGLE_CALENDAR_SCOPES),
            "connected_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert - update if exists, insert if not
        await db.google_calendar_auth.update_one(
            {"user_id": user["user_id"]},
            {"$set": cal_auth_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Google Calendar connected successfully",
            "email": google_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Google Calendar connection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect Google Calendar")


@router.get("/google-calendar/token")
async def get_google_calendar_token(request: Request):
    """Get fresh Google Calendar access token (refreshes if expired)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    cal_auth = await db.google_calendar_auth.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not cal_auth:
        raise HTTPException(status_code=404, detail="Google Calendar not connected")
    
    # Check if token is expired
    expires_at_str = cal_auth.get("expires_at")
    if expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        
        # If token expires in less than 5 minutes, refresh it
        if expires_at < datetime.now(timezone.utc) + timedelta(minutes=5):
            refresh_token = cal_auth.get("refresh_token")
            
            if not refresh_token:
                # Need to re-authenticate
                await db.google_calendar_auth.delete_one({"user_id": user["user_id"]})
                raise HTTPException(status_code=401, detail="Token expired, please reconnect Google Calendar")
            
            try:
                async with httpx.AsyncClient() as client:
                    refresh_response = await client.post(
                        "https://oauth2.googleapis.com/token",
                        data={
                            "client_id": GOOGLE_CLIENT_ID,
                            "client_secret": GOOGLE_CLIENT_SECRET,
                            "refresh_token": refresh_token,
                            "grant_type": "refresh_token"
                        }
                    )
                    
                    if refresh_response.status_code != 200:
                        await db.google_calendar_auth.delete_one({"user_id": user["user_id"]})
                        raise HTTPException(status_code=401, detail="Failed to refresh token, please reconnect")
                    
                    new_tokens = refresh_response.json()
                    
                    # Calculate new expiry
                    new_expires_in = new_tokens.get("expires_in", 3600)
                    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_expires_in)
                    
                    # Update stored tokens
                    await db.google_calendar_auth.update_one(
                        {"user_id": user["user_id"]},
                        {"$set": {
                            "access_token": new_tokens["access_token"],
                            "expires_at": new_expires_at.isoformat()
                        }}
                    )
                    
                    return {
                        "access_token": new_tokens["access_token"],
                        "expires_in": new_expires_in
                    }
                    
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Token refresh error: {e}")
                raise HTTPException(status_code=500, detail="Failed to refresh token")
    
    return {
        "access_token": cal_auth["access_token"],
        "expires_in": 3600  # Approximate
    }


@router.delete("/google-calendar/disconnect")
async def disconnect_google_calendar(request: Request):
    """Disconnect Google Calendar integration"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.google_calendar_auth.delete_one({"user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Google Calendar not connected")
    
    return {"success": True, "message": "Google Calendar disconnected"}


# Export helper functions for use in other modules
__all__ = [
    'router', 
    'get_current_user', 
    'check_membership_status',
    'create_session',
    'create_session_token',
    'get_or_create_user'
]
