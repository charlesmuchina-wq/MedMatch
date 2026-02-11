"""
Audit Report API Routes
Customizable compliance audit reports per government/regulatory request
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone

from routes.auth import get_current_user
from utils.database import db
from services.audit_reports import get_audit_report_service, AuditReportService

router = APIRouter(prefix="/audit-reports", tags=["Audit Reports"])


# ============== Pydantic Models ==============

class ReportConfig(BaseModel):
    template_id: str
    sections: Optional[List[str]] = None  # If None, use template defaults
    date_range: Optional[Dict] = None  # {"start": "2025-01-01", "end": "2025-12-31"}
    organization: Optional[Dict] = None
    ai_system: Optional[Dict] = None
    custom_fields: Optional[Dict] = None


class CustomReportConfig(BaseModel):
    name: str
    description: str
    sections: List[str]
    date_range: Dict
    requesting_authority: str
    report_purpose: str
    custom_fields: Optional[Dict] = None


# ============== Template Endpoints ==============

@router.get("/templates")
async def get_available_templates(request: Request):
    """
    Get all available audit report templates.
    Each template is designed for a specific regulatory framework.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    templates = await service.get_available_templates()
    
    return {
        "templates": templates,
        "count": len(templates)
    }


@router.get("/templates/{template_id}")
async def get_template_details(template_id: str, request: Request):
    """
    Get detailed information about a specific template including available sections.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    template = await service.get_template_details(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    
    return template


@router.get("/available-sections")
async def get_available_sections(request: Request):
    """
    Get all available sections that can be included in reports.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    return {
        "sections": [
            {"id": sec_id, **sec_info}
            for sec_id, sec_info in service.AVAILABLE_SECTIONS.items()
        ]
    }


# ============== Report Generation ==============

@router.post("/generate")
async def generate_report(config: ReportConfig, request: Request):
    """
    Generate a new audit report based on the specified template and configuration.
    
    The report will include all sections specified in the template by default,
    or you can customize which sections to include.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    try:
        report = await service.generate_report(
            template_id=config.template_id,
            report_config={
                "sections": config.sections,
                "date_range": config.date_range or {},
                "organization": config.organization or {},
                "ai_system": config.ai_system,
                "custom_fields": config.custom_fields
            },
            user_id=user["user_id"]
        )
        
        return {
            "success": True,
            "report": report
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/generate-custom")
async def generate_custom_report(config: CustomReportConfig, request: Request):
    """
    Generate a fully customized audit report for specific regulatory requests.
    Use this when standard templates don't fit the requirement.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    try:
        report = await service.generate_report(
            template_id="CUSTOM",
            report_config={
                "sections": config.sections,
                "date_range": config.date_range,
                "custom_fields": {
                    "report_name": config.name,
                    "description": config.description,
                    "requesting_authority": config.requesting_authority,
                    "report_purpose": config.report_purpose,
                    **(config.custom_fields or {})
                }
            },
            user_id=user["user_id"]
        )
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom report generation failed: {str(e)}")


# ============== Report History & Retrieval ==============

@router.get("/history")
async def get_report_history(request: Request, limit: int = 20):
    """
    Get previously generated audit reports.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    reports = await service.get_report_history(user_id=user["user_id"], limit=limit)
    
    return {
        "reports": reports,
        "count": len(reports)
    }


@router.get("/{report_id}")
async def get_report(report_id: str, request: Request):
    """
    Get a specific audit report by ID.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    report = await service.get_report_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str, format: str = "json", request: Request = None):
    """
    Download an audit report in the specified format.
    Supported formats: json
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    report = await service.get_report_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if format == "json":
        return JSONResponse(
            content=report,
            headers={
                "Content-Disposition": f"attachment; filename={report_id}.json"
            }
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


# ============== Quick Report Endpoints ==============

@router.post("/quick/nyc-ll144")
async def generate_nyc_ll144_report(request: Request):
    """Quick generate NYC Local Law 144 Bias Audit Report."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    report = await service.generate_report(
        template_id="NYC_LL144",
        report_config={},
        user_id=user["user_id"]
    )
    
    return {"success": True, "report": report}


@router.post("/quick/eu-ai-act")
async def generate_eu_ai_act_report(request: Request):
    """Quick generate EU AI Act Compliance Report."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    report = await service.generate_report(
        template_id="EU_AI_ACT",
        report_config={},
        user_id=user["user_id"]
    )
    
    return {"success": True, "report": report}


@router.post("/quick/gdpr-art22")
async def generate_gdpr_report(request: Request):
    """Quick generate GDPR Article 22 Report."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_audit_report_service(db)
    if not service:
        service = AuditReportService(db)
    
    report = await service.generate_report(
        template_id="GDPR_ART22",
        report_config={},
        user_id=user["user_id"]
    )
    
    return {"success": True, "report": report}
