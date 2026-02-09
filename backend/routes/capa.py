"""
CAPA API Routes
Part of Karau Automator

REST API for CAPA (Corrective Action Preventive Action) management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.capa_service import capa_service, CAPAStatus, CAPAType, ActionStatus


router = APIRouter(prefix="/capa", tags=["CAPA System"])


# === PYDANTIC MODELS ===

class CreateCAPARequest(BaseModel):
    title: str = Field(..., description="Brief title of the nonconformance")
    problem_statement: str = Field(..., description="Detailed description of the issue")
    capa_type: str = Field(default="both", description="corrective, preventive, or both")
    severity: str = Field(default="medium", description="critical, high, medium, low")
    source: str = Field(default="", description="Where the issue was identified")
    impacted_processes: List[str] = Field(default=[], description="List of impacted processes")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    assigned_to: str = Field(default="", description="Person assigned to the CAPA")
    created_by: str = Field(default="system", description="Creator of the CAPA")


class RootCauseRequest(BaseModel):
    description: str = Field(..., description="Description of the probable root cause")
    category: str = Field(default="", description="technical, process, human, environmental")
    evidence: str = Field(default="", description="Evidence supporting this cause")
    added_by: str = Field(default="system")


class EliminateCauseRequest(BaseModel):
    reason: str = Field(..., description="Reason for eliminating this cause")
    user: str = Field(default="system")


class RetainCauseRequest(BaseModel):
    justification: str = Field(..., description="Justification for retaining this cause")
    user: str = Field(default="system")


class ContainmentActionRequest(BaseModel):
    description: str = Field(..., description="Description of the containment action")
    addresses_cause_id: Optional[str] = Field(None, description="ID of the cause being addressed")
    responsible: str = Field(default="", description="Person responsible")
    due_date: Optional[str] = Field(None, description="Due date for the action")


class CorrectiveActionRequest(BaseModel):
    description: str = Field(..., description="Description of the corrective action")
    addresses_cause_id: Optional[str] = Field(None)
    how_it_addresses_problem: str = Field(default="", description="How this action addresses the problem")
    how_it_prevents_recurrence: str = Field(default="", description="How this prevents recurrence")
    responsible: str = Field(default="")
    due_date: Optional[str] = Field(None)


class PreventiveActionRequest(BaseModel):
    description: str = Field(..., description="Description of the preventive action")
    addresses_cause_id: Optional[str] = Field(None)
    safeguard_type: str = Field(default="", description="technical, process, training")
    how_it_prevents_future: str = Field(default="", description="How this prevents future occurrence")
    responsible: str = Field(default="")
    due_date: Optional[str] = Field(None)


class CompleteActionRequest(BaseModel):
    notes: str = Field(..., description="Completion notes")
    user: str = Field(default="system")


class VOERequest(BaseModel):
    action_id: str = Field(..., description="ID of the action being verified")
    verification_method: str = Field(..., description="Method of verification")
    acceptance_criteria: str = Field(..., description="Criteria for acceptance")
    test_procedure: str = Field(default="", description="Test procedure to follow")
    impacted_process: str = Field(default="", description="Process being tested")
    responsible: str = Field(default="")
    due_date: Optional[str] = Field(None)


class ExecuteVOERequest(BaseModel):
    result: str = Field(..., description="pass, fail, or partial")
    evidence: str = Field(..., description="Evidence of verification")
    notes: str = Field(default="")
    user: str = Field(default="system")


class AttestVOERequest(BaseModel):
    attestation: str = Field(..., description="Attestation statement")
    attester: str = Field(..., description="Person attesting")


class CloseCAPARequest(BaseModel):
    closure_notes: str = Field(..., description="Notes about closure")
    lessons_learned: str = Field(default="", description="Lessons learned")
    user: str = Field(default="system")


class CloseAtContainmentRequest(BaseModel):
    justification: str = Field(..., description="Justification for closing at containment")
    user: str = Field(default="system")


class UpdateStatusRequest(BaseModel):
    status: str = Field(..., description="New status")
    user: str = Field(default="system")
    notes: str = Field(default="")


# === API ROUTES ===

@router.post("/create")
async def create_capa(request: CreateCAPARequest):
    """Create a new CAPA"""
    try:
        capa = capa_service.create_capa(request.dict())
        return {"success": True, "capa": capa}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_capas(
    status: Optional[str] = Query(None, description="Filter by status"),
    capa_type: Optional[str] = Query(None, description="Filter by type")
):
    """List all CAPAs with optional filters"""
    capas = capa_service.list_capas(status=status, capa_type=capa_type)
    return {"capas": capas, "total": len(capas)}


@router.get("/dashboard")
async def get_dashboard():
    """Get CAPA dashboard summary"""
    return capa_service.get_dashboard_summary()


@router.get("/{capa_id}")
async def get_capa(capa_id: str):
    """Get a specific CAPA by ID"""
    capa = capa_service.get_capa(capa_id)
    if not capa:
        raise HTTPException(status_code=404, detail=f"CAPA {capa_id} not found")
    return capa


@router.put("/{capa_id}/status")
async def update_capa_status(capa_id: str, request: UpdateStatusRequest):
    """Update CAPA status"""
    try:
        capa = capa_service.update_status(
            capa_id, request.status, request.user, request.notes
        )
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# === INVESTIGATION ROUTES ===

@router.post("/{capa_id}/investigation/probable-cause")
async def add_probable_cause(capa_id: str, request: RootCauseRequest):
    """Add a probable root cause"""
    try:
        cause = capa_service.add_probable_cause(capa_id, request.dict())
        return {"success": True, "cause": cause}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{capa_id}/investigation/cause/{cause_id}/eliminate")
async def eliminate_cause(capa_id: str, cause_id: str, request: EliminateCauseRequest):
    """Eliminate a probable cause"""
    try:
        capa = capa_service.eliminate_cause(capa_id, cause_id, request.reason, request.user)
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{capa_id}/investigation/cause/{cause_id}/retain")
async def retain_cause(capa_id: str, cause_id: str, request: RetainCauseRequest):
    """Retain a cause as confirmed root cause"""
    try:
        capa = capa_service.retain_cause(capa_id, cause_id, request.justification, request.user)
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# === CONTAINMENT ROUTES ===

@router.post("/{capa_id}/containment/action")
async def add_containment_action(capa_id: str, request: ContainmentActionRequest):
    """Add a containment action"""
    try:
        action = capa_service.add_containment_action(capa_id, request.dict())
        return {"success": True, "action": action}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{capa_id}/containment/action/{action_id}/complete")
async def complete_containment_action(capa_id: str, action_id: str, request: CompleteActionRequest):
    """Complete a containment action"""
    try:
        capa = capa_service.complete_containment_action(capa_id, action_id, request.notes, request.user)
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{capa_id}/containment/close")
async def close_at_containment(capa_id: str, request: CloseAtContainmentRequest):
    """Close CAPA at containment phase"""
    try:
        capa = capa_service.close_at_containment(capa_id, request.justification, request.user)
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# === RESOLUTION ROUTES ===

@router.post("/{capa_id}/resolution/corrective-action")
async def add_corrective_action(capa_id: str, request: CorrectiveActionRequest):
    """Add a corrective action"""
    try:
        action = capa_service.add_corrective_action(capa_id, request.dict())
        return {"success": True, "action": action}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{capa_id}/resolution/preventive-action")
async def add_preventive_action(capa_id: str, request: PreventiveActionRequest):
    """Add a preventive action"""
    try:
        action = capa_service.add_preventive_action(capa_id, request.dict())
        return {"success": True, "action": action}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{capa_id}/resolution/action/{action_id}/complete")
async def complete_resolution_action(
    capa_id: str, 
    action_id: str, 
    action_type: str = Query(..., description="corrective or preventive"),
    request: CompleteActionRequest = None
):
    """Complete a corrective or preventive action"""
    try:
        capa = capa_service.complete_action(
            capa_id, action_id, action_type, 
            request.notes if request else "", 
            request.user if request else "system"
        )
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# === VOE ROUTES ===

@router.post("/{capa_id}/voe")
async def add_voe(capa_id: str, request: VOERequest):
    """Add a Verification of Effectiveness entry"""
    try:
        voe = capa_service.add_voe(capa_id, request.dict())
        return {"success": True, "voe": voe}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{capa_id}/voe/{voe_id}/execute")
async def execute_voe(capa_id: str, voe_id: str, request: ExecuteVOERequest):
    """Execute a VOE and record results"""
    try:
        capa = capa_service.execute_voe(
            capa_id, voe_id, request.result, request.evidence, request.notes, request.user
        )
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{capa_id}/voe/attest")
async def attest_voe(capa_id: str, request: AttestVOERequest):
    """Attest to VOE completion"""
    try:
        capa = capa_service.attest_voe(capa_id, request.attestation, request.attester)
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# === CLOSURE ROUTES ===

@router.post("/{capa_id}/close")
async def close_capa(capa_id: str, request: CloseCAPARequest):
    """Close the CAPA"""
    try:
        capa = capa_service.close_capa(
            capa_id, request.closure_notes, request.lessons_learned, request.user
        )
        return {"success": True, "capa": capa}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# === AUTOMATOR INTEGRATION ===

@router.post("/automator/create-from-qa")
async def create_capa_from_qa(
    title: str = Query(...),
    problem_statement: str = Query(...),
    source: str = Query(default="Translation QA"),
    severity: str = Query(default="medium")
):
    """Create a CAPA from automated QA findings"""
    capa = capa_service.create_capa({
        "title": title,
        "problem_statement": problem_statement,
        "capa_type": "both",
        "severity": severity,
        "source": source,
        "created_by": "Karau Automator"
    })
    return {"success": True, "capa": capa}
