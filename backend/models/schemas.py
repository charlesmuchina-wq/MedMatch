"""
Shared Pydantic Models
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any


# ============== Authentication Models ==============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "job_seeker"


class LoginRequest(BaseModel):
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


# ============== Job Models ==============

class JobSearchRequest(BaseModel):
    query: str
    location: str = "Remote"
    job_type: str = "fulltime"


class SaveJobRequest(BaseModel):
    job: Dict[str, Any]


class ManualJobRequest(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    description: str = ""
    url: str = ""
    salary: str = ""


# ============== Application Models ==============

class ApplicationRequest(BaseModel):
    job: Dict[str, Any]
    status: str = "Applied"
    notes: str = ""


class QuickApplyRequest(BaseModel):
    job: Dict[str, Any]


class UpdateApplicationRequest(BaseModel):
    status: str


class UpdateJobStatusRequest(BaseModel):
    job_status: str


# ============== AI Feature Models ==============

class CoverLetterRequest(BaseModel):
    job: Dict[str, Any]
    tone: str = "professional"
    custom_points: List[str] = []


class PredictCallbackRequest(BaseModel):
    job: Dict[str, Any]


class InterviewQuestionsRequest(BaseModel):
    job_title: str
    company: str
    job_description: str = ""
    question_types: List[str] = ["behavioral", "technical", "situational"]


class VoiceFeedbackRequest(BaseModel):
    question: str
    answer: str
    job_title: str
    company: str


class VideoFeedbackRequest(BaseModel):
    question: str
    answer: str
    job_title: str
    company: str
    video_data: Optional[str] = None


# ============== Alert Models ==============

class AlertRequest(BaseModel):
    query: str
    email: str


class DigestSettingsRequest(BaseModel):
    email: EmailStr
    enabled: bool = True
    job_types: List[str] = ["remote", "hybrid"]
    keywords: List[str] = []
    excluded_keywords: List[str] = []
    min_salary: Optional[int] = None
    locations: List[str] = ["Remote"]


# ============== Payment Models ==============

class CheckoutRequest(BaseModel):
    success_url: str
    cancel_url: str


class PayPalCreateRequest(BaseModel):
    return_url: str
    cancel_url: str


class PayPalExecuteRequest(BaseModel):
    payment_id: str
    payer_id: str


# ============== Recruiter Models ==============

class RecruiterJobRequest(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: str = ""
    tags: List[str] = []


# ============== Resume Profile Models ==============

class ResumeProfileRequest(BaseModel):
    name: str
    is_default: bool = False
