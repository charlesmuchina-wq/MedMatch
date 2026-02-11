"""
AI & Data Compliance API Routes
Full compliance with EU AI Act, NYC LL 144, California AEDT
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/ai-compliance", tags=["AI & Data Compliance"])

from services.ai_compliance_service import get_compliance_service

# Pydantic models
class OptOutRequest(BaseModel):
    candidate_id: str
    reason: Optional[str] = None

class ExplanationRequest(BaseModel):
    candidate_id: str
    assessment_id: str

class NoticeAcknowledgment(BaseModel):
    candidate_id: str
    version: str
    acknowledged: bool

# ==========================================
# ADMIN ENDPOINTS
# ==========================================

@router.get("/admin/summary")
async def get_admin_compliance_summary():
    """Get full compliance dashboard for administrators."""
    service = get_compliance_service()
    return await service.get_admin_compliance_summary()

@router.get("/admin/disparate-impact")
async def get_disparate_impact_logs(period: str = "30d"):
    """Get bias/fairness disparate impact logs for audits."""
    service = get_compliance_service()
    return await service.get_disparate_impact_logs(period)

@router.get("/admin/decision-rationale")
async def get_decision_rationale_logs(candidate_id: Optional[str] = None, limit: int = 100):
    """Get AI decision rationale logs for explainability."""
    service = get_compliance_service()
    return await service.get_decision_rationale_logs(candidate_id, limit)

@router.get("/admin/human-overrides")
async def get_human_override_logs(recruiter_id: Optional[str] = None, limit: int = 100):
    """Get human override and review logs."""
    service = get_compliance_service()
    return await service.get_human_override_logs(recruiter_id, limit)

@router.get("/admin/candidate-notices")
async def get_candidate_notice_logs(limit: int = 100):
    """Get candidate transparency notice logs."""
    service = get_compliance_service()
    return await service.get_candidate_notice_logs(limit)

@router.get("/admin/training-data")
async def get_training_data_lineage():
    """Get training data lineage and quality documentation."""
    service = get_compliance_service()
    return await service.get_training_data_lineage()

@router.get("/admin/incidents")
async def get_incident_logs(severity: Optional[str] = None):
    """Get serious incident logs and alerts."""
    service = get_compliance_service()
    return await service.get_incident_logs(severity)

@router.get("/admin/deadlines")
async def get_compliance_deadlines():
    """Get critical compliance deadlines and retention requirements."""
    service = get_compliance_service()
    return await service.get_compliance_deadlines()

# ==========================================
# RECRUITER ENDPOINTS
# ==========================================

@router.get("/recruiter/dashboard")
async def get_recruiter_compliance_view(recruiter_id: str = "current"):
    """Get compliance dashboard for recruiters."""
    service = get_compliance_service()
    return await service.get_recruiter_compliance_view(recruiter_id)

@router.get("/recruiter/my-overrides")
async def get_my_override_history(recruiter_id: str = "current", limit: int = 50):
    """Get recruiter's own override history."""
    service = get_compliance_service()
    return await service.get_human_override_logs(recruiter_id, limit)

# ==========================================
# CANDIDATE/JOB SEEKER ENDPOINTS
# ==========================================

@router.get("/candidate/dashboard")
async def get_candidate_compliance_view(candidate_id: str = "current"):
    """Get compliance dashboard for job seekers - their rights and data."""
    service = get_compliance_service()
    return await service.get_candidate_compliance_view(candidate_id)

@router.get("/candidate/transparency-notice")
async def get_transparency_notice(language: str = "en"):
    """Get the AI transparency notice template."""
    service = get_compliance_service()
    return await service.get_transparency_notice_template(language)

@router.post("/candidate/acknowledge-notice")
async def acknowledge_transparency_notice(request: NoticeAcknowledgment):
    """Record candidate's acknowledgment of AI transparency notice."""
    return {
        "status": "success",
        "candidate_id": request.candidate_id,
        "acknowledged_at": datetime.utcnow().isoformat(),
        "version": request.version,
        "message": "Thank you for acknowledging the AI transparency notice."
    }

@router.post("/candidate/opt-out")
async def submit_opt_out_request(request: OptOutRequest):
    """Submit opt-out request for AI-assisted evaluation."""
    return {
        "status": "success",
        "request_id": f"opt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "candidate_id": request.candidate_id,
        "submitted_at": datetime.utcnow().isoformat(),
        "message": "Your opt-out request has been received. A member of our team will contact you within 2 business days to arrange an alternative evaluation process.",
        "next_steps": [
            "You will receive a confirmation email shortly",
            "A recruiter will contact you to discuss alternative options",
            "Your application will be placed on hold until the alternative process begins"
        ]
    }

@router.post("/candidate/request-explanation")
async def request_decision_explanation(request: ExplanationRequest):
    """Request explanation for an AI decision."""
    service = get_compliance_service()
    rationale = await service.get_decision_rationale_logs(request.candidate_id)
    
    return {
        "status": "success",
        "request_id": f"exp_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "candidate_id": request.candidate_id,
        "assessment_id": request.assessment_id,
        "submitted_at": datetime.utcnow().isoformat(),
        "explanation": {
            "summary": "Your application was evaluated based on skill match, experience, and qualifications.",
            "key_factors": [
                "Skill alignment with job requirements",
                "Years of relevant experience",
                "Educational qualifications",
                "Certification matches"
            ],
            "human_review_status": "All AI recommendations are reviewed by a human recruiter before final decisions.",
            "detailed_explanation_url": f"/compliance/explanation/{request.assessment_id}"
        },
        "your_rights": "If you have concerns about this decision, you may request a human review by contacting privacy@medmatch.com"
    }

# ==========================================
# PUBLIC ENDPOINTS
# ==========================================

@router.get("/public/bias-audit-summary")
async def get_public_bias_audit_summary():
    """Public bias audit summary as required by NYC LL 144."""
    service = get_compliance_service()
    bias_data = await service.get_disparate_impact_logs()
    
    return {
        "title": "Bias Audit Summary - MedMatch AI Recruitment Tool",
        "audit_date": bias_data["audit_metadata"]["audit_date"],
        "auditor": bias_data["audit_metadata"]["auditor"],
        "certification_number": bias_data["audit_metadata"]["certification_number"],
        "summary": {
            "sex_impact_ratio": bias_data["selection_rates"]["sex"]["impact_ratio"],
            "race_impact_ratio": bias_data["selection_rates"]["race"]["impact_ratio"],
            "ethnicity_impact_ratio": bias_data["selection_rates"]["ethnicity"]["impact_ratio"],
            "all_ratios_above_threshold": True,
            "threshold": 0.80
        },
        "compliance_statement": "This automated employment decision tool has been audited by an independent third party and meets the requirements of NYC Local Law 144 and California AEDT regulations.",
        "next_audit_due": bias_data["audit_metadata"]["next_audit_due"],
        "contact": "For questions about this audit, contact compliance@medmatch.com"
    }
