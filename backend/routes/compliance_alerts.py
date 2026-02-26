"""
Compliance Alerts & GUAL API Routes
Real-time compliance monitoring and Global Unified Audit Log endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone

from routes.auth import get_current_user, require_auth
from utils.database import db
from services.compliance_alerts import get_compliance_alert_service, ComplianceAlertService
from services.gual_integration import get_gual_service, GUALIntegrationService

router = APIRouter(prefix="/compliance-alerts", tags=["Compliance Alerts"])


# ============== Pydantic Models ==============

class LocationUpdate(BaseModel):
    location_code: str


class HiringDecisionLog(BaseModel):
    action_type: str
    candidate_id: str
    ai_score: float
    contributing_factors: List[str]
    decision_outcome: str
    candidate_location: Optional[str] = None
    employer_location: Optional[str] = None
    additional_data: Optional[Dict] = None


class HumanReviewComplete(BaseModel):
    decision: str  # "APPROVED" or "REJECTED" or "OVERRIDE"
    notes: Optional[str] = None


# ============== Alert Endpoints ==============

@router.get("/check")
async def check_compliance(request: Request):
    """
    Run all compliance checks and return any new alerts.
    Creates in-app notifications for critical issues.
    """
    user = await require_auth(request)
    
    # Initialize services with database
    alert_service = get_compliance_alert_service(db)
    if not alert_service:
        # Fallback initialization
        alert_service = ComplianceAlertService(db)
    
    # Run compliance checks
    result = await alert_service.check_all_compliance(user["user_id"])
    
    return result


@router.get("/active")
async def get_active_alerts(request: Request):
    """Get all active (unacknowledged) compliance alerts."""
    user = await require_auth(request)
    
    alert_service = get_compliance_alert_service(db)
    if not alert_service:
        alert_service = ComplianceAlertService(db)
    
    alerts = await alert_service.get_active_alerts(user["user_id"])
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "has_critical": any(a["severity"] == "CRITICAL" for a in alerts)
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, request: Request):
    """Mark an alert as acknowledged."""
    user = await require_auth(request)
    
    alert_service = get_compliance_alert_service(db)
    if not alert_service:
        alert_service = ComplianceAlertService(db)
    
    success = await alert_service.acknowledge_alert(alert_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert acknowledged", "alert_id": alert_id}


# ============== GUAL Endpoints ==============

@router.post("/gual/log")
async def log_hiring_decision(decision: HiringDecisionLog, request: Request):
    """
    Log an AI-assisted hiring decision to the Global Unified Audit Log.
    Automatically determines applicable laws based on jurisdictions.
    """
    user = await require_auth(request)
    
    gual_service = get_gual_service(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    result = await gual_service.log_hiring_decision(
        action_type=decision.action_type,
        candidate_id=decision.candidate_id,
        employer_id=user["user_id"],
        ai_score=decision.ai_score,
        contributing_factors=decision.contributing_factors,
        decision_outcome=decision.decision_outcome,
        candidate_location=decision.candidate_location,
        employer_location=decision.employer_location,
        additional_data=decision.additional_data
    )
    
    return result


@router.get("/gual/entries")
async def get_gual_entries(
    request: Request,
    candidate_id: Optional[str] = None,
    action_type: Optional[str] = None,
    limit: int = 100
):
    """Get GUAL entries with optional filters."""
    user = await require_auth(request)
    
    gual_service = get_gual_service(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    entries = await gual_service.get_gual_entries(
        candidate_id=candidate_id,
        employer_id=user["user_id"],
        action_type=action_type,
        limit=limit
    )
    
    return {
        "entries": entries,
        "count": len(entries)
    }


@router.get("/gual/pending-reviews")
async def get_pending_reviews(request: Request):
    """Get GUAL entries pending human review."""
    user = await require_auth(request)
    
    gual_service = get_gual_service(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    entries = await gual_service.get_pending_reviews(user["user_id"])
    
    return {
        "pending_reviews": entries,
        "count": len(entries)
    }


@router.post("/gual/{audit_event_id}/review")
async def complete_review(
    audit_event_id: str,
    review: HumanReviewComplete,
    request: Request
):
    """Complete human review for a GUAL entry."""
    user = await require_auth(request)
    
    gual_service = get_gual_service(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    success = await gual_service.complete_human_review(
        audit_event_id=audit_event_id,
        reviewer_id=user["user_id"],
        decision=review.decision,
        notes=review.notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="GUAL entry not found")
    
    return {"message": "Review completed", "audit_event_id": audit_event_id}


# ============== Location Management ==============

@router.post("/location/update")
async def update_user_location(location: LocationUpdate, request: Request):
    """Update user's location for jurisdiction detection."""
    user = await require_auth(request)
    
    gual_service = get_gual_service(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    success = await gual_service.update_user_location(
        user_id=user["user_id"],
        location_code=location.location_code
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update location")
    
    return {
        "message": "Location updated",
        "location_code": location.location_code
    }


@router.get("/location/pending-prompts")
async def get_pending_location_prompts(request: Request):
    """Check if user needs to provide location information."""
    user = await require_auth(request)
    
    # Check if user has location set
    user_doc = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"location_code": 1}
    )
    
    has_location = bool(user_doc and user_doc.get("location_code"))
    
    # Check for pending prompts
    pending_count = await db.location_prompts.count_documents({
        "$or": [
            {"candidate_id": user["user_id"]},
            {"employer_id": user["user_id"]}
        ],
        "resolved": False
    })
    
    return {
        "has_location": has_location,
        "current_location": user_doc.get("location_code") if user_doc else None,
        "pending_prompts": pending_count,
        "prompt_required": not has_location and pending_count > 0
    }


# ============== Summary Endpoint ==============

@router.get("/summary")
async def get_compliance_summary(request: Request):
    """Get comprehensive compliance status summary."""
    user = await require_auth(request)
    
    alert_service = get_compliance_alert_service(db)
    gual_service = get_gual_service(db)
    
    if not alert_service:
        alert_service = ComplianceAlertService(db)
    if not gual_service:
        gual_service = GUALIntegrationService(db)
    
    # Get alert counts
    active_alerts = await alert_service.get_active_alerts(user["user_id"])
    
    # Get GUAL stats
    total_entries = await db.gual_log.count_documents({})
    pending_reviews = await db.gual_log.count_documents({
        "human_oversight.review_status": "PENDING"
    })
    
    # Get location status
    user_doc = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"location_code": 1}
    )
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alerts": {
            "total_active": len(active_alerts),
            "critical": len([a for a in active_alerts if a["severity"] == "CRITICAL"]),
            "high": len([a for a in active_alerts if a["severity"] == "HIGH"]),
            "medium": len([a for a in active_alerts if a["severity"] == "MEDIUM"])
        },
        "gual": {
            "total_entries": total_entries,
            "pending_reviews": pending_reviews
        },
        "user_status": {
            "location_set": bool(user_doc and user_doc.get("location_code")),
            "location_code": user_doc.get("location_code") if user_doc else None
        },
        "compliance_status": "COMPLIANT" if len([a for a in active_alerts if a["severity"] == "CRITICAL"]) == 0 else "ACTION_REQUIRED"
    }
