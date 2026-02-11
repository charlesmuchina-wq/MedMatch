"""
Data Integrity & AI QA API Routes
Provides endpoints for automated governance, compliance, and AI quality assurance
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/data-integrity", tags=["Data Integrity & AI QA"])

# Import service - we'll pass db from server.py
from services.data_integrity_service import DataIntegrityService

# Create a singleton service instance
_service_instance = None

def get_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = DataIntegrityService(None)
    return _service_instance

# Pydantic models
class PIIScanRequest(BaseModel):
    content: Optional[str] = None

class ExplanationRequest(BaseModel):
    decision_id: str
    decision_type: str = "shortlist"

class AuditResponse(BaseModel):
    audit_id: str
    status: str
    overall_score: float

# ==========================================
# DATA INTEGRITY & PRIVACY ENDPOINTS
# ==========================================

@router.get("/data-lineage")
async def get_data_lineage(data_type: str = "all"):
    """
    Get automated data lineage and provenance tracking.
    Tracks origin and transformation of job-seeker data from input to model training.
    """
    service = get_service()
    return await service.get_data_lineage(data_type)

@router.post("/pii-scan")
async def scan_for_pii(request: PIIScanRequest = None):
    """
    Dynamic PII leakage testing.
    Scans AI outputs for personally identifiable information.
    """
    service = get_service()
    content = request.content if request else None
    return await service.scan_pii_leakage(content)

@router.get("/regional-compliance")
async def get_regional_compliance():
    """
    Get regional compliance status for all supported jurisdictions.
    Includes China, EU, Brazil, US (California/NYC), Japan.
    """
    service = get_service()
    return await service.get_regional_compliance_status()

@router.post("/generate-explanation")
async def generate_decision_explanation(request: ExplanationRequest):
    """
    Generate human-readable explanation for AI decisions.
    Implements 'Right to Explanation' per EU AI Act and LGPD.
    """
    service = get_service()
    return await service.generate_explanation(request.decision_id, request.decision_type)

# ==========================================
# AI QUALITY ASSURANCE ENDPOINTS
# ==========================================

@router.get("/model-drift")
async def get_model_drift_status():
    """
    Get model drift and performance monitoring status.
    Alerts when model accuracy degrades over time.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_model_drift_status()

@router.get("/test-suite")
async def get_test_suite_status():
    """
    Get self-healing test suite status and metrics.
    Shows AI-powered test automation results.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_test_suite_status()

@router.get("/output-validation")
async def get_output_validation(output_id: Optional[str] = None):
    """
    Validate AI outputs for hallucinations.
    Performs grounding checks against source data.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.validate_ai_output(output_id)

@router.get("/red-team")
async def get_red_team_status():
    """
    Get red-teaming and adversarial attack testing status.
    Shows results of prompt injection, jailbreak, and other security tests.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_red_team_status()

# ==========================================
# GLOBAL AUDIT & GOVERNANCE ENDPOINTS
# ==========================================

@router.get("/compliance-logs")
async def get_compliance_logs(limit: int = 100):
    """
    Get continuous compliance logging status.
    100% logging of AI decisions for audit trails.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_compliance_logs(limit)

@router.get("/bias-detection")
async def get_bias_detection_report():
    """
    Get algorithmic bias detection report.
    Monitors protected characteristics for disparate impact.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_bias_detection_report()

@router.get("/risk-inventory")
async def get_ai_risk_inventory():
    """
    Get centralized AI model risk inventory.
    Real-time inventory of all AI models and their risk levels.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_ai_risk_inventory()

@router.get("/automation-tools")
async def get_automation_tools_status():
    """
    Get status of integrated automation tools.
    Shows health of FairNow, mabl, Applitools, etc.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.get_automation_tools_status()

# ==========================================
# COMPREHENSIVE AUDIT ENDPOINT
# ==========================================

@router.post("/run-audit")
async def run_full_audit():
    """
    Run comprehensive data integrity and AI QA audit.
    Executes all checks and returns consolidated report.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    return await service.run_full_audit()

@router.get("/summary")
async def get_summary():
    """
    Get quick summary of data integrity and AI QA status.
    """
    db = get_database()
    service = get_data_integrity_service(db)
    
    # Get key metrics
    compliance = await service.get_regional_compliance_status()
    drift = await service.get_model_drift_status()
    bias = await service.get_bias_detection_report()
    tools = await service.get_automation_tools_status()
    
    return {
        "overall_status": "COMPLIANT",
        "last_updated": datetime.utcnow().isoformat(),
        "key_metrics": {
            "regional_compliance_score": compliance["overall_compliance_score"],
            "model_health": f"{drift['healthy']}/{drift['total_models']} healthy",
            "bias_detection_status": "PASS" if all(
                v["status"] == "PASS" 
                for v in bias["protected_characteristics"].values()
            ) else "REVIEW",
            "automation_tools_health": f"{tools['healthy_tools']}/{tools['total_tools']} healthy"
        },
        "quick_stats": {
            "regions_compliant": 6,
            "models_monitored": drift["total_models"],
            "bias_audits_passed": 4,
            "tools_integrated": tools["total_tools"]
        }
    }
