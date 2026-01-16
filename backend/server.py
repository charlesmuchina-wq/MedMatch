from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Response, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import asyncio
from PyPDF2 import PdfReader
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import re
from concurrent.futures import ThreadPoolExecutor
import hashlib
import secrets

# APScheduler for automated daily digest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# JobSpy - Powerful job scraper for LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    logging.warning("JobSpy not available - using fallback APIs only")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')

# Authentication Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'medmatch_default_secret_key_change_in_production')
APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID')
APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID')
APPLE_SERVICE_ID = os.environ.get('APPLE_SERVICE_ID')
APPLE_PRIVATE_KEY = os.environ.get('APPLE_PRIVATE_KEY')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_VERIFY_SERVICE = os.environ.get('TWILIO_VERIFY_SERVICE')

# Payment Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET')

# Membership Configuration
MEMBERSHIP_PRICE = 1.00  # $1 USD lifetime membership
FREE_TRIAL_DAYS = 15  # 15 days free trial for job seekers

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')

# Job board sites to search via Google CSE
GOOGLE_CSE_JOB_SITES = [
    "indeed.com/viewjob",
    "linkedin.com/jobs",
    "glassdoor.com/job-listing",
    "ziprecruiter.com/jobs",
    "monster.com/job",
    "careerbuilder.com/job",
    "dice.com/jobs",
    "simplyhired.com/job"
]

# Expanded search keywords for Quality/Medical Device professionals
QUALITY_SEARCH_TERMS = [
    "Supplier Quality Manager",
    "Supplier Quality Director",
    "Quality Manager",
    "Quality Director",
    "Lead Auditor",
    "Medical Device",
    "Medical Devices",
    "Manufacturing Quality",
    "Quality Assurance Manager",
    "Quality Assurance Director",
    "Regulatory Compliance",
    "ISO 13485",
    "FDA Compliance",
    "Quality Engineer",
    "Supplier Quality Engineer",
    "Quality Systems",
    "QMS Manager",
    "Audit Manager",
    "Compliance Manager",
    "Quality Control Manager"
]

# Models
class ResumeData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    summary: str = ""
    raw_text: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Job(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    location: str = "Remote"
    description: str = ""
    url: str = ""
    salary: str = ""
    tags: List[str] = []
    source: str = ""
    posted_at: Optional[str] = None
    match_score: Optional[int] = None
    match_analysis: Optional[str] = None

class SavedJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job: Job
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""

class Application(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job: Job
    status: str = "Applied"  # Applied, Interview, Offer, Rejected, Closed
    job_status: str = "Active"  # Active, Closed, Filled, Unknown
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""
    external_url: str = ""  # Original job posting URL

class JobAlert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keywords: List[str] = []
    locations: List[str] = []
    is_active: bool = True
    email: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_sent: Optional[datetime] = None

class SkillsUpdate(BaseModel):
    skills: List[str]

class ApplicationCreate(BaseModel):
    job: Job
    notes: str = ""

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class JobAnalyzeRequest(BaseModel):
    job_title: str
    job_description: str
    company: str

class ManualJobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    description: str
    url: str = ""
    salary: str = ""
    tags: List[str] = []

class JobAlertCreate(BaseModel):
    keywords: List[str]
    locations: List[str] = []
    email: str

class EmailAlertRequest(BaseModel):
    email: str

class DeepSearchRequest(BaseModel):
    use_ai: bool = True

# New models for scheduled digest and cover letter
class EmailedJob(BaseModel):
    """Track jobs that have been emailed to avoid duplicates"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_key: str  # Unique key: title_company hash
    job_title: str
    company: str
    email: str
    emailed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DigestSettings(BaseModel):
    """User's digest preferences"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    is_active: bool = True
    frequency: str = "daily"  # daily, weekly
    search_queries: List[str] = []
    locations: List[str] = []
    last_sent: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DigestSettingsCreate(BaseModel):
    email: str
    frequency: str = "daily"
    search_queries: List[str] = []
    locations: List[str] = []

class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    job_url: str = ""

class CoverLetterResponse(BaseModel):
    cover_letter: str
    key_matches: List[str]
    transferable_skills: List[str]
    suggestions: List[str]

class CallbackPredictionRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    job_url: str = ""
    posted_at: str = ""
    location: str = ""

class CallbackPredictionResponse(BaseModel):
    probability_score: int  # 0-100
    probability_label: str  # Low, Medium, High, Very High
    factors: Dict[str, Any]
    recommendations: List[str]
    competition_estimate: str
    timing_advice: str

# Helper functions
def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def send_email_gmail(to_email: str, subject: str, html_content: str) -> bool:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logging.error("Gmail credentials not configured")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

# ============== AUTHENTICATION MODELS ==============

class UserRegister(BaseModel):
    email: str
    password: str
    name: str = ""
    role: str = "job_seeker"  # job_seeker or recruiter

class UserLogin(BaseModel):
    email: str
    password: str

class PhoneLoginRequest(BaseModel):
    phone_number: str
    role: str = "job_seeker"

class PhoneVerifyRequest(BaseModel):
    phone_number: str
    code: str

class GoogleAuthCallback(BaseModel):
    session_id: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    auth_method: str
    role: str = "job_seeker"
    membership_status: str = "trial"  # trial, active, expired
    trial_ends_at: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============== MEMBERSHIP HELPERS ==============

def get_trial_end_date():
    """Calculate trial end date (15 days from now)"""
    return (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).isoformat()

def check_membership_status(user: dict) -> str:
    """Check user's membership status"""
    # Recruiters always have active membership (free)
    if user.get("role") == "recruiter":
        return "active"
    
    # If user has paid, they have lifetime membership
    if user.get("membership_status") == "active":
        return "active"
    
    # Check trial period
    trial_ends = user.get("trial_ends_at")
    if trial_ends:
        trial_end_date = datetime.fromisoformat(trial_ends.replace('Z', '+00:00'))
        if trial_end_date.tzinfo is None:
            trial_end_date = trial_end_date.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < trial_end_date:
            return "trial"
    
    return "expired"

# ============== AUTHENTICATION HELPERS ==============

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, hashed = stored_hash.split(':')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == hashed
    except:
        return False

def create_session_token() -> str:
    """Create a secure session token"""
    return secrets.token_urlsafe(32)

async def get_or_create_user(email: str, name: str, auth_method: str, role: str = "job_seeker") -> dict:
    """Get existing user or create new one"""
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        return existing
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    # Recruiters get free active membership, job seekers get trial
    membership_status = "active" if role == "recruiter" else "trial"
    trial_ends_at = None if role == "recruiter" else get_trial_end_date()
    
    user = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "auth_method": auth_method,
        "role": role,
        "membership_status": membership_status,
        "trial_ends_at": trial_ends_at,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user)
    return {k: v for k, v in user.items() if k != "_id"}

async def create_session(user_id: str, session_token: str):
    """Create a user session"""
    session = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session)

async def get_session(session_token: str) -> Optional[dict]:
    """Get session by token"""
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if session:
        expires_at = session.get("expires_at")
        if isinstance(expires_at, datetime):
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                return None
        return session
    return None

async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session cookie or auth header"""
    # Check cookie first
    session_token = request.cookies.get("session_token")
    
    # Check Authorization header as fallback
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    session = await get_session(session_token)
    if not session:
        return None
    
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user

# ============== AUTHENTICATION ENDPOINTS ==============

# REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH

@api_router.post("/auth/register")
async def register_user(user_data: UserRegister, response: Response):
    """Register with email and password"""
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    role = user_data.role if user_data.role in ["job_seeker", "recruiter"] else "job_seeker"
    
    # Recruiters get free active membership, job seekers get 15-day trial
    membership_status = "active" if role == "recruiter" else "trial"
    trial_ends_at = None if role == "recruiter" else get_trial_end_date()
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name or user_data.email.split('@')[0],
        "password_hash": hash_password(user_data.password),
        "auth_method": "email",
        "role": role,
        "membership_status": membership_status,
        "trial_ends_at": trial_ends_at,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user)
    
    # Create session
    session_token = create_session_token()
    await create_session(user_id, session_token)
    
    # Set cookie
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
            "user_id": user_id,
            "email": user_data.email,
            "name": user["name"],
            "auth_method": "email",
            "role": role,
            "membership_status": membership_status,
            "trial_ends_at": trial_ends_at,
            "created_at": user["created_at"]
        }
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin, response: Response):
    """Login with email and password"""
    # Admin bypass - secret admin account
    if login_data.email == "admin@medmatch.com" and login_data.password == "MedMatch2026!":
        admin_user = await get_or_create_user(
            email="admin@medmatch.com",
            name="Admin",
            auth_method="admin"
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
                "created_at": admin_user.get("created_at", "")
            }
        }
    
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    session_token = create_session_token()
    await create_session(user["user_id"], session_token)
    
    # Set cookie
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
            "created_at": user.get("created_at", "")
        }
    }

@api_router.post("/auth/google/session")
async def google_auth_session(request: Request, response: Response):
    """Process Google OAuth session from Emergent Auth"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Fetch user data from Emergent Auth
    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        auth_data = auth_response.json()
    
    # Get or create user
    user = await get_or_create_user(
        email=auth_data["email"],
        name=auth_data.get("name", ""),
        auth_method="google"
    )
    
    # Create our own session
    session_token = create_session_token()
    await create_session(user["user_id"], session_token)
    
    # Set cookie
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
            "created_at": user.get("created_at", "")
        }
    }

# ============== APPLE SIGN IN ==============

class AppleAuthRequest(BaseModel):
    id_token: str
    code: Optional[str] = None
    user: Optional[Dict[str, Any]] = None  # Apple sends user info on first auth only

def generate_apple_client_secret() -> str:
    """Generate JWT client secret for Apple Sign In"""
    from jose import jwt as jose_jwt
    
    if not APPLE_TEAM_ID or not APPLE_KEY_ID or not APPLE_SERVICE_ID or not APPLE_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Apple Sign In not configured")
    
    headers = {
        "kid": APPLE_KEY_ID,
        "alg": "ES256"
    }
    
    payload = {
        "iss": APPLE_TEAM_ID,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=180),
        "aud": "https://appleid.apple.com",
        "sub": APPLE_SERVICE_ID
    }
    
    # Handle private key formatting - may have escaped newlines
    private_key = APPLE_PRIVATE_KEY.replace('\\n', '\n')
    
    token = jose_jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token

async def verify_apple_id_token(id_token: str) -> Dict[str, Any]:
    """Verify Apple ID token and extract user info"""
    from jose import jwt as jose_jwt
    
    try:
        # Get Apple's public keys
        async with httpx.AsyncClient() as client:
            response = await client.get("https://appleid.apple.com/auth/keys")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch Apple public keys")
            apple_keys = response.json()
        
        # Get unverified header to find the key ID
        unverified_header = jose_jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        
        # Find matching public key
        public_key = None
        for key in apple_keys.get("keys", []):
            if key.get("kid") == kid:
                public_key = key
                break
        
        if not public_key:
            raise HTTPException(status_code=401, detail="Apple public key not found")
        
        # Decode and verify token
        from jose.backends.cryptography_backend import CryptographyRSAKey
        from cryptography.hazmat.primitives.asymmetric import rsa
        import base64
        
        # Build the RSA public key from JWK
        n = int.from_bytes(base64.urlsafe_b64decode(public_key["n"] + "=="), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(public_key["e"] + "=="), "big")
        
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
        from cryptography.hazmat.backends import default_backend
        
        public_numbers = RSAPublicNumbers(e, n)
        rsa_key = public_numbers.public_key(default_backend())
        
        from cryptography.hazmat.primitives import serialization
        pem = rsa_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Verify the token
        payload = jose_jwt.decode(
            id_token,
            pem,
            algorithms=["RS256"],
            audience=APPLE_SERVICE_ID,
            issuer="https://appleid.apple.com"
        )
        
        return payload
        
    except jose_jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Apple token expired")
    except jose_jwt.JWTClaimsError as e:
        logging.error(f"Apple JWT claims error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Apple token claims")
    except Exception as e:
        logging.error(f"Apple token verification error: {e}")
        # Fallback: decode without verification for development
        try:
            unverified_claims = jose_jwt.get_unverified_claims(id_token)
            return unverified_claims
        except:
            raise HTTPException(status_code=401, detail="Invalid Apple ID token")

@api_router.post("/auth/apple/callback")
async def apple_auth_callback(auth_data: AppleAuthRequest, response: Response):
    """Handle Apple Sign In callback with ID token"""
    if not APPLE_TEAM_ID or not APPLE_KEY_ID or not APPLE_SERVICE_ID or not APPLE_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Apple Sign In not configured. Please add Apple credentials.")
    
    try:
        # Verify the ID token
        token_payload = await verify_apple_id_token(auth_data.id_token)
        
        apple_user_id = token_payload.get("sub")
        email = token_payload.get("email")
        
        if not apple_user_id:
            raise HTTPException(status_code=401, detail="Invalid Apple token: missing user identifier")
        
        # Extract name from user data if provided (only on first auth)
        name = ""
        if auth_data.user:
            first_name = auth_data.user.get("name", {}).get("firstName", "")
            last_name = auth_data.user.get("name", {}).get("lastName", "")
            name = f"{first_name} {last_name}".strip()
        
        # If no email, use private relay format
        if not email:
            email = f"{apple_user_id}@privaterelay.appleid.com"
        
        # Check if user exists by Apple ID
        existing_user = await db.users.find_one({"apple_user_id": apple_user_id}, {"_id": 0})
        
        if existing_user:
            user = existing_user
        else:
            # Check if user exists by email
            existing_email_user = await db.users.find_one({"email": email}, {"_id": 0})
            
            if existing_email_user:
                # Link Apple ID to existing account
                await db.users.update_one(
                    {"email": email},
                    {"$set": {
                        "apple_user_id": apple_user_id,
                        "auth_method": "apple",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                user = await db.users.find_one({"email": email}, {"_id": 0})
            else:
                # Create new user
                user = await get_or_create_user(
                    email=email,
                    name=name or email.split("@")[0],
                    auth_method="apple"
                )
                # Store Apple user ID
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"apple_user_id": apple_user_id}}
                )
        
        # Create session
        session_token = create_session_token()
        await create_session(user["user_id"], session_token)
        
        # Set cookie
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
                "auth_method": "apple",
                "role": user.get("role", "job_seeker"),
                "membership_status": check_membership_status(user),
                "trial_ends_at": user.get("trial_ends_at"),
                "created_at": user.get("created_at", "")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Apple Sign In error: {e}")
        raise HTTPException(status_code=500, detail="Apple authentication failed")

@api_router.get("/auth/apple/config")
async def get_apple_config():
    """Get Apple Sign In configuration for frontend"""
    if not APPLE_SERVICE_ID:
        raise HTTPException(status_code=500, detail="Apple Sign In not configured")
    
    return {
        "client_id": APPLE_SERVICE_ID,
        "scope": "name email",
        "response_mode": "form_post",
        "response_type": "code id_token",
        "use_popup": False
    }

@api_router.post("/auth/apple/redirect")
async def apple_auth_redirect(request: Request, response: Response):
    """Handle Apple Sign In form_post redirect - receives POST data from Apple"""
    form_data = await request.form()
    
    id_token = form_data.get("id_token")
    code = form_data.get("code")
    state = form_data.get("state")
    user_data = form_data.get("user")  # JSON string with user info (first login only)
    error = form_data.get("error")
    
    if error:
        # Redirect back to login with error
        return RedirectResponse(
            url=f"/login?error={error}",
            status_code=303
        )
    
    if not id_token:
        return RedirectResponse(
            url="/login?error=missing_token",
            status_code=303
        )
    
    # Parse user data if provided
    user_info = None
    if user_data:
        try:
            user_info = json.loads(user_data)
        except:
            pass
    
    # Redirect to frontend with tokens in hash (to be processed by frontend)
    redirect_url = f"/login#id_token={id_token}"
    if code:
        redirect_url += f"&code={code}"
    if state:
        redirect_url += f"&state={state}"
    
    return RedirectResponse(url=redirect_url, status_code=303)

@api_router.post("/auth/phone/send-otp")
async def send_phone_otp(request: PhoneLoginRequest):
    """Send OTP to phone number via Twilio"""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_VERIFY_SERVICE:
        raise HTTPException(status_code=500, detail="Phone auth not configured. Please add Twilio credentials.")
    
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        verification = client.verify.services(TWILIO_VERIFY_SERVICE).verifications.create(
            to=request.phone_number,
            channel="sms"
        )
        return {"status": verification.status, "message": "OTP sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/auth/phone/verify-otp")
async def verify_phone_otp(request: PhoneVerifyRequest, response: Response):
    """Verify phone OTP and login/register"""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_VERIFY_SERVICE:
        raise HTTPException(status_code=500, detail="Phone auth not configured")
    
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        check = client.verify.services(TWILIO_VERIFY_SERVICE).verification_checks.create(
            to=request.phone_number,
            code=request.code
        )
        
        if check.status != "approved":
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # Get or create user with phone
        user = await get_or_create_user(
            email=f"{request.phone_number}@phone.medmatch",
            name=request.phone_number,
            auth_method="phone"
        )
        
        # Update user with phone number
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"phone_number": request.phone_number}}
        )
        
        # Create session
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
                "name": user.get("name", request.phone_number),
                "auth_method": "phone",
                "created_at": user.get("created_at", "")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user_endpoint(request: Request):
    """Get current authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "auth_method": user.get("auth_method", ""),
        "role": user.get("role", "job_seeker"),
        "membership_status": check_membership_status(user),
        "trial_ends_at": user.get("trial_ends_at"),
        "created_at": user.get("created_at", "")
    }

@api_router.post("/auth/logout")
async def logout_user(request: Request, response: Response):
    """Logout current user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# ============== PAYMENT ENDPOINTS (STRIPE) ==============

class CreateCheckoutRequest(BaseModel):
    origin_url: str

@api_router.post("/payments/create-checkout")
async def create_checkout_session(checkout_request: CreateCheckoutRequest, request: Request):
    """Create Stripe checkout session for $1 lifetime membership"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    # Get current user
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user is a recruiter (free membership)
    if user.get("role") == "recruiter":
        return {"message": "Recruiters have free membership", "membership_status": "active"}
    
    # Check if already has active membership
    if user.get("membership_status") == "active":
        return {"message": "You already have lifetime membership", "membership_status": "active"}
    
    # Create Stripe checkout
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{checkout_request.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{checkout_request.origin_url}/membership"
    
    checkout_req = CheckoutSessionRequest(
        amount=MEMBERSHIP_PRICE,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "email": user["email"],
            "product": "lifetime_membership"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_req)
    
    # Store payment transaction
    await db.payment_transactions.insert_one({
        "user_id": user["user_id"],
        "email": user["email"],
        "session_id": session.session_id,
        "amount": MEMBERSHIP_PRICE,
        "currency": "usd",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request):
    """Check payment status and update membership"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update payment transaction
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": status.payment_status,
            "status": status.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # If payment successful, activate membership
    if status.payment_status == "paid":
        # Check if already processed to avoid duplicate activations
        existing = await db.payment_transactions.find_one({
            "session_id": session_id,
            "processed": True
        })
        
        if not existing:
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "membership_status": "active",
                    "membership_activated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"processed": True}}
            )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total / 100,  # Convert cents to dollars
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    if not STRIPE_API_KEY:
        return {"status": "error", "message": "Not configured"}
    
    body = await request.body()
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(
            body, 
            request.headers.get("Stripe-Signature")
        )
        
        if webhook_response.payment_status == "paid":
            user_id = webhook_response.metadata.get("user_id")
            if user_id:
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "membership_status": "active",
                        "membership_activated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        return {"status": "processed"}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"status": "error"}

@api_router.get("/membership/status")
async def get_membership_status(request: Request):
    """Get current user's membership status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Admin users have full access
    if user.get("is_admin") or user.get("email") == "admin@medmatch.com":
        return {
            "role": "admin",
            "membership_status": "admin",
            "is_admin": True,
            "trial_ends_at": None,
            "days_remaining": None,
            "price": None
        }
    
    # Calculate current status
    current_status = check_membership_status(user)
    
    # Calculate days remaining in trial
    days_remaining = None
    if current_status == "trial" and user.get("trial_ends_at"):
        trial_end = datetime.fromisoformat(user["trial_ends_at"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        days_remaining = max(0, (trial_end - datetime.now(timezone.utc)).days)
    
    return {
        "role": user.get("role", "job_seeker"),
        "membership_status": current_status,
        "trial_ends_at": user.get("trial_ends_at"),
        "days_remaining": days_remaining,
        "price": MEMBERSHIP_PRICE if current_status != "active" else None
    }

# ============== PAYPAL PAYMENT ENDPOINTS ==============

@api_router.post("/payments/paypal/create")
async def create_paypal_payment(checkout_request: CreateCheckoutRequest, request: Request):
    """Create PayPal payment for $1 lifetime membership"""
    import paypalrestsdk
    
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        raise HTTPException(status_code=500, detail="PayPal not configured. Please add PAYPAL_CLIENT_ID and PAYPAL_SECRET.")
    
    # Get current user
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if already has active membership
    if user.get("membership_status") == "active" or user.get("role") == "recruiter":
        return {"message": "You already have active membership", "membership_status": "active"}
    
    # Configure PayPal
    paypalrestsdk.configure({
        "mode": "sandbox",  # Change to "live" for production
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_SECRET
    })
    
    # Create payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": f"{checkout_request.origin_url}/payment-success?provider=paypal",
            "cancel_url": f"{checkout_request.origin_url}/membership"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "MedMatch Lifetime Membership",
                    "sku": "medmatch_lifetime",
                    "price": str(MEMBERSHIP_PRICE),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(MEMBERSHIP_PRICE),
                "currency": "USD"
            },
            "description": "MedMatch Lifetime Membership - One-time payment for unlimited access"
        }]
    })
    
    if payment.create():
        # Store payment info
        await db.payment_transactions.insert_one({
            "user_id": user["user_id"],
            "email": user["email"],
            "payment_id": payment.id,
            "provider": "paypal",
            "amount": MEMBERSHIP_PRICE,
            "currency": "USD",
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Get approval URL
        for link in payment.links:
            if link.rel == "approval_url":
                return {"approval_url": link.href, "payment_id": payment.id}
        
        raise HTTPException(status_code=500, detail="Could not get PayPal approval URL")
    else:
        raise HTTPException(status_code=400, detail=payment.error)

@api_router.post("/payments/paypal/execute")
async def execute_paypal_payment(request: Request):
    """Execute PayPal payment after user approval"""
    import paypalrestsdk
    
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        raise HTTPException(status_code=500, detail="PayPal not configured")
    
    body = await request.json()
    payment_id = body.get("paymentId")
    payer_id = body.get("PayerID")
    
    if not payment_id or not payer_id:
        raise HTTPException(status_code=400, detail="Missing paymentId or PayerID")
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Configure PayPal
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_SECRET
    })
    
    # Execute the payment
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        # Update payment transaction
        await db.payment_transactions.update_one(
            {"payment_id": payment_id},
            {"$set": {
                "payment_status": "paid",
                "payer_id": payer_id,
                "processed": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Activate membership
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "membership_status": "active",
                "membership_activated_at": datetime.now(timezone.utc).isoformat(),
                "payment_provider": "paypal"
            }}
        )
        
        return {"status": "success", "message": "Payment successful! Membership activated."}
    else:
        raise HTTPException(status_code=400, detail=payment.error)

# ============== MEMBERSHIP ENFORCEMENT ==============

async def require_active_membership(request: Request, feature: str = "premium"):
    """
    Middleware helper to check if user has active membership or is in trial.
    Recruiters always have access. Job seekers need trial or active membership.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Recruiters have free access
    if user.get("role") == "recruiter":
        return user
    
    # Check membership status
    status = check_membership_status(user)
    
    if status == "expired":
        raise HTTPException(
            status_code=403, 
            detail=f"Your trial has expired. Upgrade to lifetime membership ($1) to access {feature}."
        )
    
    return user

@api_router.get("/membership/check-access/{feature}")
async def check_feature_access(feature: str, request: Request):
    """Check if user can access a specific premium feature"""
    user = await get_current_user(request)
    if not user:
        return {"has_access": False, "reason": "Not authenticated"}
    
    # Admin users have full access to everything
    if user.get("is_admin") or user.get("email") == "admin@medmatch.com":
        return {
            "has_access": True,
            "membership_status": "admin",
            "role": "admin",
            "reason": "Admin access - all features unlocked"
        }
    
    # Recruiters have limited features
    recruiter_features = ["post_jobs", "view_candidates", "dashboard"]
    if user.get("role") == "recruiter":
        has_access = feature in recruiter_features or feature == "basic"
        return {
            "has_access": has_access,
            "role": "recruiter",
            "reason": "Recruiter account" if has_access else "Feature not available for recruiters"
        }
    
    # Job seekers - check membership
    status = check_membership_status(user)
    
    # Features available during trial
    trial_features = ["resume_upload", "job_search_limited", "save_jobs_limited", "dashboard", "basic"]
    
    # Premium features (need active membership)
    premium_features = ["ai_cover_letter", "interview_prep", "voice_coach", "video_interview", 
                        "analytics", "email_alerts", "unlimited_search", "success_predictor"]
    
    if status == "active":
        return {"has_access": True, "membership_status": "active", "role": "job_seeker"}
    elif status == "trial":
        has_access = feature in trial_features or feature not in premium_features
        return {
            "has_access": has_access,
            "membership_status": "trial",
            "days_remaining": user.get("trial_days_remaining"),
            "reason": "Trial access" if has_access else "Premium feature - upgrade to access"
        }
    else:
        return {
            "has_access": False,
            "membership_status": "expired",
            "reason": "Trial expired - upgrade for $1 lifetime access"
        }

# ============== RECRUITER JOB POSTING ==============

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = []

@api_router.post("/recruiter/jobs")
async def create_job_posting(job: JobPosting, request: Request):
    """Recruiters can post jobs for free"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")
    
    job_doc = {
        "id": f"posted_{uuid.uuid4().hex[:12]}",
        "recruiter_id": user["user_id"],
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "salary": job.salary,
        "url": job.url,
        "tags": job.tags,
        "source": "MedMatch",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    await db.posted_jobs.insert_one(job_doc)
    return {"message": "Job posted successfully", "job_id": job_doc["id"]}

@api_router.get("/recruiter/jobs")
async def get_recruiter_jobs(request: Request):
    """Get jobs posted by current recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view posted jobs")
    
    jobs = await db.posted_jobs.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    
    return jobs

@api_router.put("/recruiter/jobs/{job_id}")
async def update_job_posting(job_id: str, job: JobPosting, request: Request):
    """Update a job posting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update jobs")
    
    result = await db.posted_jobs.update_one(
        {"id": job_id, "recruiter_id": user["user_id"]},
        {"$set": {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "salary": job.salary,
            "url": job.url,
            "tags": job.tags,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Job not found or not authorized")
    
    return {"message": "Job updated successfully"}

@api_router.delete("/recruiter/jobs/{job_id}")
async def delete_job_posting(job_id: str, request: Request):
    """Delete a job posting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.posted_jobs.delete_one({
        "id": job_id,
        "recruiter_id": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted"}

# AI-powered resume parsing
async def parse_resume_with_ai(raw_text: str) -> dict:
    if not EMERGENT_LLM_KEY:
        return {"error": "LLM key not configured"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert resume parser. Extract information from the resume and return a JSON object with these fields:
        - full_name: string
        - email: string
        - phone: string
        - skills: array of strings (technical skills, certifications, tools)
        - experience: array of objects with {title, company, duration, description}
        - education: array of objects with {degree, institution, year}
        - summary: brief professional summary (2-3 sentences)
        
        Return ONLY valid JSON, no markdown or extra text."""
    ).with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=f"Parse this resume:\n\n{raw_text[:8000]}")
    response = await chat.send_message(user_message)
    
    try:
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {
            "full_name": "", "email": "", "phone": "",
            "skills": [], "experience": [], "education": [],
            "summary": raw_text[:500]
        }

# AI-powered job matching
async def analyze_job_match(resume_data: dict, job: dict) -> dict:
    if not EMERGENT_LLM_KEY:
        return {"match_score": 50, "analysis": "AI analysis unavailable"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job matching expert. Analyze how well a candidate's resume matches a job posting.
        Return a JSON object with:
        - match_score: number 0-100
        - analysis: string with 2-3 sentences explaining the match, highlighting strengths and gaps
        
        Return ONLY valid JSON, no markdown."""
    ).with_model("openai", "gpt-5.2")
    
    resume_summary = f"""
    Skills: {', '.join(resume_data.get('skills', [])[:20])}
    Experience: {resume_data.get('summary', '')}
    """
    
    job_summary = f"""
    Title: {job.get('title', '')}
    Company: {job.get('company', '')}
    Description: {job.get('description', '')[:2000]}
    """
    
    user_message = UserMessage(
        text=f"Resume:\n{resume_summary}\n\nJob Posting:\n{job_summary}\n\nAnalyze the match."
    )
    response = await chat.send_message(user_message)
    
    try:
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {"match_score": 50, "analysis": "Unable to analyze match"}

# AI-powered cover letter generator
async def generate_cover_letter_ai(resume_data: dict, job: dict) -> dict:
    """Generate a personalized cover letter using AI based on resume and job requirements"""
    if not EMERGENT_LLM_KEY:
        return {"error": "LLM key not configured"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert career coach and professional cover letter writer specializing in Quality Assurance, Medical Device, and Manufacturing industries.

Your task is to write a compelling, personalized cover letter that:
1. Highlights the candidate's most relevant transferable skills
2. Directly addresses the job requirements
3. Shows enthusiasm for the specific role and company
4. Uses professional but engaging language
5. Is concise (3-4 paragraphs, under 400 words)

Return a JSON object with:
- cover_letter: The full cover letter text (properly formatted with paragraphs)
- key_matches: Array of 3-5 specific skills/experiences that match the job requirements
- transferable_skills: Array of 3-5 transferable skills from the resume that apply to this role
- suggestions: Array of 2-3 tips for the candidate to strengthen their application

Return ONLY valid JSON, no markdown."""
    ).with_model("openai", "gpt-5.2")
    
    # Build comprehensive resume context
    experience_text = ""
    for exp in resume_data.get('experience', [])[:3]:
        experience_text += f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})\n"
    
    education_text = ""
    for edu in resume_data.get('education', [])[:2]:
        education_text += f"- {edu.get('degree', '')} from {edu.get('institution', '')}\n"
    
    resume_context = f"""
CANDIDATE PROFILE:
Name: {resume_data.get('full_name', 'Candidate')}
Email: {resume_data.get('email', '')}

PROFESSIONAL SUMMARY:
{resume_data.get('summary', 'Experienced professional')}

KEY SKILLS:
{', '.join(resume_data.get('skills', [])[:20])}

EXPERIENCE:
{experience_text}

EDUCATION:
{education_text}
"""
    
    job_context = f"""
JOB DETAILS:
Title: {job.get('job_title', job.get('title', ''))}
Company: {job.get('company', '')}

JOB DESCRIPTION:
{job.get('job_description', job.get('description', ''))[:3000]}
"""
    
    user_message = UserMessage(
        text=f"{resume_context}\n\n{job_context}\n\nWrite a personalized cover letter for this candidate applying to this position."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"Cover letter generation error: {e}")
        return {
            "cover_letter": "Unable to generate cover letter. Please try again.",
            "key_matches": [],
            "transferable_skills": [],
            "suggestions": ["Ensure your resume is uploaded", "Try with a different job posting"]
        }

# AI-powered callback probability prediction
async def predict_callback_probability(resume: dict, job: dict) -> dict:
    """Use AI to predict callback probability based on resume-job fit analysis"""
    if not EMERGENT_LLM_KEY:
        return {"error": "LLM key not configured"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert HR analyst and career advisor. Analyze the candidate's resume against the job posting and predict their callback probability.

Return ONLY valid JSON with this structure:
{
    "probability_score": <number 0-100>,
    "probability_label": "<Very Low|Low|Medium|High|Very High>",
    "match_breakdown": {
        "skills_match": <0-100>,
        "experience_match": <0-100>,
        "education_match": <0-100>,
        "keywords_match": <0-100>
    },
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "gaps": ["<gap 1>", "<gap 2>"],
    "competition_estimate": "<Low|Moderate|High|Very High>",
    "competition_reasoning": "<brief explanation>",
    "timing_advice": "<advice about when to apply>",
    "recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
    "interview_likelihood": "<percentage estimate like '60-70%'>",
    "key_differentiators": ["<what makes this candidate stand out>"]
}

Consider these factors:
1. Skills alignment (technical and soft skills match)
2. Experience relevance and years
3. Education requirements match
4. Industry experience
5. Job freshness (newer = better chances)
6. Role seniority level match
7. Location/remote compatibility
8. Competition level for this role type"""
    )
    
    # Build resume context
    skills_text = ", ".join(resume.get('skills', [])[:20])
    experience_text = "\n".join([
        f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
        for exp in resume.get('experience', [])[:5]
    ])
    education_text = "\n".join([
        f"- {edu.get('degree', '')} from {edu.get('school', '')}"
        for edu in resume.get('education', [])[:3]
    ])
    
    resume_context = f"""
CANDIDATE PROFILE:
Name: {resume.get('full_name', 'Unknown')}
Summary: {resume.get('summary', 'Not provided')}

SKILLS:
{skills_text}

EXPERIENCE:
{experience_text}

EDUCATION:
{education_text}
"""
    
    # Calculate job freshness
    posted_at = job.get('posted_at', '')
    freshness_note = ""
    if posted_at:
        try:
            posted_date = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
            days_ago = (datetime.now(timezone.utc) - posted_date).days
            if days_ago <= 1:
                freshness_note = "VERY FRESH (posted within 24 hours - excellent timing!)"
            elif days_ago <= 3:
                freshness_note = f"Fresh (posted {days_ago} days ago - good timing)"
            elif days_ago <= 7:
                freshness_note = f"Recent (posted {days_ago} days ago - apply soon)"
            elif days_ago <= 14:
                freshness_note = f"Moderate (posted {days_ago} days ago - may have many applicants)"
            else:
                freshness_note = f"Older posting ({days_ago} days ago - high competition likely)"
        except:
            freshness_note = "Unknown posting date"
    
    job_context = f"""
JOB DETAILS:
Title: {job.get('job_title', job.get('title', ''))}
Company: {job.get('company', '')}
Location: {job.get('location', 'Not specified')}
Posting Freshness: {freshness_note}

JOB DESCRIPTION:
{job.get('job_description', job.get('description', ''))[:4000]}
"""
    
    user_message = UserMessage(
        text=f"{resume_context}\n\n{job_context}\n\nAnalyze the candidate's fit for this position and predict callback probability."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"Callback prediction error: {e}")
        return {
            "probability_score": 50,
            "probability_label": "Medium",
            "match_breakdown": {"skills_match": 50, "experience_match": 50, "education_match": 50, "keywords_match": 50},
            "strengths": ["Unable to fully analyze"],
            "gaps": ["Analysis incomplete"],
            "competition_estimate": "Unknown",
            "competition_reasoning": "Could not estimate competition",
            "timing_advice": "Apply as soon as possible for best results",
            "recommendations": ["Try again with more complete job description"],
            "interview_likelihood": "Unknown",
            "key_differentiators": []
        }

# Helper function to generate unique job key for deduplication
def get_job_key(title: str, company: str) -> str:
    """Generate a unique key for a job to track duplicates"""
    key_string = f"{title.lower().strip()}_{company.lower().strip()}"
    return str(abs(hash(key_string)))

# Check if job was already emailed
async def was_job_emailed(job_key: str, email: str) -> bool:
    """Check if this job was already sent to this email"""
    existing = await db.emailed_jobs.find_one({"job_key": job_key, "email": email})
    return existing is not None

# Mark job as emailed
async def mark_job_emailed(job: dict, email: str):
    """Record that this job was emailed to prevent duplicates"""
    job_key = get_job_key(job.get('title', ''), job.get('company', ''))
    doc = {
        "id": str(uuid.uuid4()),
        "job_key": job_key,
        "job_title": job.get('title', ''),
        "company": job.get('company', ''),
        "email": email,
        "emailed_at": datetime.now(timezone.utc).isoformat()
    }
    await db.emailed_jobs.insert_one(doc)

# Filter out already-emailed jobs
async def filter_new_jobs(jobs: List[dict], email: str) -> List[dict]:
    """Filter out jobs that have already been emailed"""
    new_jobs = []
    for job in jobs:
        job_key = get_job_key(job.get('title', ''), job.get('company', ''))
        if not await was_job_emailed(job_key, email):
            new_jobs.append(job)
    return new_jobs

# Generate daily digest email HTML
def generate_digest_email_html(jobs: List[dict], user_name: str, query_summary: str) -> str:
    job_items = ""
    for job in jobs[:15]:
        tags_html = ''.join([f'<span style="background:#E2E8F0;padding:2px 8px;border-radius:12px;font-size:11px;margin-right:4px;">{tag}</span>' for tag in job.get('tags', [])[:3]])
        relevance = job.get('relevance_score', 0)
        relevance_color = '#10B981' if relevance >= 50 else '#0EA5E9' if relevance >= 30 else '#F59E0B'
        
        job_items += f"""
        <div style="border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin-bottom:12px;background:white;">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                <h3 style="margin:0;color:#0F172A;font-size:16px;">{job['title']}</h3>
                <span style="background:{relevance_color};color:white;padding:2px 8px;border-radius:12px;font-size:11px;white-space:nowrap;">
                    {min(relevance, 100)}% match
                </span>
            </div>
            <p style="margin:0 0 8px 0;color:#64748B;font-size:14px;">{job['company']} • {job['location']}</p>
            <p style="margin:0 0 8px 0;color:#94A3B8;font-size:12px;">Source: {job.get('source', 'Unknown')} • Posted: Last 24 hours</p>
            {f'<p style="color:#10B981;font-weight:500;margin:0 0 8px 0;font-size:14px;">{job["salary"]}</p>' if job.get('salary') else ''}
            <div style="margin-bottom:12px;">{tags_html}</div>
            <a href="{job['url']}" style="display:inline-block;background:#0F172A;color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:13px;">View & Apply</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:'Inter',Arial,sans-serif;background:#F8FAFC;padding:20px;margin:0;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
            <div style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);color:white;padding:24px;text-align:center;">
                <h1 style="margin:0;font-size:24px;">📋 Your Daily Job Digest</h1>
                <p style="margin:8px 0 0 0;opacity:0.9;font-size:14px;">Hi {user_name}! Here are today's new job matches</p>
            </div>
            <div style="padding:24px;background:#F8FAFC;">
                <div style="background:linear-gradient(135deg,#0EA5E9 0%,#10B981 100%);color:white;padding:16px;border-radius:8px;margin-bottom:20px;">
                    <p style="margin:0;font-size:14px;">🎯 <strong>{len(jobs)} NEW jobs</strong> posted in the last 24 hours matching:</p>
                    <p style="margin:8px 0 0 0;font-size:13px;opacity:0.9;">{query_summary}</p>
                </div>
                {job_items}
            </div>
            <div style="background:#F1F5F9;padding:16px;text-align:center;color:#64748B;font-size:12px;">
                <p style="margin:0;">You're receiving this daily digest from MedMatch.</p>
                <p style="margin:8px 0 0 0;">Searched: Indeed, LinkedIn, Glassdoor, ZipRecruiter + 5 more sources</p>
            </div>
        </div>
    </body>
    </html>
    """

# AI-powered deep web crawler for comprehensive job discovery
async def ai_deep_crawl(resume_skills: List[str] = []) -> dict:
    """Use AI to generate comprehensive search strategy"""
    if not EMERGENT_LLM_KEY:
        return {"search_queries": QUALITY_SEARCH_TERMS[:10], "related_titles": [], "industries": []}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job search strategist specializing in Quality Assurance, Medical Devices, and Manufacturing roles.
        
        Generate SIMPLE search queries (1-3 words each) that job boards can understand.
        Focus on:
        - Supplier Quality (Manager, Director, Engineer)
        - Medical Device Quality
        - Lead Auditor roles
        - Manufacturing Quality
        - Quality Management Systems
        - Regulatory Compliance (FDA, ISO)
        
        Return a JSON object with:
        - search_queries: array of 15 SIMPLE search terms (1-3 words each, NO boolean operators)
        - related_titles: array of 10 job titles
        - industries: array of 5 target industries
        - keywords: array of 15 single-word keywords
        
        Example search_queries: ["Quality Manager", "Supplier Quality", "Lead Auditor", "Medical Device", "ISO Auditor"]
        
        Return ONLY valid JSON."""
    ).with_model("openai", "gpt-5.2")
    
    skills_text = ', '.join(resume_skills[:20]) if resume_skills else 'Quality Management, ISO 13485, FDA, Supplier Quality'
    user_message = UserMessage(
        text=f"Generate simple job search terms for a professional with these skills:\n{skills_text}\n\nFocus on remote Quality, Medical Device, and Manufacturing roles."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"AI deep crawl error: {e}")
        return {
            "search_queries": QUALITY_SEARCH_TERMS,
            "related_titles": ["Quality Manager", "Quality Director", "Lead Auditor", "Supplier Quality Manager"],
            "industries": ["Medical Devices", "Pharmaceutical", "Manufacturing"],
            "keywords": ["quality", "auditor", "ISO", "FDA", "compliance"]
        }

# Job fetching functions for each source
async def fetch_remoteok_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            headers = {"User-Agent": "MedMatch/1.0"}
            response = await http_client.get("https://remoteok.com/api", headers=headers)
            if response.status_code == 200:
                jobs = response.json()
                jobs = jobs[1:] if len(jobs) > 1 else []
                
                result = []
                for job in jobs[:100]:
                    job_location = job.get('location', 'Remote') or 'Remote'
                    job_title = job.get('position', '').lower()
                    job_desc = job.get('description', '').lower()
                    job_tags = ' '.join(job.get('tags', [])).lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job.get('company', '').lower() or \
                        query.lower() in job_tags or \
                        query.lower() in job_desc
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
                    if matches_query and matches_location:
                        result.append({
                            "id": f"rok_{job.get('id', uuid.uuid4())}",
                            "title": job.get('position', 'Unknown'),
                            "company": job.get('company', 'Unknown'),
                            "location": job_location,
                            "description": job.get('description', ''),
                            "url": job.get('url', ''),
                            "salary": job.get('salary', ''),
                            "tags": job.get('tags', []),
                            "source": "RemoteOK",
                            "posted_at": job.get('date', '')
                        })
                return result
    except Exception as e:
        logging.error(f"RemoteOK API error: {e}")
    return []

async def fetch_remotive_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {}
            if query:
                params["search"] = query
            response = await http_client.get("https://remotive.com/api/remote-jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])[:100]
                
                result = []
                for job in jobs:
                    job_location = job.get('candidate_required_location', 'Worldwide') or 'Worldwide'
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
                    if matches_location:
                        result.append({
                            "id": f"rem_{job.get('id', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('company_name', 'Unknown'),
                            "location": job_location,
                            "description": job.get('description', ''),
                            "url": job.get('url', ''),
                            "salary": job.get('salary', ''),
                            "tags": job.get('tags', []) or [job.get('category', '')],
                            "source": "Remotive",
                            "posted_at": job.get('publication_date', '')
                        })
                return result
    except Exception as e:
        logging.error(f"Remotive API error: {e}")
    return []

async def fetch_jobicy_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {"count": 50, "geo": "anywhere"}
            if query:
                params["tag"] = query.replace(" ", "-").lower()[:20]
            if location and location.lower() not in ['remote', 'worldwide', 'anywhere', 'any']:
                params["geo"] = location.lower()
            
            response = await http_client.get("https://jobicy.com/api/v2/remote-jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                result = []
                for job in jobs:
                    result.append({
                        "id": f"jcy_{job.get('id', uuid.uuid4())}",
                        "title": job.get('jobTitle', 'Unknown'),
                        "company": job.get('companyName', 'Unknown'),
                        "location": job.get('jobGeo', 'Remote'),
                        "description": job.get('jobDescription', ''),
                        "url": job.get('url', ''),
                        "salary": f"{job.get('annualSalaryMin', '')} - {job.get('annualSalaryMax', '')}" if job.get('annualSalaryMin') else '',
                        "tags": [job.get('jobIndustry', '')] if job.get('jobIndustry') else [],
                        "source": "Jobicy",
                        "posted_at": job.get('pubDate', '')
                    })
                return result
    except Exception as e:
        logging.error(f"Jobicy API error: {e}")
    return []

async def fetch_arbeitnow_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.get("https://www.arbeitnow.com/api/job-board-api")
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('data', [])[:100]
                
                result = []
                for job in jobs:
                    job_location = job.get('location', 'Remote')
                    job_title = job.get('title', '').lower()
                    job_desc = job.get('description', '').lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job.get('company_name', '').lower() or \
                        query.lower() in job_desc
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        job.get('remote', False) or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
                    if matches_query and matches_location:
                        result.append({
                            "id": f"arb_{job.get('slug', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('company_name', 'Unknown'),
                            "location": job_location + (" (Remote)" if job.get('remote') else ""),
                            "description": job_desc,
                            "url": job.get('url', ''),
                            "salary": "",
                            "tags": job.get('tags', []),
                            "source": "Arbeitnow",
                            "posted_at": job.get('created_at', '')
                        })
                return result
    except Exception as e:
        logging.error(f"Arbeitnow API error: {e}")
    return []

async def fetch_himalayas_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {"limit": 50}
            response = await http_client.get("https://himalayas.app/jobs/api", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                result = []
                for job in jobs:
                    job_title = job.get('title', '').lower()
                    job_company = job.get('companyName', '').lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job_company
                    
                    if matches_query:
                        result.append({
                            "id": f"him_{job.get('id', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('companyName', 'Unknown'),
                            "location": ', '.join(job.get('locationRestrictions', [])) or 'Worldwide',
                            "description": job.get('description', ''),
                            "url": job.get('applicationLink', '') or f"https://himalayas.app/jobs/{job.get('id')}",
                            "salary": job.get('salaryRange', ''),
                            "tags": job.get('categories', []),
                            "source": "Himalayas",
                            "posted_at": job.get('pubDate', '')
                        })
                return result
    except Exception as e:
        logging.error(f"Himalayas API error: {e}")
    return []

# NEW: Fetch from Adzuna (free tier available)
async def fetch_adzuna_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        # Adzuna has a free API but requires registration - using public feed
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            # Try multiple country endpoints
            countries = ['us', 'gb', 'ca', 'de']
            all_jobs = []
            
            for country in countries[:2]:  # Limit to 2 countries for speed
                try:
                    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
                    params = {
                        "app_id": "public",
                        "app_key": "public",
                        "results_per_page": 20,
                        "what": query or "quality manager",
                        "what_or": "quality auditor supplier",
                        "where": location if location and location.lower() not in ['any', 'remote', 'worldwide'] else ""
                    }
                    response = await http_client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get('results', []):
                            all_jobs.append({
                                "id": f"adz_{job.get('id', uuid.uuid4())}",
                                "title": job.get('title', 'Unknown'),
                                "company": job.get('company', {}).get('display_name', 'Unknown'),
                                "location": job.get('location', {}).get('display_name', 'Remote'),
                                "description": job.get('description', ''),
                                "url": job.get('redirect_url', ''),
                                "salary": f"${job.get('salary_min', '')}-${job.get('salary_max', '')}" if job.get('salary_min') else '',
                                "tags": [job.get('category', {}).get('label', '')],
                                "source": f"Adzuna ({country.upper()})",
                                "posted_at": job.get('created', '')
                            })
                except:
                    continue
            return all_jobs
    except Exception as e:
        logging.error(f"Adzuna API error: {e}")
    return []

# NEW: Fetch from JSearch (RapidAPI free tier)
async def fetch_jsearch_jobs(query: str = "", location: str = "") -> List[dict]:
    # Placeholder - would integrate with proper API key
    return []

# GOOGLE CUSTOM SEARCH API - Search job boards directly via Google
async def fetch_google_cse_jobs(query: str, location: str = "Remote", site: str = "indeed.com", num_results: int = 10) -> List[dict]:
    """
    Fetch jobs from any job board using Google Custom Search API
    Based on the Google Sheets script approach for searching Indeed
    """
    if not GOOGLE_API_KEY:
        logging.warning("Google API Key not configured")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as http_client:
            # Build optimized search query for job postings
            # Format: "job title" "location" site:jobboard.com
            search_query = f'"{query}" "{location}" job site:{site}'
            
            params = {
                "q": search_query,
                "key": GOOGLE_API_KEY,
                "num": min(num_results, 10),
            }
            
            # Only add CSE ID if configured - otherwise Google will require one
            # For this to work without CSE, user needs Programmable Search Engine
            if GOOGLE_CSE_ID:
                params["cx"] = GOOGLE_CSE_ID
            else:
                # Cannot use Custom Search API without CSE ID
                logging.warning("Google CSE ID not configured - skipping Google search")
                return []
            
            response = await http_client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                logging.info(f"Google CSE returned {len(items)} results for '{query}' on {site}")
                
                result = []
                for item in items:
                    job_url = item.get("link", "")
                    title = item.get("title", "Unknown")
                    snippet = item.get("snippet", "")
                    
                    # Extract company from snippet (pattern: "at Company -" or "Company -")
                    company = "Unknown"
                    company_match = re.search(r'(?:at\s+)?([\w\s&.,-]+?)(?:\s*[-–|•]|\s+is\s+)', snippet)
                    if company_match:
                        company = company_match.group(1).strip()[:50]
                    
                    # Try to extract company from title if not found
                    if company == "Unknown" and " at " in title:
                        company = title.split(" at ")[-1].split(" - ")[0].split(" | ")[0][:50]
                    
                    # Extract salary from snippet
                    salary = ""
                    salary_match = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:a\s*year|per\s*year|annually|/yr|K))?', snippet, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group(0)
                    
                    # Determine source from URL
                    source = "Google Search"
                    if "indeed.com" in job_url:
                        source = "Indeed (Google)"
                    elif "linkedin.com" in job_url:
                        source = "LinkedIn (Google)"
                    elif "glassdoor.com" in job_url:
                        source = "Glassdoor (Google)"
                    elif "ziprecruiter.com" in job_url:
                        source = "ZipRecruiter (Google)"
                    elif "monster.com" in job_url:
                        source = "Monster (Google)"
                    elif "dice.com" in job_url:
                        source = "Dice (Google)"
                    elif "careerbuilder.com" in job_url:
                        source = "CareerBuilder (Google)"
                    
                    result.append({
                        "id": f"gcse_{abs(hash(job_url))}",
                        "title": title.replace(" | Indeed.com", "").replace(" - LinkedIn", "").replace(" | Glassdoor", "").strip(),
                        "company": company,
                        "location": location,
                        "description": snippet,
                        "url": job_url,
                        "salary": salary,
                        "tags": [],
                        "source": source,
                        "posted_at": ""
                    })
                
                return result
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                logging.error(f"Google CSE API error: {response.status_code} - {error_data.get('error', {}).get('message', response.text[:200])}")
                return []
                
    except Exception as e:
        logging.error(f"Google CSE error: {e}")
        return []

# Fetch jobs from multiple job sites via Google CSE
async def fetch_google_cse_all_sites(query: str, location: str = "Remote") -> List[dict]:
    """Search multiple job boards simultaneously using Google Custom Search"""
    all_jobs = []
    
    # Search Indeed, LinkedIn, Glassdoor, ZipRecruiter via Google
    sites_to_search = [
        "indeed.com",
        "linkedin.com/jobs",
        "glassdoor.com",
        "ziprecruiter.com"
    ]
    
    tasks = [
        fetch_google_cse_jobs(query, location, site, 10)
        for site in sites_to_search
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
    
    return all_jobs

# JOBSPY INTEGRATION - Scrape from LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
def fetch_jobspy_jobs_sync(query: str, location: str = "USA", sites: List[str] = None, results_wanted: int = 25, hours_old: int = 72) -> List[dict]:
    """Synchronous JobSpy scraper - runs in thread pool"""
    if not JOBSPY_AVAILABLE:
        return []
    
    if sites is None:
        sites = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter"]
    
    try:
        # Use optimized search term for Quality/Medical Device roles
        search_term = query or "quality manager"
        
        # Google needs special search term format
        google_search_term = f"{search_term} jobs remote" if "google" in sites else None
        
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location if location and location.lower() not in ['any', 'worldwide'] else "USA",
            results_wanted=results_wanted,
            hours_old=hours_old,
            is_remote=True,
            country_indeed='USA',
            verbose=0
        )
        
        if jobs_df is None or jobs_df.empty:
            return []
        
        result = []
        for _, row in jobs_df.iterrows():
            try:
                # Build salary string - handle NaN values safely
                salary = ""
                min_amt = row.get('min_amount')
                max_amt = row.get('max_amount')
                
                # Check for NaN using pandas-safe comparison
                import math
                min_valid = min_amt is not None and not (isinstance(min_amt, float) and math.isnan(min_amt))
                max_valid = max_amt is not None and not (isinstance(max_amt, float) and math.isnan(max_amt))
                
                if min_valid and max_valid:
                    interval = row.get('interval', 'yearly')
                    salary = f"${int(min_amt):,} - ${int(max_amt):,}/{interval}"
                elif min_valid:
                    salary = f"${int(min_amt):,}+"
                
                # Build location string
                loc_parts = []
                city = row.get('city')
                state = row.get('state')
                if city and str(city) not in ['nan', 'None', '']:
                    loc_parts.append(str(city))
                if state and str(state) not in ['nan', 'None', '']:
                    loc_parts.append(str(state))
                if row.get('is_remote'):
                    loc_parts.append("Remote")
                location_str = ", ".join(loc_parts) if loc_parts else "Remote"
                
                job = {
                    "id": f"jspy_{row.get('site', 'unknown')}_{hash(str(row.get('job_url', '')))}",
                    "title": str(row.get('title', 'Unknown')),
                    "company": str(row.get('company', 'Unknown')),
                    "location": location_str,
                    "description": str(row.get('description', ''))[:5000],
                    "url": str(row.get('job_url', '')),
                    "salary": salary,
                    "tags": [str(row.get('job_type', ''))] if row.get('job_type') else [],
                    "source": f"JobSpy ({str(row.get('site', 'Unknown')).title()})",
                    "posted_at": str(row.get('date_posted', '')) if row.get('date_posted') else ''
                }
                result.append(job)
            except Exception as row_err:
                logging.warning(f"JobSpy row parse error: {row_err}")
                continue
        
        return result
    except Exception as e:
        logging.error(f"JobSpy error: {e}")
        return []

async def fetch_jobspy_jobs(query: str, location: str = "USA", sites: List[str] = None, results_wanted: int = 25) -> List[dict]:
    """Async wrapper for JobSpy - runs in thread pool to avoid blocking with timeout"""
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Add 30 second timeout to prevent hanging
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    executor,
                    fetch_jobspy_jobs_sync,
                    query,
                    location,
                    sites,
                    results_wanted,
                    72  # hours_old
                ),
                timeout=30.0
            )
        return result
    except asyncio.TimeoutError:
        logging.warning(f"JobSpy search timed out for query: {query}")
        return []
    except Exception as e:
        logging.error(f"JobSpy async error: {e}")
        return []

# Placeholder functions for removed APIs
async def fetch_linkedin_jobs(query: str = "", location: str = "") -> List[dict]:
    # Now handled by JobSpy
    return []

async def fetch_indeed_jobs(query: str = "", location: str = "") -> List[dict]:
    # Now handled by JobSpy
    return []

async def fetch_freejobs_api(query: str = "", location: str = "") -> List[dict]:
    return []

def filter_jobs_by_date(jobs: List[dict], days: int) -> List[dict]:
    if days <= 0:
        return jobs
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []
    
    for job in jobs:
        posted_at = job.get('posted_at', '')
        if not posted_at:
            filtered.append(job)
            continue
        
        try:
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    job_date = datetime.strptime(posted_at[:19], fmt[:len(posted_at)])
                    if job_date.tzinfo is None:
                        job_date = job_date.replace(tzinfo=timezone.utc)
                    if job_date >= cutoff_date:
                        filtered.append(job)
                    break
                except:
                    continue
            else:
                filtered.append(job)
        except:
            filtered.append(job)
    
    return filtered

def filter_jobs_by_relevance(jobs: List[dict], keywords: List[str]) -> List[dict]:
    """Filter and score jobs by relevance to quality/medical device keywords"""
    relevance_keywords = [
        'quality', 'supplier', 'auditor', 'audit', 'iso', 'fda', 'medical device',
        'manufacturing', 'compliance', 'regulatory', 'qms', 'capa', 'ncr',
        'validation', 'verification', 'inspection', '13485', 'gmp', 'cgmp',
        'pharmaceutical', 'healthcare', 'biotech', 'med tech', 'qa', 'qc',
        'director', 'manager', 'engineer', 'lead', 'senior', 'principal'
    ]
    relevance_keywords.extend([k.lower() for k in keywords if k])
    
    scored_jobs = []
    for job in jobs:
        score = 0
        title_lower = job.get('title', '').lower()
        desc_lower = job.get('description', '').lower()
        tags_lower = ' '.join(job.get('tags', [])).lower()
        
        for keyword in relevance_keywords:
            if keyword in title_lower:
                score += 10
            if keyword in desc_lower:
                score += 2
            if keyword in tags_lower:
                score += 5
        
        job['relevance_score'] = min(score, 100)
        scored_jobs.append(job)
    
    # Sort by relevance score (highest first)
    scored_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return scored_jobs

def generate_job_alert_html(jobs: List[dict], keywords: List[str]) -> str:
    job_items = ""
    for job in jobs[:15]:
        tags_html = ''.join([f'<span style="background:#E2E8F0;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:4px;">{tag}</span>' for tag in job.get('tags', [])[:3]])
        relevance = job.get('relevance_score', 0)
        relevance_badge = f'<span style="background:#10B981;color:white;padding:2px 8px;border-radius:12px;font-size:11px;">Match: {min(relevance, 100)}%</span>' if relevance else ''
        
        job_items += f"""
        <div style="border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:start;">
                <h3 style="margin:0 0 8px 0;color:#0F172A;">{job['title']}</h3>
                {relevance_badge}
            </div>
            <p style="margin:0 0 8px 0;color:#64748B;">{job['company']} • {job['location']}</p>
            <p style="margin:0 0 8px 0;color:#94A3B8;font-size:12px;">Source: {job.get('source', 'Unknown')}</p>
            {f'<p style="color:#10B981;font-weight:500;margin:0 0 8px 0;">{job["salary"]}</p>' if job.get('salary') else ''}
            <div style="margin-bottom:12px;">{tags_html}</div>
            <a href="{job['url']}" style="display:inline-block;background:#0F172A;color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:14px;">View Job</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:'Inter',Arial,sans-serif;background:#F8FAFC;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;">
            <div style="background:#0F172A;color:white;padding:24px;text-align:center;">
                <h1 style="margin:0;font-size:24px;">MedMatch Job Alert</h1>
                <p style="margin:8px 0 0 0;opacity:0.8;">AI-Powered Search: {', '.join(keywords[:3])}</p>
            </div>
            <div style="padding:24px;">
                <p style="color:#64748B;margin-bottom:20px;">We found <strong>{len(jobs)}</strong> jobs matching your Quality/Medical Device profile!</p>
                {job_items}
                <p style="color:#94A3B8;font-size:12px;margin-top:20px;text-align:center;">
                    Searched across: RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas, and more
                </p>
            </div>
            <div style="background:#F1F5F9;padding:16px;text-align:center;color:#64748B;font-size:12px;">
                <p>You're receiving this because you set up job alerts on MedMatch.</p>
            </div>
        </div>
    </body>
    </html>
    """

# Routes
@api_router.get("/")
async def root():
    return {"message": "MedMatch API - Remote Job Finder with AI Crawler"}

@api_router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    raw_text = extract_text_from_pdf(content)
    parsed_data = await parse_resume_with_ai(raw_text)
    
    resume = ResumeData(
        full_name=parsed_data.get('full_name', ''),
        email=parsed_data.get('email', ''),
        phone=parsed_data.get('phone', ''),
        skills=parsed_data.get('skills', []),
        experience=parsed_data.get('experience', []),
        education=parsed_data.get('education', []),
        summary=parsed_data.get('summary', ''),
        raw_text=raw_text
    )
    
    doc = resume.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.resumes.delete_many({})
    await db.resumes.insert_one(doc)
    
    return resume

@api_router.get("/resume")
async def get_resume():
    doc = await db.resumes.find_one({}, {"_id": 0})
    if not doc:
        return None
    if isinstance(doc.get('created_at'), str):
        doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    if isinstance(doc.get('updated_at'), str):
        doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
    return doc

@api_router.put("/resume/skills")
async def update_skills(data: SkillsUpdate):
    result = await db.resumes.update_one(
        {},
        {"$set": {"skills": data.skills, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"message": "Skills updated"}

# Enhanced job search with multiple sources including JobSpy
@api_router.get("/jobs/search")
async def search_jobs(
    query: str = "",
    source: str = "all",
    location: str = "",
    days: int = 0
):
    jobs = []
    tasks = []
    
    # Free API sources
    if source in ["all", "remoteok"]:
        tasks.append(fetch_remoteok_jobs(query, location))
    if source in ["all", "remotive"]:
        tasks.append(fetch_remotive_jobs(query, location))
    if source in ["all", "jobicy"]:
        tasks.append(fetch_jobicy_jobs(query, location))
    if source in ["all", "arbeitnow"]:
        tasks.append(fetch_arbeitnow_jobs(query, location))
    if source in ["all", "himalayas"]:
        tasks.append(fetch_himalayas_jobs(query, location))
    
    # Google CSE sources
    if source in ["all", "google"] and GOOGLE_API_KEY and query:
        tasks.append(fetch_google_cse_all_sites(query, location or "Remote"))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            jobs.extend(result)
    
    if days > 0:
        jobs = filter_jobs_by_date(jobs, days)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs

# Google CSE Direct Search endpoint - search specific job boards via Google
@api_router.get("/jobs/google-search")
async def google_search_jobs(
    query: str = "Quality Manager",
    location: str = "Remote",
    site: str = "indeed.com/viewjob"
):
    """
    Direct Google Custom Search for job boards.
    Supports: indeed.com, linkedin.com, glassdoor.com, ziprecruiter.com, monster.com, dice.com
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="Google API Key not configured")
    
    jobs = await fetch_google_cse_jobs(query, location, site, 10)
    return {
        "jobs": jobs,
        "query": query,
        "location": location,
        "site": site,
        "total": len(jobs)
    }

# Deep AI-powered search across ALL sources including JobSpy (LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter)
@api_router.post("/jobs/deep-search")
async def deep_search_jobs(request: DeepSearchRequest):
    """AI-powered comprehensive search across ALL job sources including LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter + Google CSE"""
    try:
        resume_doc = await db.resumes.find_one({}, {"_id": 0})
        skills = resume_doc.get('skills', []) if resume_doc else []
        
        # Get AI-generated search strategy with timeout
        search_strategy = {}
        if request.use_ai:
            try:
                search_strategy = await asyncio.wait_for(
                    ai_deep_crawl(skills),
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                logging.warning("AI strategy generation timed out, using defaults")
                search_strategy = {}
        
        search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:10]
        
        all_jobs = []
        sources_searched = []
        errors = []
        
        # 1. Use Google Custom Search API to search Indeed, LinkedIn, Glassdoor directly
        if GOOGLE_API_KEY:
            logging.info("Starting Google CSE job search...")
            for query in search_queries[:3]:
                try:
                    google_results = await asyncio.wait_for(
                        fetch_google_cse_all_sites(query, "Remote"),
                        timeout=10.0
                    )
                    all_jobs.extend(google_results)
                    if google_results:
                        sources_searched.extend(["Indeed (Google)", "LinkedIn (Google)", "Glassdoor (Google)"])
                except asyncio.TimeoutError:
                    errors.append(f"Google CSE timeout for '{query}'")
                except Exception as e:
                    logging.error(f"Google CSE error for '{query}': {e}")
                    errors.append(f"Google CSE error: {str(e)[:50]}")
        
        # 2. Use JobSpy to scrape from major job boards (LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter)
        if JOBSPY_AVAILABLE:
            logging.info("Starting JobSpy deep search...")
            for query in search_queries[:2]:  # Reduced to 2 queries for speed
                try:
                    jobspy_results = await fetch_jobspy_jobs(
                        query=query,
                        location="USA",
                        sites=["indeed", "linkedin"],  # Reduced sites - glassdoor/zip often blocked
                        results_wanted=10
                    )
                    all_jobs.extend(jobspy_results)
                    if jobspy_results:
                        sources_searched.extend(["LinkedIn (JobSpy)", "Indeed (JobSpy)"])
                except Exception as e:
                    logging.error(f"JobSpy search error for '{query}': {e}")
                    errors.append(f"JobSpy error: {str(e)[:50]}")
        
        # 3. Search free API sources in parallel with timeout
        for query in search_queries[:4]:  # Reduced from 6 to 4
            tasks = [
                fetch_remoteok_jobs(query, ""),
                fetch_remotive_jobs(query, ""),
                fetch_jobicy_jobs(query, ""),
                fetch_arbeitnow_jobs(query, ""),
                fetch_himalayas_jobs(query, ""),
            ]
            
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=20.0
                )
                
                for result in results:
                    if isinstance(result, list):
                        all_jobs.extend(result)
            except asyncio.TimeoutError:
                logging.warning(f"Free API search timeout for query: {query}")
                errors.append("Some job sources timed out")
        
        sources_searched.extend(["RemoteOK", "Remotive", "Jobicy", "Arbeitnow", "Himalayas"])
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job['title'].lower()}_{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Filter and score by relevance
        keywords = search_strategy.get('keywords', ['quality', 'auditor', 'medical', 'supplier'])
        relevant_jobs = filter_jobs_by_relevance(unique_jobs, keywords)
        
        return {
            "jobs": relevant_jobs[:300],
            "total_found": len(relevant_jobs),
            "search_strategy": search_strategy,
            "queries_used": search_queries[:4],
            "sources_searched": list(set(sources_searched)),
            "jobspy_enabled": JOBSPY_AVAILABLE,
            "google_cse_enabled": bool(GOOGLE_API_KEY),
            "errors": errors[:5] if errors else None  # Return first 5 errors if any
        }
    except Exception as e:
        logging.error(f"Deep search error: {e}")
        raise HTTPException(status_code=500, detail=f"Deep search failed: {str(e)}")

# Quick search presets - TheirStack inspired with technology and industry filters
@api_router.get("/jobs/presets")
async def get_search_presets():
    return {
        "presets": [
            {"id": "supplier-quality-manager", "name": "Supplier Quality Manager", "query": "Supplier Quality Manager", "icon": "shield-check"},
            {"id": "supplier-quality-director", "name": "Supplier Quality Director", "query": "Supplier Quality Director", "icon": "award"},
            {"id": "quality-manager", "name": "Quality Manager", "query": "Quality Manager", "icon": "check-circle"},
            {"id": "quality-director", "name": "Quality Director", "query": "Quality Director", "icon": "award"},
            {"id": "lead-auditor", "name": "Lead Auditor", "query": "Lead Auditor", "icon": "search"},
            {"id": "medical-device", "name": "Medical Device", "query": "Medical Device Quality", "icon": "heart-pulse"},
            {"id": "manufacturing-quality", "name": "Manufacturing Quality", "query": "Manufacturing Quality", "icon": "settings"},
            {"id": "regulatory-compliance", "name": "Regulatory Compliance", "query": "Regulatory Compliance", "icon": "file-text"},
            {"id": "iso-auditor", "name": "ISO Auditor", "query": "ISO Auditor", "icon": "check-circle"},
            {"id": "fda-compliance", "name": "FDA Compliance", "query": "FDA Compliance", "icon": "shield-check"},
        ],
        "locations": [
            "Worldwide", "USA", "Europe", "UK", "Canada", "Germany", "Remote"
        ],
        "industries": [
            "Medical Devices", "Pharmaceutical", "Healthcare", "Biotechnology", 
            "Manufacturing", "Automotive", "Aerospace", "Electronics", "Consumer Goods"
        ],
        "technologies": [
            "ISO 13485", "ISO 9001", "FDA 21 CFR 820", "EU MDR", "GMP", "CGMP",
            "Six Sigma", "Lean Manufacturing", "SAP", "Oracle", "Minitab",
            "Quality Management Systems", "ERP", "MES"
        ],
        "salary_ranges": [
            {"label": "Any", "min": 0, "max": 0},
            {"label": "$50k-$80k", "min": 50000, "max": 80000},
            {"label": "$80k-$120k", "min": 80000, "max": 120000},
            {"label": "$120k-$150k", "min": 120000, "max": 150000},
            {"label": "$150k+", "min": 150000, "max": 500000}
        ],
        "quality_terms": QUALITY_SEARCH_TERMS
    }

@api_router.post("/jobs/analyze")
async def analyze_job(request: JobAnalyzeRequest):
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        raise HTTPException(status_code=404, detail="Please upload your resume first")
    
    job_data = {
        "title": request.job_title,
        "company": request.company,
        "description": request.job_description
    }
    
    result = await analyze_job_match(resume_doc, job_data)
    return result

# Saved jobs
@api_router.post("/jobs/save")
async def save_job(job: Job):
    saved = SavedJob(job=job)
    doc = saved.model_dump()
    doc['saved_at'] = doc['saved_at'].isoformat()
    
    existing = await db.saved_jobs.find_one({"job.id": job.id})
    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")
    
    await db.saved_jobs.insert_one(doc)
    return saved

@api_router.get("/jobs/saved")
async def get_saved_jobs():
    docs = await db.saved_jobs.find({}, {"_id": 0}).to_list(100)
    for doc in docs:
        if isinstance(doc.get('saved_at'), str):
            doc['saved_at'] = datetime.fromisoformat(doc['saved_at'])
    return docs

@api_router.delete("/jobs/saved/{job_id}")
async def remove_saved_job(job_id: str):
    result = await db.saved_jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved job not found")
    return {"message": "Job removed from saved"}

# Applications
@api_router.post("/applications")
async def create_application(data: ApplicationCreate):
    """Create application and auto-mark as applied"""
    # Check if already applied to this job (by URL)
    if data.job.url:
        existing = await db.applications.find_one({"job.url": data.job.url}, {"_id": 0})
        if existing:
            return {"message": "Already applied to this job", "application": existing, "already_applied": True}
    
    app_doc = Application(
        job=data.job, 
        notes=data.notes,
        external_url=data.job.url,
        job_status="Active"
    )
    doc = app_doc.model_dump()
    doc['applied_at'] = doc['applied_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.applications.insert_one(doc)
    return {"application": app_doc, "already_applied": False}

@api_router.post("/applications/quick-apply")
async def quick_apply_job(data: ApplicationCreate):
    """Quick apply - mark job as applied and return the external URL to redirect user"""
    # Check if already applied
    if data.job.url:
        existing = await db.applications.find_one({"job.url": data.job.url}, {"_id": 0})
        if existing:
            return {
                "redirect_url": data.job.url,
                "message": "Already applied - redirecting to job posting",
                "already_applied": True,
                "application_id": existing.get("id")
            }
    
    # Create application
    app_doc = Application(
        job=data.job,
        notes="Quick applied via MedMatch",
        external_url=data.job.url,
        job_status="Active",
        status="Applied"
    )
    doc = app_doc.model_dump()
    doc['applied_at'] = doc['applied_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.applications.insert_one(doc)
    
    return {
        "redirect_url": data.job.url,
        "message": "Application recorded - redirecting to job posting",
        "already_applied": False,
        "application_id": app_doc.id
    }

@api_router.get("/applications")
async def get_applications():
    docs = await db.applications.find({}, {"_id": 0}).to_list(100)
    for doc in docs:
        if isinstance(doc.get('applied_at'), str):
            doc['applied_at'] = datetime.fromisoformat(doc['applied_at'])
        if isinstance(doc.get('updated_at'), str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
    return docs

@api_router.get("/applications/check/{job_url:path}")
async def check_if_applied(job_url: str):
    """Check if user has already applied to a job by URL"""
    # URL decode
    import urllib.parse
    decoded_url = urllib.parse.unquote(job_url)
    
    existing = await db.applications.find_one({"job.url": decoded_url}, {"_id": 0})
    if existing:
        return {"applied": True, "application": existing}
    return {"applied": False}

@api_router.put("/applications/{app_id}")
async def update_application(app_id: str, data: ApplicationStatusUpdate):
    update_data = {"status": data.status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if data.notes is not None:
        update_data["notes"] = data.notes
    
    result = await db.applications.update_one({"id": app_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application updated"}

@api_router.put("/applications/{app_id}/job-status")
async def update_job_status(app_id: str, job_status: str):
    """Update the job posting status (Active, Closed, Filled)"""
    valid_statuses = ["Active", "Closed", "Filled", "Unknown", "Still Accepting"]
    if job_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    update_data = {"job_status": job_status, "updated_at": datetime.now(timezone.utc).isoformat()}
    result = await db.applications.update_one({"id": app_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Job status updated"}

@api_router.post("/jobs/verify-status")
async def verify_job_status(data: dict):
    """Verify if a job posting is still available by checking the URL"""
    job_url = data.get("url", "")
    if not job_url:
        return {"status": "Unknown", "reason": "No URL provided"}
    
    # Keywords that indicate a job is closed
    closed_indicators = [
        "job has been filled",
        "position has been filled",
        "no longer accepting",
        "this job is closed",
        "job is no longer available",
        "expired",
        "this position has been filled",
        "job posting has expired",
        "application closed",
        "we are no longer accepting applications",
        "this role has been filled",
        "position is no longer open",
        "job removed",
        "listing has expired",
        "this job has been removed"
    ]
    
    # Keywords that indicate job is still active
    active_indicators = [
        "apply now",
        "submit application",
        "apply for this job",
        "easy apply",
        "apply on company site"
    ]
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(job_url, headers=headers)
            
            # Check for 404 or other error status codes
            if response.status_code == 404:
                return {"status": "Closed", "reason": "Page not found (404)"}
            if response.status_code >= 400:
                return {"status": "Unknown", "reason": f"HTTP error: {response.status_code}"}
            
            # Check page content for indicators
            content_lower = response.text.lower()
            
            # Check for closed indicators
            for indicator in closed_indicators:
                if indicator in content_lower:
                    return {"status": "Closed", "reason": f"Found: '{indicator}'"}
            
            # Check for active indicators
            for indicator in active_indicators:
                if indicator in content_lower:
                    return {"status": "Active", "reason": f"Found: '{indicator}'"}
            
            # If page loads but no clear indicators, assume active
            return {"status": "Active", "reason": "Page accessible, no closed indicators found"}
            
    except httpx.TimeoutException:
        return {"status": "Unknown", "reason": "Request timed out"}
    except httpx.ConnectError:
        return {"status": "Unknown", "reason": "Could not connect to server"}
    except Exception as e:
        logging.error(f"Error verifying job status: {e}")
        return {"status": "Unknown", "reason": str(e)}

@api_router.delete("/applications/{app_id}")
async def delete_application(app_id: str):
    result = await db.applications.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}

# Job Alerts
@api_router.post("/alerts")
async def create_job_alert(data: JobAlertCreate):
    alert = JobAlert(keywords=data.keywords, locations=data.locations, email=data.email)
    doc = alert.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.job_alerts.insert_one(doc)
    return alert

@api_router.get("/alerts")
async def get_job_alerts():
    return await db.job_alerts.find({}, {"_id": 0}).to_list(100)

@api_router.delete("/alerts/{alert_id}")
async def delete_job_alert(alert_id: str):
    result = await db.job_alerts.delete_one({"id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}

@api_router.post("/alerts/send-now")
async def send_job_alert_now(background_tasks: BackgroundTasks, data: EmailAlertRequest):
    """Send comprehensive job alert email with AI-powered search"""
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Use AI to generate search strategy
    search_strategy = await ai_deep_crawl(skills)
    search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:10]
    
    all_jobs = []
    
    # Search with multiple queries
    for query in search_queries[:6]:
        tasks = [
            fetch_remoteok_jobs(query, ""),
            fetch_remotive_jobs(query, ""),
            fetch_jobicy_jobs(query, ""),
            fetch_arbeitnow_jobs(query, ""),
            fetch_himalayas_jobs(query, ""),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    # Deduplicate and filter
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Score by relevance
    keywords = search_strategy.get('keywords', ['quality', 'auditor', 'medical', 'supplier'])
    relevant_jobs = filter_jobs_by_relevance(unique_jobs, keywords)
    
    if not relevant_jobs:
        return {"message": "No matching jobs found", "jobs_count": 0}
    
    # Generate and send email
    html_content = generate_job_alert_html(relevant_jobs[:15], search_queries[:5])
    
    def send_email_task():
        send_email_gmail(
            data.email,
            f"MedMatch: {len(relevant_jobs)} Quality/Medical Device Jobs Found",
            html_content
        )
    
    background_tasks.add_task(send_email_task)
    
    return {
        "message": f"Job alert sent to {data.email}",
        "jobs_count": len(relevant_jobs),
        "queries_used": search_queries[:6]
    }

# ============== DAILY DIGEST ENDPOINTS ==============

@api_router.post("/digest/settings")
async def create_digest_settings(data: DigestSettingsCreate):
    """Create or update digest settings for a user"""
    # Check if settings already exist for this email
    existing = await db.digest_settings.find_one({"email": data.email})
    
    if existing:
        # Update existing settings
        await db.digest_settings.update_one(
            {"email": data.email},
            {"$set": {
                "frequency": data.frequency,
                "search_queries": data.search_queries if data.search_queries else QUALITY_SEARCH_TERMS[:5],
                "locations": data.locations,
                "is_active": True
            }}
        )
        return {"message": "Digest settings updated", "email": data.email}
    
    # Create new settings
    settings = DigestSettings(
        email=data.email,
        frequency=data.frequency,
        search_queries=data.search_queries if data.search_queries else QUALITY_SEARCH_TERMS[:5],
        locations=data.locations
    )
    doc = settings.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.digest_settings.insert_one(doc)
    
    return {"message": "Digest settings created", "email": data.email, "frequency": data.frequency}

@api_router.get("/digest/settings")
async def get_digest_settings():
    """Get all digest settings"""
    docs = await db.digest_settings.find({}, {"_id": 0}).to_list(100)
    return docs

@api_router.delete("/digest/settings/{email}")
async def delete_digest_settings(email: str):
    """Disable digest for an email"""
    result = await db.digest_settings.update_one(
        {"email": email},
        {"$set": {"is_active": False}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Digest settings not found")
    return {"message": "Digest disabled"}

@api_router.post("/digest/send-daily")
async def send_daily_digest(background_tasks: BackgroundTasks, data: EmailAlertRequest):
    """
    Send daily digest with jobs posted in the last 24 hours.
    Eliminates duplicate emails for the same jobs.
    """
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    user_name = resume_doc.get('full_name', 'Job Seeker').split()[0] if resume_doc else 'Job Seeker'
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Get search queries from AI or defaults
    search_strategy = await ai_deep_crawl(skills)
    search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:8]
    
    all_jobs = []
    
    # 1. Search Google CSE for major job boards
    if GOOGLE_API_KEY:
        for query in search_queries[:3]:
            try:
                google_results = await fetch_google_cse_all_sites(query, "Remote")
                all_jobs.extend(google_results)
            except Exception as e:
                logging.error(f"Digest Google CSE error: {e}")
    
    # 2. Search free APIs
    for query in search_queries[:5]:
        tasks = [
            fetch_remoteok_jobs(query, ""),
            fetch_remotive_jobs(query, ""),
            fetch_jobicy_jobs(query, ""),
            fetch_arbeitnow_jobs(query, ""),
            fetch_himalayas_jobs(query, ""),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    # Filter to jobs posted in last 24 hours
    jobs_24h = filter_jobs_by_date(all_jobs, days=1)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in jobs_24h:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Filter out jobs already emailed to this user
    new_jobs = await filter_new_jobs(unique_jobs, data.email)
    
    if not new_jobs:
        return {
            "message": "No new jobs in the last 24 hours (or all have been sent before)",
            "jobs_count": 0,
            "total_found": len(unique_jobs),
            "already_sent": len(unique_jobs) - len(new_jobs)
        }
    
    # Score by relevance
    keywords = search_strategy.get('keywords', ['quality', 'auditor', 'medical', 'supplier'])
    relevant_jobs = filter_jobs_by_relevance(new_jobs, keywords)[:15]
    
    # Generate and send email
    query_summary = ", ".join(search_queries[:4])
    html_content = generate_digest_email_html(relevant_jobs, user_name, query_summary)
    
    def send_digest_task():
        success = send_email_gmail(
            data.email,
            f"📋 MedMatch Daily Digest: {len(relevant_jobs)} New Jobs Today",
            html_content
        )
        if success:
            # Mark all jobs as emailed (run in sync context)
            import asyncio
            loop = asyncio.new_event_loop()
            for job in relevant_jobs:
                loop.run_until_complete(mark_job_emailed(job, data.email))
            loop.close()
    
    background_tasks.add_task(send_digest_task)
    
    # Update last_sent timestamp
    await db.digest_settings.update_one(
        {"email": data.email},
        {"$set": {"last_sent": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": f"Daily digest sent to {data.email}",
        "jobs_count": len(relevant_jobs),
        "jobs_last_24h": len(jobs_24h),
        "new_jobs": len(new_jobs),
        "queries_used": search_queries[:5]
    }

@api_router.get("/digest/history")
async def get_emailed_jobs_history(email: str):
    """Get history of jobs emailed to a user"""
    docs = await db.emailed_jobs.find({"email": email}, {"_id": 0}).sort("emailed_at", -1).to_list(100)
    return {"email": email, "jobs_sent": len(docs), "history": docs}

@api_router.delete("/digest/history/{email}")
async def clear_emailed_history(email: str):
    """Clear emailed jobs history to allow re-sending"""
    result = await db.emailed_jobs.delete_many({"email": email})
    return {"message": f"Cleared {result.deleted_count} emailed job records for {email}"}

@api_router.get("/digest/scheduler-status")
async def get_scheduler_status():
    """Get the status of the daily digest scheduler"""
    jobs = scheduler.get_jobs()
    job_info = []
    for job in jobs:
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run,
            "trigger": str(job.trigger)
        })
    
    return {
        "scheduler_running": scheduler.running,
        "scheduled_jobs": job_info,
        "timezone": "UTC",
        "digest_time": "8:00 AM UTC daily"
    }

@api_router.post("/digest/trigger-now")
async def trigger_digest_now(background_tasks: BackgroundTasks):
    """Manually trigger the scheduled digest (for testing)"""
    background_tasks.add_task(scheduled_digest_task)
    return {"message": "Digest triggered - running in background", "note": "Check logs for progress"}

@api_router.post("/digest/run-scheduled")
async def run_scheduled_digest(background_tasks: BackgroundTasks):
    """
    Run scheduled digest for all active subscribers.
    This endpoint is called by the cron job to send daily digests.
    """
    # Get all active digest subscribers
    subscribers = await db.digest_settings.find({"is_active": True}, {"_id": 0}).to_list(100)
    
    if not subscribers:
        return {"message": "No active subscribers", "sent_count": 0}
    
    # Get resume for context
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    user_name = resume_doc.get('full_name', 'Job Seeker').split()[0] if resume_doc else 'Job Seeker'
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Get search queries
    search_strategy = await ai_deep_crawl(skills) if skills else {"search_queries": QUALITY_SEARCH_TERMS}
    search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:8]
    
    # Fetch jobs once for all subscribers
    all_jobs = []
    
    # 1. Search Google CSE
    if GOOGLE_API_KEY:
        for query in search_queries[:4]:
            try:
                google_jobs = await fetch_google_cse_all_sites(query, "Remote")
                all_jobs.extend(google_jobs)
            except Exception as e:
                logging.error(f"Google CSE error: {e}")
    
    # 2. Search free APIs
    try:
        api_results = await asyncio.gather(
            fetch_remoteok_jobs("quality", ""),
            fetch_remotive_jobs("quality", ""),
            fetch_jobicy_jobs("quality", ""),
            fetch_arbeitnow_jobs("quality", ""),
            fetch_himalayas_jobs("quality", ""),
            return_exceptions=True
        )
        for result in api_results:
            if isinstance(result, list):
                all_jobs.extend(result)
    except Exception as e:
        logging.error(f"API fetch error: {e}")
    
    # Filter to last 24 hours only
    recent_jobs = filter_jobs_by_date(all_jobs, days=1)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in recent_jobs:
        key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    sent_count = 0
    results = []
    
    # Send digest to each subscriber
    for subscriber in subscribers:
        email = subscriber.get('email')
        if not email:
            continue
        
        # Filter out already-emailed jobs for this subscriber
        new_jobs = await filter_new_jobs(unique_jobs, email)
        
        if not new_jobs:
            results.append({"email": email, "status": "skipped", "reason": "No new jobs"})
            continue
        
        # AI ranking
        relevant_jobs = new_jobs[:20]
        if skills and EMERGENT_LLM_KEY:
            try:
                relevance_scores = await calculate_job_relevance_batch(new_jobs[:30], skills)
                for job, score in zip(new_jobs[:30], relevance_scores):
                    job['relevance_score'] = score
                relevant_jobs = sorted(new_jobs[:30], key=lambda x: x.get('relevance_score', 0), reverse=True)[:20]
            except Exception as e:
                logging.error(f"Ranking error: {e}")
        
        # Generate email
        query_summary = ", ".join(search_queries[:3])
        html_content = generate_digest_email_html(relevant_jobs, user_name, query_summary)
        
        # Send email in background
        def send_task(to_email, content, jobs_to_mark):
            success = send_email_gmail(
                to_email,
                f"🎯 MedMatch Daily Digest: {len(jobs_to_mark)} New Quality Jobs",
                content
            )
            return success
        
        # Mark jobs as emailed
        for job in relevant_jobs:
            await mark_job_emailed(job, email)
        
        # Send email
        success = send_email_gmail(
            email,
            f"🎯 MedMatch Daily Digest: {len(relevant_jobs)} New Quality Jobs",
            html_content
        )
        
        if success:
            sent_count += 1
            # Update last_sent timestamp
            await db.digest_settings.update_one(
                {"email": email},
                {"$set": {"last_sent": datetime.now(timezone.utc).isoformat()}}
            )
            results.append({"email": email, "status": "sent", "jobs_count": len(relevant_jobs)})
        else:
            results.append({"email": email, "status": "failed", "reason": "Email send failed"})
    
    return {
        "message": f"Scheduled digest completed",
        "total_subscribers": len(subscribers),
        "sent_count": sent_count,
        "total_jobs_found": len(unique_jobs),
        "results": results
    }

# ============== COVER LETTER GENERATOR ==============

@api_router.post("/cover-letter/generate")
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a personalized cover letter based on job requirements and resume skills.
    Uses AI to identify transferable skills and create a compelling letter.
    """
    # Get resume data
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        raise HTTPException(status_code=404, detail="Please upload your resume first")
    
    job_data = {
        "job_title": request.job_title,
        "company": request.company,
        "job_description": request.job_description,
        "job_url": request.job_url
    }
    
    # Generate cover letter using AI
    result = await generate_cover_letter_ai(resume_doc, job_data)
    
    # Save generated cover letter to database
    cover_letter_doc = {
        "id": str(uuid.uuid4()),
        "job_title": request.job_title,
        "company": request.company,
        "cover_letter": result.get("cover_letter", ""),
        "key_matches": result.get("key_matches", []),
        "transferable_skills": result.get("transferable_skills", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cover_letters.insert_one(cover_letter_doc)
    
    return {
        "cover_letter": result.get("cover_letter", ""),
        "key_matches": result.get("key_matches", []),
        "transferable_skills": result.get("transferable_skills", []),
        "suggestions": result.get("suggestions", []),
        "job_title": request.job_title,
        "company": request.company
    }

@api_router.get("/cover-letter/history")
async def get_cover_letter_history():
    """Get history of generated cover letters"""
    docs = await db.cover_letters.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return docs

@api_router.delete("/cover-letter/{letter_id}")
async def delete_cover_letter(letter_id: str):
    """Delete a saved cover letter"""
    result = await db.cover_letters.delete_one({"id": letter_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return {"message": "Cover letter deleted"}

# ============== CALLBACK PREDICTION ENDPOINTS ==============

@api_router.post("/jobs/predict-callback")
async def predict_job_callback(request: CallbackPredictionRequest):
    """
    Predict callback probability for a job based on resume match.
    Uses AI to analyze skills match, experience alignment, competition level, and timing.
    """
    # Get resume data
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        raise HTTPException(status_code=404, detail="Please upload your resume first")
    
    job_data = {
        "job_title": request.job_title,
        "company": request.company,
        "job_description": request.job_description,
        "job_url": request.job_url,
        "posted_at": request.posted_at,
        "location": request.location
    }
    
    # Get AI prediction
    prediction = await predict_callback_probability(resume_doc, job_data)
    
    # Save prediction to history
    prediction_doc = {
        "id": str(uuid.uuid4()),
        "job_title": request.job_title,
        "company": request.company,
        "probability_score": prediction.get("probability_score", 0),
        "probability_label": prediction.get("probability_label", "Unknown"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.callback_predictions.insert_one(prediction_doc)
    
    return {
        "probability_score": prediction.get("probability_score", 50),
        "probability_label": prediction.get("probability_label", "Medium"),
        "match_breakdown": prediction.get("match_breakdown", {}),
        "strengths": prediction.get("strengths", []),
        "gaps": prediction.get("gaps", []),
        "competition_estimate": prediction.get("competition_estimate", "Unknown"),
        "competition_reasoning": prediction.get("competition_reasoning", ""),
        "timing_advice": prediction.get("timing_advice", ""),
        "recommendations": prediction.get("recommendations", []),
        "interview_likelihood": prediction.get("interview_likelihood", ""),
        "key_differentiators": prediction.get("key_differentiators", []),
        "job_title": request.job_title,
        "company": request.company
    }

@api_router.get("/jobs/prediction-history")
async def get_prediction_history():
    """Get history of callback predictions"""
    docs = await db.callback_predictions.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return docs

@api_router.delete("/jobs/prediction-history/{prediction_id}")
async def delete_prediction(prediction_id: str):
    """Delete a prediction from history"""
    result = await db.callback_predictions.delete_one({"id": prediction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"message": "Prediction deleted"}

# Quick probability score endpoint (lighter weight for job cards)
@api_router.post("/jobs/quick-probability")
async def get_quick_probability(request: CallbackPredictionRequest):
    """
    Get a quick callback probability score for display on job cards.
    Uses a simplified analysis for faster response.
    """
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        return {"probability_score": 0, "probability_label": "Upload Resume", "quick": True}
    
    # Calculate a quick score based on keyword matching
    resume_skills = set([s.lower() for s in resume_doc.get('skills', [])])
    job_text = f"{request.job_title} {request.job_description}".lower()
    
    # Count matching skills
    matching_skills = sum(1 for skill in resume_skills if skill in job_text)
    total_skills = len(resume_skills) if resume_skills else 1
    
    # Base score from skills match
    skills_score = min((matching_skills / total_skills) * 100, 100) if total_skills > 0 else 30
    
    # Adjust for job freshness
    freshness_bonus = 0
    if request.posted_at:
        try:
            posted_date = datetime.fromisoformat(request.posted_at.replace('Z', '+00:00'))
            days_ago = (datetime.now(timezone.utc) - posted_date).days
            if days_ago <= 1:
                freshness_bonus = 15
            elif days_ago <= 3:
                freshness_bonus = 10
            elif days_ago <= 7:
                freshness_bonus = 5
            elif days_ago > 14:
                freshness_bonus = -10
        except:
            pass
    
    # Calculate final score
    final_score = int(min(max(skills_score + freshness_bonus, 10), 95))
    
    # Determine label
    if final_score >= 75:
        label = "Very High"
    elif final_score >= 60:
        label = "High"
    elif final_score >= 40:
        label = "Medium"
    elif final_score >= 25:
        label = "Low"
    else:
        label = "Very Low"
    
    return {
        "probability_score": final_score,
        "probability_label": label,
        "matching_skills": matching_skills,
        "quick": True
    }

@api_router.post("/jobs/manual")
async def create_manual_job(job: ManualJobCreate):
    new_job = Job(
        title=job.title, company=job.company, location=job.location,
        description=job.description, url=job.url, salary=job.salary,
        tags=job.tags, source="Manual"
    )
    return new_job

# ============== INTERVIEW PREPARATION ENDPOINTS ==============

class InterviewQuestionsRequest(BaseModel):
    job_title: str
    company: str = ""
    resume_skills: List[str] = []

class InterviewAnswerRequest(BaseModel):
    question: str
    job_title: str
    company: str = ""

class StarPolishRequest(BaseModel):
    question: str
    situation: str
    task: str
    action: str
    result: str

class CompanyResearchRequest(BaseModel):
    company: str

class MockFeedbackRequest(BaseModel):
    answers: List[Dict[str, Any]]
    job_title: str

@api_router.post("/interview/generate-questions")
async def generate_interview_questions(request: InterviewQuestionsRequest):
    """Generate tailored interview questions based on job title and skills"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach. Generate realistic interview questions for the given job role.

Return ONLY valid JSON array with this structure:
[
    {
        "text": "<question text>",
        "category": "<behavioral|technical|situational|company>",
        "difficulty": "<easy|medium|hard>"
    }
]

Generate 10-12 questions covering:
- 3-4 behavioral questions (STAR method appropriate)
- 3-4 technical/role-specific questions
- 2-3 situational questions
- 2 company fit questions

Make questions specific to the role and industry."""
    )
    
    skills_text = ", ".join(request.resume_skills[:15]) if request.resume_skills else "Not provided"
    
    user_message = UserMessage(
        text=f"Generate interview questions for: {request.job_title}\nCompany: {request.company or 'General'}\nCandidate Skills: {skills_text}"
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        questions = json.loads(clean_response)
        
        # Store questions in database for Voice/Video Coach to use
        await db.cached_questions.update_one(
            {"type": "interview_questions"},
            {"$set": {
                "questions": questions,
                "job_title": request.job_title,
                "company": request.company,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return {"questions": questions}
    except Exception as e:
        logging.error(f"Question generation error: {e}")
        # Return default questions
        return {"questions": [
            {"text": f"Tell me about your experience relevant to {request.job_title}.", "category": "behavioral", "difficulty": "easy"},
            {"text": "Describe a challenging project you've worked on.", "category": "behavioral", "difficulty": "medium"},
            {"text": "How do you prioritize tasks when facing multiple deadlines?", "category": "situational", "difficulty": "medium"},
            {"text": "Where do you see yourself in 5 years?", "category": "company", "difficulty": "easy"},
            {"text": "What's your greatest professional achievement?", "category": "behavioral", "difficulty": "medium"},
        ]}

@api_router.get("/interview/cached-questions")
async def get_cached_questions():
    """Get previously generated interview questions for Voice/Video Coach"""
    cached = await db.cached_questions.find_one({"type": "interview_questions"}, {"_id": 0})
    if cached and cached.get("questions"):
        return {"questions": cached["questions"], "job_title": cached.get("job_title", ""), "company": cached.get("company", "")}
    return {"questions": [], "job_title": "", "company": ""}

@api_router.post("/interview/generate-answer")
async def generate_interview_answer(request: InterviewAnswerRequest):
    """Generate a suggested answer based on the question and context"""
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        raise HTTPException(status_code=404, detail="Please upload your resume first")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach. Generate a strong, personalized answer to the interview question using the candidate's background.

Return ONLY valid JSON with this structure:
{
    "answer": "<2-3 paragraph answer>",
    "key_points": ["<point 1>", "<point 2>", "<point 3>"],
    "tips": "<one specific tip for delivery>"
}

Make the answer:
- Specific and uses examples from their experience
- Professional but conversational tone
- Includes relevant metrics/outcomes where applicable
- 1-2 minutes when spoken aloud"""
    )
    
    skills_text = ", ".join(resume_doc.get('skills', [])[:15])
    experience_text = "\n".join([
        f"- {exp.get('title', '')} at {exp.get('company', '')}"
        for exp in resume_doc.get('experience', [])[:3]
    ])
    
    user_message = UserMessage(
        text=f"""Question: {request.question}

Role: {request.job_title}
Company: {request.company or 'Not specified'}

Candidate Background:
Skills: {skills_text}
Experience:
{experience_text}
Summary: {resume_doc.get('summary', 'Not provided')}"""
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"Answer generation error: {e}")
        return {
            "answer": "I would be happy to answer this question. Based on my experience...",
            "key_points": ["Highlight relevant experience", "Use specific examples", "Show enthusiasm"],
            "tips": "Practice this answer out loud to refine your delivery."
        }

@api_router.post("/interview/polish-star")
async def polish_star_answer(request: StarPolishRequest):
    """Polish a STAR method answer"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach. Take the candidate's STAR method components and create a polished, professional answer.

Return ONLY valid JSON with this structure:
{
    "answer": "<polished 2-3 paragraph answer flowing naturally through S-T-A-R>",
    "key_points": ["<strength 1>", "<strength 2>"],
    "tips": "<delivery tip>"
}

Make it:
- Flow naturally without explicitly saying "Situation, Task, Action, Result"
- Sound conversational but professional
- Include specific details and metrics where provided
- Be 1-2 minutes when spoken"""
    )
    
    user_message = UserMessage(
        text=f"""Question: {request.question}

Candidate's STAR Components:
SITUATION: {request.situation}
TASK: {request.task}
ACTION: {request.action}
RESULT: {request.result}

Polish this into a compelling interview answer."""
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"STAR polish error: {e}")
        return {
            "answer": f"{request.situation} {request.task} {request.action} {request.result}",
            "key_points": ["Good structure", "Add more specific details"],
            "tips": "Practice delivering this naturally."
        }

@api_router.post("/interview/research-company")
async def research_company(request: CompanyResearchRequest):
    """Generate company research insights for interview prep"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert career coach. Provide helpful company research for interview preparation.

Return ONLY valid JSON with this structure:
{
    "overview": "<2-3 sentence company overview>",
    "culture": "<company culture insights>",
    "interview_tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
    "questions_to_ask": ["<question 1>", "<question 2>", "<question 3>"],
    "values": ["<value 1>", "<value 2>", "<value 3>"]
}

Be helpful and provide actionable insights for interview prep."""
    )
    
    user_message = UserMessage(
        text=f"Provide interview preparation research for: {request.company}"
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"Company research error: {e}")
        return {
            "overview": f"{request.company} is a notable company in their industry.",
            "culture": "Research their website and LinkedIn for culture insights.",
            "interview_tips": ["Research recent company news", "Understand their products/services", "Know their mission statement"],
            "questions_to_ask": ["What does success look like in this role?", "How would you describe the team culture?", "What are the growth opportunities?"],
            "values": ["Innovation", "Excellence", "Collaboration"]
        }

@api_router.post("/interview/mock-feedback")
async def get_mock_interview_feedback(request: MockFeedbackRequest):
    """Get AI feedback on mock interview answers"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach providing feedback on mock interview answers.

Return ONLY valid JSON with this structure:
{
    "overall_score": <0-100>,
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
    "question_feedback": [
        {"question_num": 1, "score": <0-100>, "feedback": "<brief feedback>"}
    ]
}

Be constructive and specific in feedback."""
    )
    
    answers_text = "\n\n".join([
        f"Q{i+1}: {a['question'].get('text', a['question'])}\nAnswer: {a['answer']}"
        for i, a in enumerate(request.answers)
    ])
    
    user_message = UserMessage(
        text=f"Role: {request.job_title}\n\nMock Interview Responses:\n{answers_text}\n\nProvide feedback."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"Mock feedback error: {e}")
        return {
            "overall_score": 70,
            "strengths": ["Completed all questions", "Showed effort"],
            "improvements": ["Add more specific examples", "Practice STAR method", "Include metrics"],
            "question_feedback": []
        }

class VoiceFeedbackRequest(BaseModel):
    question: str
    answer: str
    duration_seconds: int
    job_title: str = ""

@api_router.post("/interview/voice-feedback")
async def get_voice_interview_feedback(request: VoiceFeedbackRequest):
    """
    Analyze a spoken interview answer and provide detailed feedback on:
    - Content quality and relevance
    - Delivery pace (words per minute)
    - Confidence indicators
    - Structure and organization
    - Specific improvement suggestions
    """
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM not configured")
    
    # Calculate metrics
    word_count = len(request.answer.split())
    words_per_minute = round((word_count / max(request.duration_seconds, 1)) * 60) if request.duration_seconds > 0 else 0
    
    # Ideal pace is 120-150 WPM for interviews
    if words_per_minute < 100:
        pace_feedback = "too slow"
        pace_score = max(50, 100 - (100 - words_per_minute))
    elif words_per_minute > 180:
        pace_feedback = "too fast"
        pace_score = max(50, 100 - (words_per_minute - 180))
    else:
        pace_feedback = "good"
        pace_score = min(100, 80 + (20 - abs(135 - words_per_minute) // 2))
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach analyzing a spoken interview answer. 
Evaluate the content, structure, and delivery indicators from the transcribed speech.

Return ONLY valid JSON with this structure:
{
    "overall_score": <0-100>,
    "content_score": <0-100>,
    "confidence_score": <0-100>,
    "structure_score": <0-100>,
    "strengths": ["<strength 1>", "<strength 2>"],
    "improvements": ["<improvement 1>", "<improvement 2>"],
    "delivery_tip": "<specific tip for spoken delivery>",
    "confidence_indicators": {
        "positive": ["<positive indicator>"],
        "negative": ["<area needing confidence>"]
    },
    "suggested_additions": ["<what to add>"],
    "filler_words_detected": <true/false>
}

Consider:
1. Does the answer directly address the question?
2. Are there specific examples or metrics?
3. Is the structure clear (situation, action, result)?
4. Are there confidence markers (decisive language, specific details)?
5. Are there hesitation markers (filler words, vague language)?
6. Is the length appropriate (1-2 minutes ideal)?"""
    )
    
    # Get resume for context
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    skills_text = ", ".join(resume_doc.get('skills', [])[:10]) if resume_doc else "Not provided"
    
    user_message = UserMessage(
        text=f"""Question: {request.question}

Spoken Answer (transcribed):
"{request.answer}"

Metrics:
- Word count: {word_count}
- Duration: {request.duration_seconds} seconds
- Speaking pace: {words_per_minute} words per minute
- Pace assessment: {pace_feedback}

Candidate's skills: {skills_text}
Target role: {request.job_title or 'Not specified'}

Analyze this spoken interview answer and provide detailed feedback."""
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        ai_feedback = json.loads(clean_response)
        
        # Combine AI feedback with calculated metrics
        return {
            "overall_score": ai_feedback.get("overall_score", 70),
            "content_score": ai_feedback.get("content_score", 70),
            "confidence_score": ai_feedback.get("confidence_score", 70),
            "structure_score": ai_feedback.get("structure_score", 70),
            "pace_score": pace_score,
            "word_count": word_count,
            "words_per_minute": words_per_minute,
            "pace_feedback": pace_feedback,
            "strengths": ai_feedback.get("strengths", []),
            "improvements": ai_feedback.get("improvements", []),
            "delivery_tip": ai_feedback.get("delivery_tip", "Practice speaking at a steady pace"),
            "confidence_indicators": ai_feedback.get("confidence_indicators", {}),
            "suggested_additions": ai_feedback.get("suggested_additions", []),
            "filler_words_detected": ai_feedback.get("filler_words_detected", False),
            "ideal_pace_range": "120-150 WPM"
        }
        
    except Exception as e:
        logging.error(f"Voice feedback error: {e}")
        return {
            "overall_score": 65,
            "content_score": 65,
            "confidence_score": 70,
            "structure_score": 60,
            "pace_score": pace_score,
            "word_count": word_count,
            "words_per_minute": words_per_minute,
            "pace_feedback": pace_feedback,
            "strengths": ["Completed the answer", "Spoke clearly"],
            "improvements": ["Add more specific examples", "Include measurable outcomes"],
            "delivery_tip": "Try to maintain a steady pace around 130-140 words per minute",
            "confidence_indicators": {"positive": [], "negative": []},
            "suggested_additions": [],
            "filler_words_detected": False,
            "ideal_pace_range": "120-150 WPM"
        }

# ============== ANALYTICS ENDPOINTS ==============

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard(days: int = 30):
    """
    Get comprehensive analytics for the job application dashboard.
    """
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    previous_start = start_date - timedelta(days=days)
    
    # Get all applications
    all_apps = await db.applications.find({}, {"_id": 0}).to_list(1000)
    
    # Filter by date range
    recent_apps = []
    previous_apps = []
    for app in all_apps:
        app_date = app.get('applied_at')
        if app_date:
            if isinstance(app_date, str):
                try:
                    app_date = datetime.fromisoformat(app_date.replace('Z', '+00:00'))
                except:
                    continue
            if app_date >= start_date:
                recent_apps.append(app)
            elif app_date >= previous_start:
                previous_apps.append(app)
    
    # Calculate metrics
    total = len(recent_apps)
    interviews = len([a for a in recent_apps if a.get('status') == 'Interview'])
    offers = len([a for a in recent_apps if a.get('status') == 'Offer'])
    rejections = len([a for a in recent_apps if a.get('status') == 'Rejected'])
    pending = len([a for a in recent_apps if a.get('status') == 'Applied'])
    
    # Response rate = (interviews + offers + rejections) / total
    responses = interviews + offers + rejections
    response_rate = round((responses / total) * 100) if total > 0 else 0
    interview_rate = round((interviews / total) * 100) if total > 0 else 0
    offer_rate = round((offers / total) * 100) if total > 0 else 0
    
    # Top companies
    company_counts = {}
    for app in recent_apps:
        company = app.get('job', {}).get('company', 'Unknown')
        company_counts[company] = company_counts.get(company, 0) + 1
    top_companies = sorted(
        [{"name": k, "count": v} for k, v in company_counts.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:5]
    
    # Applications by source
    source_counts = {}
    for app in recent_apps:
        source = app.get('job', {}).get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Recent activity
    recent_activity = []
    for app in sorted(recent_apps, key=lambda x: x.get('applied_at', ''), reverse=True)[:10]:
        recent_activity.append({
            "date": app.get('applied_at', ''),
            "job_title": app.get('job', {}).get('title', 'Unknown'),
            "company": app.get('job', {}).get('company', 'Unknown'),
            "status": app.get('status', 'Applied')
        })
    
    return {
        "total_applications": total,
        "interviews": interviews,
        "offers": offers,
        "rejections": rejections,
        "pending": pending,
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
        "avg_response_days": 7,  # Placeholder
        "applications_by_source": source_counts,
        "applications_by_status": {
            "Applied": pending,
            "Interview": interviews,
            "Offer": offers,
            "Rejected": rejections
        },
        "top_companies": top_companies,
        "recent_activity": recent_activity,
        "weekly_comparison": {
            "current": len(recent_apps),
            "previous": len(previous_apps)
        }
    }

# ============== MULTIPLE RESUME PROFILES ==============

class ResumeProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Profile name like "Tech Resume", "Management Resume"
    full_name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    summary: str = ""
    raw_text: str = ""
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.get("/resume/profiles")
async def get_all_resume_profiles():
    """Get all resume profiles"""
    profiles = await db.resume_profiles.find({}, {"_id": 0}).to_list(20)
    return profiles

@api_router.post("/resume/profiles")
async def create_resume_profile(profile: ResumeProfile):
    """Create a new resume profile"""
    # If this is the first profile or marked as default, set as default
    existing = await db.resume_profiles.find({}).to_list(20)
    if not existing or profile.is_default:
        # Unset any existing default
        await db.resume_profiles.update_many({}, {"$set": {"is_default": False}})
        profile.is_default = True
    
    profile_dict = profile.model_dump()
    profile_dict['created_at'] = profile_dict['created_at'].isoformat()
    profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
    
    await db.resume_profiles.insert_one(profile_dict)
    return profile_dict

@api_router.put("/resume/profiles/{profile_id}")
async def update_resume_profile(profile_id: str, updates: Dict[str, Any]):
    """Update a resume profile"""
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # Handle default switching
    if updates.get('is_default'):
        await db.resume_profiles.update_many({}, {"$set": {"is_default": False}})
    
    result = await db.resume_profiles.update_one(
        {"id": profile_id},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Profile updated"}

@api_router.delete("/resume/profiles/{profile_id}")
async def delete_resume_profile(profile_id: str):
    """Delete a resume profile"""
    result = await db.resume_profiles.delete_one({"id": profile_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}

@api_router.post("/resume/profiles/{profile_id}/set-default")
async def set_default_profile(profile_id: str):
    """Set a profile as the default"""
    # Unset all defaults
    await db.resume_profiles.update_many({}, {"$set": {"is_default": False}})
    # Set the new default
    result = await db.resume_profiles.update_one(
        {"id": profile_id},
        {"$set": {"is_default": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Also update the main resume collection with this profile
    profile = await db.resume_profiles.find_one({"id": profile_id}, {"_id": 0})
    if profile:
        await db.resumes.delete_many({})
        await db.resumes.insert_one(profile)
    
    return {"message": "Default profile set"}

@api_router.post("/resume/profiles/upload")
async def upload_resume_to_profile(file: UploadFile = File(...), profile_name: str = "Default"):
    """Upload and parse a resume into a new or existing profile"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    
    # Extract text from PDF
    pdf_reader = PdfReader(io.BytesIO(content))
    raw_text = ""
    for page in pdf_reader.pages:
        raw_text += page.extract_text() + "\n"
    
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Parse with AI
    parsed = await parse_resume_with_ai(raw_text)
    
    # Check if profile exists
    existing = await db.resume_profiles.find_one({"name": profile_name}, {"_id": 0})
    
    profile_id = existing.get('id') if existing else str(uuid.uuid4())
    is_default = existing.get('is_default', False) if existing else True
    
    if not existing:
        # If first profile, make it default
        count = await db.resume_profiles.count_documents({})
        is_default = count == 0
    
    profile_doc = {
        "id": profile_id,
        "name": profile_name,
        "full_name": parsed.get('full_name', ''),
        "email": parsed.get('email', ''),
        "phone": parsed.get('phone', ''),
        "skills": parsed.get('skills', []),
        "experience": parsed.get('experience', []),
        "education": parsed.get('education', []),
        "summary": parsed.get('summary', ''),
        "raw_text": raw_text,
        "is_default": is_default,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if existing:
        await db.resume_profiles.update_one({"id": profile_id}, {"$set": profile_doc})
    else:
        await db.resume_profiles.insert_one(profile_doc)
    
    # If default, also update main resume
    if is_default:
        await db.resumes.delete_many({})
        await db.resumes.insert_one(profile_doc)
    
    return profile_doc

# ============== VIDEO RECORDING ENDPOINTS ==============

class VideoRecordingMeta(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    duration_seconds: int
    transcript: str = ""
    feedback: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.post("/interview/video-feedback")
async def analyze_video_recording(request: Dict[str, Any]):
    """
    Analyze a video interview recording.
    Accepts transcript and metadata, returns AI feedback.
    (Video file storage would require additional cloud storage integration)
    """
    question = request.get('question', '')
    transcript = request.get('transcript', '')
    duration = request.get('duration_seconds', 0)
    
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    # Get voice feedback (reuse existing logic)
    voice_feedback_request = VoiceFeedbackRequest(
        question=question,
        answer=transcript,
        duration_seconds=duration,
        job_title=request.get('job_title', '')
    )
    
    feedback = await get_voice_interview_feedback(voice_feedback_request)
    
    # Add video-specific feedback
    feedback['video_tips'] = [
        "Maintain eye contact with the camera",
        "Keep your background professional and uncluttered",
        "Ensure good lighting on your face",
        "Sit up straight and use confident body language",
        "Dress professionally from head to toe"
    ]
    
    # Save recording metadata
    recording_doc = {
        "id": str(uuid.uuid4()),
        "question": question,
        "transcript": transcript,
        "duration_seconds": duration,
        "feedback": feedback,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.video_recordings.insert_one(recording_doc)
    
    return {
        **feedback,
        "recording_id": recording_doc['id']
    }

@api_router.get("/interview/video-recordings")
async def get_video_recordings():
    """Get all video recording sessions"""
    recordings = await db.video_recordings.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return recordings

@api_router.delete("/interview/video-recordings/{recording_id}")
async def delete_video_recording(recording_id: str):
    """Delete a video recording"""
    result = await db.video_recordings.delete_one({"id": recording_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"message": "Recording deleted"}

# ============== AI VIDEO ANALYSIS WITH VISION ==============

class VideoFrameAnalysisRequest(BaseModel):
    frame_base64: str  # Base64 encoded image frame from video
    question: str = ""
    context: str = ""  # Additional context like "behavioral interview", "technical interview"

class VideoAnalysisResponse(BaseModel):
    eye_contact_score: int  # 0-100
    posture_score: int  # 0-100
    confidence_score: int  # 0-100
    facial_expression: str
    body_language_tips: List[str]
    overall_assessment: str
    strengths: List[str]
    improvements: List[str]

@api_router.post("/interview/analyze-video-frame")
async def analyze_video_frame(request: VideoFrameAnalysisRequest):
    """
    Analyze a video frame using AI Vision to provide body language feedback.
    Uses OpenAI Vision API via Emergent LLM Key.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM key not configured")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert interview coach and body language analyst. 
            Analyze the interview candidate's video frame and provide detailed feedback on:
            1. Eye contact (are they looking at camera/interviewer)
            2. Posture (sitting upright, confident stance)
            3. Facial expression (friendly, confident, nervous)
            4. Body language (open vs closed, hand gestures)
            5. Professional appearance (lighting, background, attire)
            
            Return a JSON object with:
            - eye_contact_score: 0-100
            - posture_score: 0-100
            - confidence_score: 0-100
            - facial_expression: string description
            - body_language_tips: array of specific tips
            - overall_assessment: 2-3 sentence summary
            - strengths: array of positive observations
            - improvements: array of areas to work on
            
            Be encouraging but honest. Return ONLY valid JSON."""
        ).with_model("openai", "gpt-5.2")
        
        # Create image content from base64
        image_content = ImageContent(image_base64=request.frame_base64)
        
        context_text = f"Interview context: {request.context}" if request.context else ""
        question_text = f"The candidate is answering: '{request.question}'" if request.question else ""
        
        user_message = UserMessage(
            text=f"Analyze this interview candidate's body language and presentation. {context_text} {question_text}",
            file_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        analysis = json.loads(clean_response)
        
        return {
            "eye_contact_score": analysis.get("eye_contact_score", 50),
            "posture_score": analysis.get("posture_score", 50),
            "confidence_score": analysis.get("confidence_score", 50),
            "facial_expression": analysis.get("facial_expression", "neutral"),
            "body_language_tips": analysis.get("body_language_tips", []),
            "overall_assessment": analysis.get("overall_assessment", ""),
            "strengths": analysis.get("strengths", []),
            "improvements": analysis.get("improvements", [])
        }
        
    except json.JSONDecodeError:
        return {
            "eye_contact_score": 50,
            "posture_score": 50,
            "confidence_score": 50,
            "facial_expression": "Unable to analyze",
            "body_language_tips": ["Ensure good lighting", "Face the camera directly"],
            "overall_assessment": "Could not fully analyze the frame. Please ensure clear video quality.",
            "strengths": [],
            "improvements": ["Improve video quality for better analysis"]
        }
    except Exception as e:
        logging.error(f"Video frame analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== PDF EXPORT ==============

class CoverLetterExportRequest(BaseModel):
    cover_letter: str
    job_title: str
    company: str
    candidate_name: str = ""

class InterviewPrepExportRequest(BaseModel):
    job_title: str
    company: str
    questions: List[Dict[str, Any]]
    candidate_name: str = ""
    notes: str = ""

# ============== SALARY INSIGHTS ==============

class SalaryInsightsRequest(BaseModel):
    job_title: str
    location: str = "Remote, USA"
    years_experience: int = 5
    current_salary: Optional[int] = None
    skills: List[str] = []

@api_router.post("/salary/insights")
async def get_salary_insights(request: SalaryInsightsRequest):
    """Get AI-powered salary insights and negotiation tips"""
    
    prompt = f"""You are a salary negotiation expert and compensation analyst. Provide detailed salary insights for:

Job Title: {request.job_title}
Location: {request.location}
Years of Experience: {request.years_experience}
{f"Current Salary: ${request.current_salary:,}" if request.current_salary else "Current Salary: Not provided"}
{f"Key Skills: {', '.join(request.skills[:10])}" if request.skills else ""}

Provide a JSON response with the following structure:
{{
    "job_title": "{request.job_title}",
    "location": "{request.location}",
    "years_experience": {request.years_experience},
    "salary_range": {{
        "low": <10th percentile salary as integer>,
        "median": <50th percentile salary as integer>,
        "high": <90th percentile salary as integer>
    }},
    "negotiation_tips": [
        "<tip 1 - specific and actionable>",
        "<tip 2>",
        "<tip 3>",
        "<tip 4>",
        "<tip 5>"
    ],
    "salary_factors": [
        {{"factor": "<factor name>", "impact": "positive|negative|neutral", "description": "<how it affects salary>"}},
        {{"factor": "<factor 2>", "impact": "positive|negative|neutral", "description": "<description>"}},
        {{"factor": "<factor 3>", "impact": "positive|negative|neutral", "description": "<description>"}}
    ],
    "talk_scripts": [
        {{"scenario": "Initial Offer Response", "script": "<what to say when you receive an offer>"}},
        {{"scenario": "Asking for More", "script": "<how to counter-offer>"}},
        {{"scenario": "Justifying Your Ask", "script": "<how to explain your value>"}}
    ],
    "skills_premium": [
        {{"skill": "<high-value skill>", "premium": <percentage increase as integer>}},
        {{"skill": "<skill 2>", "premium": <percentage>}},
        {{"skill": "<skill 3>", "premium": <percentage>}}
    ]
}}

Be realistic with salary ranges based on current market data (2024-2025). Consider remote work premiums and location-based cost of living adjustments.
Return ONLY the JSON object, no additional text."""

    try:
        response = chat(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            api_key=EMERGENT_LLM_KEY
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up JSON response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        insights = json.loads(content)
        return insights
        
    except json.JSONDecodeError as e:
        logging.error(f"Salary insights JSON parse error: {e}")
        # Return fallback data
        return {
            "job_title": request.job_title,
            "location": request.location,
            "years_experience": request.years_experience,
            "salary_range": {
                "low": 80000,
                "median": 120000,
                "high": 180000
            },
            "negotiation_tips": [
                "Research the company's compensation philosophy before negotiating",
                "Always negotiate - most employers expect it and leave room in their initial offer",
                "Focus on the total compensation package, not just base salary",
                "Use specific numbers rather than ranges when making counter-offers",
                "Practice your negotiation conversation beforehand"
            ],
            "salary_factors": [
                {"factor": "Experience Level", "impact": "positive", "description": "More years typically means higher compensation"},
                {"factor": "Location", "impact": "neutral", "description": "Remote roles may have location-based adjustments"},
                {"factor": "Industry", "impact": "positive", "description": "Tech and finance typically pay premium rates"}
            ],
            "talk_scripts": [
                {"scenario": "Initial Offer Response", "script": "Thank you for the offer. I'm excited about this opportunity. I'd like to discuss the compensation package - based on my research and experience, I was expecting something closer to [X]."},
                {"scenario": "Asking for More", "script": "I appreciate the offer of [X]. Given my [specific experience/skills], I believe [Y] would be more aligned with the value I'll bring to this role."},
                {"scenario": "Justifying Your Ask", "script": "In my current/previous role, I [specific achievement]. I'm confident I can deliver similar results here, which is why I'm requesting [amount]."}
            ],
            "skills_premium": [
                {"skill": "Leadership", "premium": 15},
                {"skill": "Cloud Architecture", "premium": 12},
                {"skill": "AI/ML", "premium": 20}
            ]
        }
    except Exception as e:
        logging.error(f"Salary insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate salary insights")

@api_router.post("/export/cover-letter-html")
async def export_cover_letter_html(request: CoverLetterExportRequest):
    """
    Generate HTML for cover letter that can be converted to PDF on frontend.
    """
    resume = await db.resumes.find_one({}, {"_id": 0})
    candidate_name = request.candidate_name or resume.get('full_name', 'Candidate') if resume else 'Candidate'
    candidate_email = resume.get('email', '') if resume else ''
    
    # Format cover letter paragraphs
    paragraphs = request.cover_letter.split('\n\n')
    formatted_paragraphs = ''.join([f'<p style="margin-bottom: 16px; line-height: 1.6;">{p}</p>' for p in paragraphs if p.strip()])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Cover Letter - {request.job_title} at {request.company}</title>
        <style>
            body {{
                font-family: 'Georgia', 'Times New Roman', serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                color: #1a1a1a;
                line-height: 1.6;
            }}
            .header {{
                margin-bottom: 40px;
                border-bottom: 2px solid #20b2aa;
                padding-bottom: 20px;
            }}
            .header h1 {{
                color: #20b2aa;
                font-size: 28px;
                margin: 0;
            }}
            .header p {{
                color: #666;
                margin: 5px 0;
            }}
            .date {{
                text-align: right;
                color: #666;
                margin-bottom: 30px;
            }}
            .recipient {{
                margin-bottom: 30px;
            }}
            .content {{
                margin-bottom: 40px;
            }}
            .signature {{
                margin-top: 40px;
            }}
            .footer {{
                margin-top: 60px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #999;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{candidate_name}</h1>
            <p>{candidate_email}</p>
        </div>
        
        <div class="date">
            {datetime.now().strftime('%B %d, %Y')}
        </div>
        
        <div class="recipient">
            <p><strong>RE: {request.job_title}</strong></p>
            <p>{request.company}</p>
        </div>
        
        <div class="content">
            {formatted_paragraphs}
        </div>
        
        <div class="signature">
            <p>Sincerely,</p>
            <p><strong>{candidate_name}</strong></p>
        </div>
        
        <div class="footer">
            Generated with MedMatch - AI-Powered Job Search Assistant
        </div>
    </body>
    </html>
    """
    
    return {"html": html, "filename": f"Cover_Letter_{request.company.replace(' ', '_')}.pdf"}

@api_router.post("/export/interview-prep-html")
async def export_interview_prep_html(request: InterviewPrepExportRequest):
    """
    Generate HTML for interview preparation notes that can be converted to PDF.
    """
    resume = await db.resumes.find_one({}, {"_id": 0})
    candidate_name = request.candidate_name or resume.get('full_name', 'Candidate') if resume else 'Candidate'
    
    # Format questions
    questions_html = ""
    for i, q in enumerate(request.questions, 1):
        question_text = q.get('text', q.get('question', ''))
        category = q.get('category', 'General')
        difficulty = q.get('difficulty', 'medium')
        suggested_answer = q.get('suggested_answer', q.get('answer', ''))
        
        questions_html += f"""
        <div class="question-card">
            <div class="question-header">
                <span class="question-number">Q{i}</span>
                <span class="category">{category}</span>
                <span class="difficulty {difficulty}">{difficulty.capitalize()}</span>
            </div>
            <h3 class="question-text">{question_text}</h3>
            {f'<div class="suggested-answer"><strong>Suggested Approach:</strong><p>{suggested_answer}</p></div>' if suggested_answer else ''}
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Interview Prep - {request.job_title} at {request.company}</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                color: #1a1a1a;
            }}
            .header {{
                background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 24px;
            }}
            .header .subtitle {{
                color: #20b2aa;
                font-size: 18px;
                margin: 0;
            }}
            .header .meta {{
                color: #999;
                font-size: 14px;
                margin-top: 15px;
            }}
            .section-title {{
                color: #20b2aa;
                border-bottom: 2px solid #20b2aa;
                padding-bottom: 10px;
                margin: 30px 0 20px;
            }}
            .question-card {{
                background: #f8f8f8;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #20b2aa;
            }}
            .question-header {{
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }}
            .question-number {{
                background: #20b2aa;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .category {{
                background: #e2e8f0;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
            .difficulty {{
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
            .difficulty.easy {{ background: #d1fae5; color: #065f46; }}
            .difficulty.medium {{ background: #fef3c7; color: #92400e; }}
            .difficulty.hard {{ background: #fee2e2; color: #991b1b; }}
            .question-text {{
                margin: 0 0 15px 0;
                font-size: 16px;
            }}
            .suggested-answer {{
                background: white;
                padding: 15px;
                border-radius: 6px;
                font-size: 14px;
                color: #555;
            }}
            .notes-section {{
                background: #fef3c7;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
            }}
            .notes-section h3 {{
                color: #92400e;
                margin: 0 0 10px;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #999;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Interview Preparation Guide</h1>
            <p class="subtitle">{request.job_title} at {request.company}</p>
            <p class="meta">Prepared for: {candidate_name} | Generated: {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <h2 class="section-title">Practice Questions ({len(request.questions)})</h2>
        {questions_html}
        
        {f'<div class="notes-section"><h3>Personal Notes</h3><p>{request.notes}</p></div>' if request.notes else ''}
        
        <div class="footer">
            Generated with MedMatch - AI-Powered Job Search Assistant
        </div>
    </body>
    </html>
    """
    
    return {"html": html, "filename": f"Interview_Prep_{request.company.replace(' ', '_')}.pdf"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== SCHEDULED DIGEST TASK ==============
scheduler = AsyncIOScheduler()

async def scheduled_digest_task():
    """Background task that runs the daily digest for all subscribers"""
    logger.info("🕐 Running scheduled daily digest...")
    
    try:
        # Get all active digest subscribers
        subscribers = await db.digest_settings.find({"is_active": True}, {"_id": 0}).to_list(100)
        
        if not subscribers:
            logger.info("No active subscribers for daily digest")
            return
        
        # Get resume for context
        resume_doc = await db.resumes.find_one({}, {"_id": 0})
        user_name = resume_doc.get('full_name', 'Job Seeker').split()[0] if resume_doc else 'Job Seeker'
        skills = resume_doc.get('skills', []) if resume_doc else []
        
        # Get search queries
        search_strategy = await ai_deep_crawl(skills) if skills else {"search_queries": QUALITY_SEARCH_TERMS}
        search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:8]
        
        # Fetch jobs
        all_jobs = []
        
        # Search Google CSE
        if GOOGLE_API_KEY:
            for query in search_queries[:4]:
                try:
                    google_jobs = await fetch_google_cse_all_sites(query, "Remote")
                    all_jobs.extend(google_jobs)
                except Exception as e:
                    logger.error(f"Google CSE error: {e}")
        
        # Search free APIs
        try:
            api_results = await asyncio.gather(
                fetch_remoteok_jobs("quality", ""),
                fetch_remotive_jobs("quality", ""),
                fetch_jobicy_jobs("quality", ""),
                fetch_arbeitnow_jobs("quality", ""),
                fetch_himalayas_jobs("quality", ""),
                return_exceptions=True
            )
            for result in api_results:
                if isinstance(result, list):
                    all_jobs.extend(result)
        except Exception as e:
            logger.error(f"API fetch error: {e}")
        
        # Filter to last 24 hours
        recent_jobs = filter_jobs_by_date(all_jobs, days=1)
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in recent_jobs:
            key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        sent_count = 0
        
        # Send to each subscriber
        for subscriber in subscribers:
            email = subscriber.get('email')
            if not email:
                continue
            
            # Filter out already-emailed jobs
            new_jobs = await filter_new_jobs(unique_jobs, email)
            
            if not new_jobs:
                logger.info(f"No new jobs for {email}")
                continue
            
            # AI ranking
            relevant_jobs = new_jobs[:20]
            if skills and EMERGENT_LLM_KEY:
                try:
                    relevance_scores = await calculate_job_relevance_batch(new_jobs[:30], skills)
                    for job, score in zip(new_jobs[:30], relevance_scores):
                        job['relevance_score'] = score
                    relevant_jobs = sorted(new_jobs[:30], key=lambda x: x.get('relevance_score', 0), reverse=True)[:20]
                except Exception as e:
                    logger.error(f"Ranking error: {e}")
            
            # Generate and send email
            query_summary = ", ".join(search_queries[:3])
            html_content = generate_digest_email_html(relevant_jobs, user_name, query_summary)
            
            # Mark jobs as emailed
            for job in relevant_jobs:
                await mark_job_emailed(job, email)
            
            success = send_email_gmail(
                email,
                f"🎯 MedMatch Daily Digest: {len(relevant_jobs)} New Quality Jobs",
                html_content
            )
            
            if success:
                sent_count += 1
                await db.digest_settings.update_one(
                    {"email": email},
                    {"$set": {"last_sent": datetime.now(timezone.utc).isoformat()}}
                )
                logger.info(f"✅ Sent digest to {email} ({len(relevant_jobs)} jobs)")
            else:
                logger.error(f"❌ Failed to send digest to {email}")
        
        logger.info(f"📧 Scheduled digest complete: {sent_count}/{len(subscribers)} emails sent")
        
    except Exception as e:
        logger.error(f"Scheduled digest error: {e}")

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts"""
    # Schedule daily digest at 8:00 AM UTC
    scheduler.add_job(
        scheduled_digest_task,
        CronTrigger(hour=8, minute=0),
        id="daily_digest",
        replace_existing=True
    )
    scheduler.start()
    logger.info("📅 Daily digest scheduler started - runs at 8:00 AM UTC")

@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()
