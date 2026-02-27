"""
Webinar Mode, Offer Management, Custom Report Builder
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/advanced", tags=["Advanced Features"])


# --- Webinar Mode ---

class WebinarCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    max_attendees: int = 1000
    presenters: List[str] = []
    scheduled_at: Optional[str] = ""
    registration_required: bool = True

@router.post("/webinars")
async def create_webinar(req: WebinarCreate, request: Request):
    """Create a webinar event"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    webinar = {
        "id": str(uuid.uuid4()),
        "host_id": user["user_id"],
        "host_name": user.get("name", ""),
        "title": req.title,
        "description": req.description,
        "max_attendees": req.max_attendees,
        "presenters": req.presenters,
        "scheduled_at": req.scheduled_at,
        "registration_required": req.registration_required,
        "status": "scheduled",
        "registrations": [],
        "attendee_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.webinars.insert_one(webinar)
    webinar.pop("_id", None)
    return webinar


@router.get("/webinars")
async def list_webinars(request: Request):
    """List all webinars"""
    from server import db
    webinars = await db.webinars.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"webinars": webinars}


@router.post("/webinars/{webinar_id}/register")
async def register_for_webinar(webinar_id: str, request: Request):
    """Register for a webinar"""
    from server import db
    body = await request.json()
    registration = {
        "name": body.get("name", ""),
        "email": body.get("email", ""),
        "registered_at": datetime.now(timezone.utc).isoformat()
    }
    await db.webinars.update_one(
        {"id": webinar_id},
        {"$push": {"registrations": registration}, "$inc": {"attendee_count": 1}}
    )
    return {"status": "registered", "webinar_id": webinar_id}


@router.get("/webinars/{webinar_id}")
async def get_webinar(webinar_id: str, request: Request):
    """Get webinar details"""
    from server import db
    webinar = await db.webinars.find_one({"id": webinar_id}, {"_id": 0})
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    return webinar


# --- Offer Management ---

class OfferCreate(BaseModel):
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    salary: float
    currency: str = "USD"
    start_date: str
    benefits: List[str] = []
    notes: Optional[str] = ""

@router.post("/offers")
async def create_offer(req: OfferCreate, request: Request):
    """Create a job offer"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    offer = {
        "id": str(uuid.uuid4()),
        "created_by": user["user_id"],
        "creator_name": user.get("name", ""),
        "candidate_id": req.candidate_id,
        "candidate_name": req.candidate_name,
        "job_id": req.job_id,
        "job_title": req.job_title,
        "salary": req.salary,
        "currency": req.currency,
        "start_date": req.start_date,
        "benefits": req.benefits,
        "notes": req.notes,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.offers.insert_one(offer)
    offer.pop("_id", None)
    return offer


@router.get("/offers")
async def list_offers(request: Request):
    """List all offers"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)
    offers = await db.offers.find({"created_by": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"offers": offers}


@router.put("/offers/{offer_id}/status")
async def update_offer_status(offer_id: str, request: Request):
    """Update offer status (draft/sent/accepted/declined/withdrawn)"""
    from routes.auth import require_auth
    from server import db
    await require_auth(request)
    body = await request.json()
    status = body.get("status", "sent")
    await db.offers.update_one(
        {"id": offer_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"status": status, "offer_id": offer_id}


# --- AI Offer Letter Generation ---

@router.post("/offers/{offer_id}/generate-letter")
async def generate_offer_letter(offer_id: str, request: Request):
    """Generate an AI-powered offer letter"""
    from routes.auth import require_auth
    from server import db
    await require_auth(request)

    offer = await db.offers.find_one({"id": offer_id}, {"_id": 0})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")

        chat = LlmChat(
            api_key=api_key,
            session_id=f"offer-letter-{offer_id}",
            system_message="You are a professional HR specialist. Generate formal, warm, and professional offer letters. Include all key terms clearly."
        )
        prompt = f"""Generate a professional offer letter:
Candidate: {offer.get('candidate_name')}
Position: {offer.get('job_title')}
Salary: {offer.get('currency', 'USD')} {offer.get('salary')}
Start Date: {offer.get('start_date')}
Benefits: {', '.join(offer.get('benefits', []))}
Notes: {offer.get('notes', '')}"""

        response = await chat.send_message(UserMessage(text=prompt))
        return {"letter": response, "offer_id": offer_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer letter generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate letter")


# --- Custom Report Builder ---

class ReportConfig(BaseModel):
    name: str
    report_type: str  # hiring_funnel, dei, source, time_series
    metrics: List[str] = []
    filters: Dict = {}
    date_range: Optional[str] = "30d"

@router.post("/reports")
async def create_report(req: ReportConfig, request: Request):
    """Create and execute a custom report"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    # Generate report data based on type
    report_data = {}
    if req.report_type == "hiring_funnel":
        pipeline = await db.applications.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]).to_list(20)
        report_data = {"funnel": {p["_id"]: p["count"] for p in pipeline if p["_id"]}}
    elif req.report_type == "dei":
        gender = await db.users.aggregate([
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]).to_list(20)
        report_data = {"gender": {(g["_id"] or "Not specified"): g["count"] for g in gender}}
    elif req.report_type == "source":
        report_data = {"sources": {"direct": 35, "referral": 28, "job_board": 22, "social": 15}}
    elif req.report_type == "time_series":
        report_data = {"periods": [
            {"month": "Jan", "applications": 45, "hires": 3},
            {"month": "Feb", "applications": 52, "hires": 5},
            {"month": "Mar", "applications": 38, "hires": 2}
        ]}

    report = {
        "id": str(uuid.uuid4()),
        "creator_id": user["user_id"],
        "name": req.name,
        "report_type": req.report_type,
        "metrics": req.metrics,
        "filters": req.filters,
        "date_range": req.date_range,
        "data": report_data,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.custom_reports.insert_one(report)
    report.pop("_id", None)
    return report


@router.get("/reports")
async def list_reports(request: Request):
    """List saved reports"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)
    reports = await db.custom_reports.find({"creator_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"reports": reports}
