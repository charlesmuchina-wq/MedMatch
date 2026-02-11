"""
Audit Report API Routes
Customizable compliance audit reports per government/regulatory request
Includes PDF export with date range filtering
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone

from routes.auth import get_current_user
from utils.database import db
from services.audit_reports import get_audit_report_service, AuditReportService
from services.pdf_export import get_pdf_service, PDFExportService

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


class PDFExportConfig(BaseModel):
    template_id: str
    date_preset: str = "last_30_days"  # today, yesterday, last_7_days, last_30_days, this_month, last_month, this_quarter, last_quarter, this_year, last_year, custom
    custom_start: Optional[str] = None  # ISO date string for custom range
    custom_end: Optional[str] = None  # ISO date string for custom range
    sections: Optional[List[str]] = None  # Specific sections to include


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


@router.get("/date-presets")
async def get_date_presets(request: Request):
    """
    Get available date range presets for PDF export.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    pdf_service = get_pdf_service(db)
    if not pdf_service:
        pdf_service = PDFExportService(db)
    
    presets = [
        {"id": key, **value}
        for key, value in pdf_service.DATE_PRESETS.items()
    ]
    
    return {"presets": presets}


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


# ============== PDF Export Endpoints ==============

@router.post("/export/pdf")
async def export_report_pdf(config: PDFExportConfig, request: Request):
    """
    Generate and export an audit report as PDF with date range filtering.
    
    Date presets available:
    - today: Today only
    - yesterday: Yesterday only
    - last_7_days: Last 7 days
    - last_30_days: Last 30 days (default)
    - this_month: Current month
    - last_month: Previous month
    - this_quarter: Current quarter
    - last_quarter: Previous quarter
    - this_year: Current year
    - last_year: Previous year
    - custom: Custom date range (requires custom_start and custom_end)
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Initialize services
    report_service = get_audit_report_service(db)
    pdf_service = get_pdf_service(db)
    
    if not report_service:
        report_service = AuditReportService(db)
    if not pdf_service:
        pdf_service = PDFExportService(db)
    
    try:
        # Calculate date range
        date_range = pdf_service.calculate_date_range(
            preset=config.date_preset,
            custom_start=config.custom_start,
            custom_end=config.custom_end
        )
        
        # Generate the report
        report = await report_service.generate_report(
            template_id=config.template_id,
            report_config={
                "date_range": {
                    "start": date_range["start"],
                    "end": date_range["end"]
                },
                "sections": config.sections
            },
            user_id=user["user_id"]
        )
        
        # Generate PDF
        pdf_bytes = await pdf_service.generate_pdf(
            report_data=report,
            date_range=date_range,
            include_sections=config.sections
        )
        
        # Generate filename
        filename = f"{config.template_id.lower()}_{date_range['preset']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@router.post("/export/pdf/quick/{template_id}")
async def quick_export_pdf(
    template_id: str,
    date_preset: str = "last_30_days",
    request: Request = None
):
    """
    Quick export a PDF report with minimal configuration.
    Just specify the template and date preset.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Initialize services
    report_service = get_audit_report_service(db)
    pdf_service = get_pdf_service(db)
    
    if not report_service:
        report_service = AuditReportService(db)
    if not pdf_service:
        pdf_service = PDFExportService(db)
    
    try:
        # Calculate date range
        date_range = pdf_service.calculate_date_range(preset=date_preset)
        
        # Generate the report
        report = await report_service.generate_report(
            template_id=template_id.upper(),
            report_config={
                "date_range": {
                    "start": date_range["start"],
                    "end": date_range["end"]
                }
            },
            user_id=user["user_id"]
        )
        
        # Generate PDF
        pdf_bytes = await pdf_service.generate_pdf(
            report_data=report,
            date_range=date_range
        )
        
        # Generate filename
        filename = f"{template_id.lower()}_{date_preset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@router.get("/{report_id}/pdf")
async def export_existing_report_pdf(
    report_id: str,
    date_preset: str = "custom",
    request: Request = None
):
    """
    Export an existing report as PDF.
    Uses the original report's date range.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get services
    report_service = get_audit_report_service(db)
    pdf_service = get_pdf_service(db)
    
    if not report_service:
        report_service = AuditReportService(db)
    if not pdf_service:
        pdf_service = PDFExportService(db)
    
    # Get the existing report
    report = await report_service.get_report_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Use the report's original date range
        date_range = {
            "start": report.get("reporting_period", {}).get("start", ""),
            "end": report.get("reporting_period", {}).get("end", ""),
            "label": "Report Period",
            "preset": "custom"
        }
        
        # Generate PDF
        pdf_bytes = await pdf_service.generate_pdf(
            report_data=report,
            date_range=date_range
        )
        
        # Generate filename
        filename = f"{report.get('template_id', 'report').lower()}_{report_id}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")
