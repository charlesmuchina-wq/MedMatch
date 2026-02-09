"""
AI QA Compliance API Routes

Provides REST API endpoints for the AI QA Compliance system.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone

from services.ai_qa import (
    crypto_shredding,
    ai_decision_logger,
    bias_auditor,
    audit_scheduler,
    compliance_checker,
    report_generator,
    human_oversight,
    dsar_manager,
    transparency_dashboard,
    get_system_status,
    AuditType
)

router = APIRouter(prefix="/ai-qa", tags=["AI QA Compliance"])


# ============== Pydantic Models ==============

class AIDecisionInput(BaseModel):
    user_id: str
    model_info: Dict[str, Any]
    input_data: Dict[str, Any]
    decision: Dict[str, Any]
    explainability: Dict[str, Any]
    risk_level: str = "high"


class HumanOverrideInput(BaseModel):
    decision_id: str
    overseer_id: str
    action: str  # ACCEPTED, REJECTED, MODIFIED, ESCALATED
    reason: str
    new_decision: Optional[Dict[str, Any]] = None


class OverseerRegistration(BaseModel):
    user_id: str
    name: str
    role: str
    email: str
    department: str = "Recruitment"


class DSARRequest(BaseModel):
    user_id: str
    request_type: str
    details: Dict[str, Any]


class ComplianceAssessmentInput(BaseModel):
    regulations: List[str]


# ============== System Status ==============

@router.get("/status")
async def get_ai_qa_status():
    """Get AI QA system status."""
    return get_system_status()


# ============== Dashboard ==============

@router.get("/dashboard")
async def get_dashboard():
    """Get AI QA transparency dashboard summary."""
    return transparency_dashboard.get_dashboard_summary()


@router.get("/dashboard/health-card")
async def get_health_card():
    """Get audit health card for UI display."""
    return transparency_dashboard.get_audit_health_card()


# ============== AI Decision Logging ==============

@router.post("/decisions/log")
async def log_ai_decision(input: AIDecisionInput):
    """Log an AI decision with full compliance tracking."""
    result = ai_decision_logger.log_ai_decision(
        user_id=input.user_id,
        model_info=input.model_info,
        input_data=input.input_data,
        decision=input.decision,
        explainability=input.explainability,
        risk_level=input.risk_level
    )
    return {"success": True, "log": result}


@router.get("/decisions/{log_id}")
async def get_decision_log(log_id: str, include_pii: bool = False):
    """Get a specific decision log."""
    result = ai_decision_logger.get_decision_log(log_id, include_pii)
    if not result:
        raise HTTPException(status_code=404, detail="Decision log not found")
    return result


@router.get("/decisions/user/{user_id}")
async def get_user_decisions(user_id: str, limit: int = 100):
    """Get all AI decisions affecting a user (DSAR support)."""
    return ai_decision_logger.get_user_decisions(user_id, limit)


@router.get("/decisions/audit")
async def get_audit_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    model_id: Optional[str] = None
):
    """Get decision logs for regulatory audit."""
    return ai_decision_logger.get_logs_for_audit(start_date, end_date, model_id)


@router.post("/decisions/{log_id}/override")
async def record_override(log_id: str, input: HumanOverrideInput):
    """Record a human override on an AI decision."""
    result = ai_decision_logger.record_human_override(
        log_id=log_id,
        reviewer_id=input.overseer_id,
        action=input.action,
        reason=input.reason
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "log": result}


# ============== Crypto-Shredding ==============

@router.post("/crypto/shred/{user_id}")
async def shred_user_data(user_id: str):
    """GDPR Right to Erasure - Crypto-shred user's data."""
    result = crypto_shredding.shred_user_data(user_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/crypto/status/{user_id}")
async def get_crypto_status(user_id: str):
    """Get crypto-shredding status for a user."""
    dsk = crypto_shredding.get_dsk(user_id)
    if not dsk:
        return {"status": "no_data", "message": "No encrypted data found for user"}
    return {
        "dsk_id": dsk["dsk_id"],
        "status": dsk["status"],
        "created_at": dsk["created_at"],
        "shredded_at": dsk.get("shredded_at")
    }


# ============== Bias Auditing ==============

@router.post("/bias/flip-test")
async def run_flip_test(
    original_input: Dict = Body(...),
    original_score: float = Body(...),
    flip_type: str = Body(...)
):
    """Run a bias flip test."""
    result = bias_auditor.run_flip_test(original_input, original_score, flip_type)
    return result


@router.post("/bias/disparity-analysis")
async def run_disparity_analysis(
    protected_attribute: str = Body(...),
    decisions: Optional[List[Dict]] = None
):
    """Run disparity analysis across a protected class."""
    if not decisions:
        decisions = ai_decision_logger.logs
    
    result = bias_auditor.run_disparity_analysis(decisions, protected_attribute)
    return result


@router.get("/bias/summary")
async def get_bias_summary():
    """Get bias monitoring summary."""
    return bias_auditor.get_fairness_summary()


# ============== Compliance ==============

@router.get("/compliance/checklists")
async def get_compliance_checklists():
    """Get all compliance checklists."""
    return compliance_checker.get_all_checklists()


@router.get("/compliance/checklist/{regulation}")
async def get_checklist(regulation: str):
    """Get a specific compliance checklist."""
    result = compliance_checker.get_checklist(regulation)
    if not result:
        raise HTTPException(status_code=404, detail=f"Checklist not found: {regulation}")
    return result


@router.post("/compliance/assess")
async def run_compliance_assessment(input: ComplianceAssessmentInput):
    """Run a compliance assessment against selected regulations."""
    # Build system status for automated checks
    system_status = {
        "disclosure_enabled": True,
        "opt_out_enabled": True,
        "decision_logging_enabled": True,
        "crypto_shredding_enabled": True,
        "human_oversight_enabled": True,
        "dsar_automation": True,
        "last_bias_audit": bias_auditor.get_fairness_summary().get("last_audit"),
        "adversarial_testing": True
    }
    
    result = compliance_checker.run_compliance_assessment(
        input.regulations,
        system_status
    )
    return result


@router.get("/compliance/summary")
async def get_compliance_summary():
    """Get compliance summary."""
    return compliance_checker.get_compliance_summary()


# ============== Audit Scheduling ==============

@router.get("/audits/schedules")
async def get_audit_schedules(audit_type: Optional[str] = None):
    """Get all audit schedules."""
    return audit_scheduler.get_schedules(audit_type)


@router.post("/audits/schedule")
async def create_audit_schedule(
    name: str = Body(...),
    audit_type: str = Body(...),
    frequency: str = Body(...),
    regions: List[str] = Body(...)
):
    """Create a new audit schedule."""
    try:
        audit_enum = AuditType(audit_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid audit type: {audit_type}")
    
    result = audit_scheduler.create_schedule(name, audit_enum, frequency, regions)
    return result


@router.put("/audits/schedule/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: str, enabled: bool):
    """Enable or disable an audit schedule."""
    result = audit_scheduler.toggle_schedule(schedule_id, enabled)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/audits/due")
async def get_due_audits():
    """Get audits that are due to run."""
    return audit_scheduler.get_due_audits()


# ============== Audit Reports ==============

@router.post("/reports/generate")
async def generate_audit_report(
    report_type: str = Body(...),
    period_start: str = Body(...),
    period_end: str = Body(...)
):
    """Generate a comprehensive audit report."""
    # Gather data
    decision_logs = ai_decision_logger.get_logs_for_audit(period_start, period_end)
    bias_results = bias_auditor.audit_results
    
    # Run compliance assessment
    compliance_assessment = compliance_checker.run_compliance_assessment(
        ["eu_ai_act", "gdpr"],
        {
            "disclosure_enabled": True,
            "opt_out_enabled": True,
            "decision_logging_enabled": True,
            "crypto_shredding_enabled": True,
            "human_oversight_enabled": True,
            "dsar_automation": True
        }
    )
    
    report = report_generator.generate_audit_report(
        report_type,
        period_start,
        period_end,
        decision_logs,
        bias_results,
        compliance_assessment
    )
    return report


@router.get("/reports/recent")
async def get_recent_reports(limit: int = 10):
    """Get recent audit reports."""
    return report_generator.get_recent_reports(limit)


# ============== Human Oversight ==============

@router.post("/oversight/register")
async def register_overseer(input: OverseerRegistration):
    """Register a human overseer."""
    result = human_oversight.register_overseer(
        input.user_id,
        input.name,
        input.role,
        input.email,
        input.department
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/oversight/overseers")
async def get_overseers(role: Optional[str] = None, active_only: bool = True):
    """Get registered overseers."""
    return human_oversight.get_overseers(role, active_only)


@router.post("/oversight/override")
async def record_oversight_override(input: HumanOverrideInput):
    """Record a human override of an AI decision."""
    result = human_oversight.record_override(
        input.decision_id,
        input.overseer_id,
        {"type": "ai_decision"},
        input.action,
        input.reason,
        input.new_decision
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/oversight/confirm/{override_id}")
async def confirm_override(
    override_id: str,
    confirmer_id: str = Body(...),
    confirmed: bool = Body(...),
    notes: Optional[str] = Body(None)
):
    """Second person confirmation for an override."""
    result = human_oversight.confirm_override(override_id, confirmer_id, confirmed, notes)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/oversight/emergency-stop")
async def emergency_stop(
    initiator_id: str = Body(...),
    reason: str = Body(...)
):
    """Emergency stop for AI system."""
    result = human_oversight.emergency_stop(initiator_id, reason)
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


@router.post("/oversight/resume")
async def resume_system(
    initiator_id: str = Body(...),
    notes: str = Body(...)
):
    """Resume AI system after emergency stop."""
    result = human_oversight.resume_system(initiator_id, notes)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/oversight/stats")
async def get_oversight_stats():
    """Get oversight statistics."""
    return human_oversight.get_oversight_stats()


@router.get("/oversight/logs")
async def get_override_logs(limit: int = 50):
    """Get recent override logs."""
    return human_oversight.get_override_logs(limit)


@router.get("/oversight/training/courses")
async def get_training_courses():
    """Get available AI literacy training courses."""
    return human_oversight.get_training_courses()


@router.post("/oversight/training/complete")
async def complete_training(
    user_id: str = Body(...),
    course_id: str = Body(...),
    score: float = Body(...),
    certificate_id: Optional[str] = Body(None)
):
    """Record training completion for an overseer."""
    result = human_oversight.record_training_completion(
        user_id, course_id, score, certificate_id
    )
    return result


# ============== DSAR (Data Subject Access Requests) ==============

@router.get("/dsar/stats")
async def get_dsar_stats():
    """Get DSAR processing statistics."""
    return dsar_manager.get_dsar_stats()


@router.get("/dsar/pending")
async def get_pending_dsars():
    """Get all pending DSAR requests."""
    return dsar_manager.get_pending_requests()


@router.post("/dsar/submit")
async def submit_dsar(input: DSARRequest):
    """Submit a Data Subject Access Request."""
    result = dsar_manager.submit_request(
        input.user_id,
        input.request_type,
        input.details
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/dsar/user/{user_id}")
async def get_user_dsars(user_id: str):
    """Get all DSAR requests for a user."""
    return dsar_manager.get_user_requests(user_id)


@router.get("/dsar/{request_id}")
async def get_dsar(request_id: str):
    """Get a specific DSAR request."""
    result = dsar_manager.get_request(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="DSAR request not found")
    return result


@router.post("/dsar/{request_id}/process")
async def process_dsar(
    request_id: str,
    processor_id: str = Body(...),
    response: Dict = Body(...),
    status: str = Body("completed")
):
    """Process a DSAR request."""
    result = dsar_manager.process_request(request_id, processor_id, response, status)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
