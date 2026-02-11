"""
Global AI Compliance API Routes
Full 2026 Global Coverage: EU, UK, US, Canada, Singapore, China, South Korea, Japan, Brazil, Africa, ASEAN
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

router = APIRouter(prefix="/global-compliance", tags=["Global AI Compliance"])

from services.global_compliance_service import get_global_compliance_service

# Pydantic models
class GUALRequest(BaseModel):
    candidate_location: str
    employer_location: str
    action_type: str = "AI_RANKING_DECISION"
    user_id: str
    input_data_hash: str
    output_score: float
    contributing_factors: List[str]
    bias_check_passed: bool = True

class ExplanationReportRequest(BaseModel):
    candidate_id: str
    assessment_id: str

# ==========================================
# GLOBAL UNIFIED AUDIT LOG (GUAL)
# ==========================================

@router.post("/gual/create")
async def create_gual_entry(request: GUALRequest):
    """Create a Global Unified Audit Log entry for cross-border compliance."""
    service = get_global_compliance_service()
    return await service.create_gual_entry(
        candidate_location=request.candidate_location,
        employer_location=request.employer_location,
        action_type=request.action_type,
        user_id=request.user_id,
        agent_id="recruitment_model_v4.2.1",
        input_data_hash=request.input_data_hash,
        output_score=request.output_score,
        contributing_factors=request.contributing_factors,
        bias_check_passed=request.bias_check_passed
    )

# ==========================================
# ASIA-PACIFIC ENDPOINTS
# ==========================================

@router.get("/asia-pacific/singapore")
async def get_singapore_compliance():
    """Singapore Workplace Fairness Act & AI Verify compliance."""
    service = get_global_compliance_service()
    return await service.get_singapore_compliance()

@router.get("/asia-pacific/china")
async def get_china_compliance():
    """China PIPL, Algorithm Filing, Synthetic Content compliance."""
    service = get_global_compliance_service()
    return await service.get_china_compliance()

@router.get("/asia-pacific/south-korea")
async def get_south_korea_compliance():
    """South Korea AI Basic Act compliance."""
    service = get_global_compliance_service()
    return await service.get_south_korea_compliance()

@router.get("/asia-pacific/japan")
async def get_japan_compliance():
    """Japan AI Strategy Headquarters guidelines."""
    service = get_global_compliance_service()
    return await service.get_japan_compliance()

@router.get("/asia-pacific/asean")
async def get_asean_compliance():
    """ASEAN AI Governance and Ethics Guide compliance."""
    service = get_global_compliance_service()
    return await service.get_asean_compliance()

# ==========================================
# NORTH AMERICA ENDPOINTS
# ==========================================

@router.get("/north-america/canada")
async def get_canada_compliance():
    """Canada AIDA and Ontario ESA Amendment compliance."""
    service = get_global_compliance_service()
    return await service.get_canada_compliance()

@router.get("/north-america/colorado")
async def get_colorado_compliance():
    """Colorado AI Act (SB 205) compliance."""
    service = get_global_compliance_service()
    return await service.get_colorado_compliance()

# ==========================================
# SOUTH AMERICA & AFRICA ENDPOINTS
# ==========================================

@router.get("/south-america/brazil")
async def get_brazil_compliance():
    """Brazil Bill 2338/2023 and LGPD compliance."""
    service = get_global_compliance_service()
    return await service.get_brazil_compliance()

@router.get("/africa")
async def get_africa_compliance():
    """African Union AI Strategy and regional compliance."""
    service = get_global_compliance_service()
    return await service.get_africa_compliance()

# ==========================================
# AUTO-REPORT GENERATION
# ==========================================

@router.get("/reports/annual-bias-audit")
async def generate_annual_bias_audit():
    """Generate annual bias audit report for NYC LL 144 / California AEDT filing."""
    service = get_global_compliance_service()
    return await service.generate_annual_bias_audit_report()

@router.get("/reports/eu-technical-file")
async def generate_eu_technical_file():
    """Generate EU AI Act Technical Documentation for regulatory authorities."""
    service = get_global_compliance_service()
    return await service.generate_regulatory_technical_file()

@router.post("/reports/candidate-explanation")
async def generate_candidate_explanation(request: ExplanationReportRequest):
    """Generate automated explanation report for candidate (GDPR/AEDT)."""
    service = get_global_compliance_service()
    return await service.generate_candidate_explanation_report(
        request.candidate_id, 
        request.assessment_id
    )

# ==========================================
# INCIDENT & MONITORING
# ==========================================

@router.get("/incidents/check")
async def check_incident_alerts():
    """Check for incidents requiring 96-hour regulatory reporting."""
    service = get_global_compliance_service()
    return await service.check_incident_alerts()

# ==========================================
# GLOBAL SUMMARY
# ==========================================

@router.get("/summary")
async def get_global_compliance_summary():
    """Get comprehensive global compliance status across all regions."""
    service = get_global_compliance_service()
    return await service.get_global_compliance_summary()
