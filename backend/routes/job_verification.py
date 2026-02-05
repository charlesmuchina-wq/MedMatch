"""
Job Liveness API Routes
Handles job verification and ghost job detection.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

from routes.auth import get_current_user
from services.job_liveness import get_liveness_service

router = APIRouter(prefix="/jobs/verify", tags=["Job Verification"])


class ReportJobRequest(BaseModel):
    job_id: str
    reason: Optional[str] = "expired"


class BatchVerifyRequest(BaseModel):
    job_ids: List[str]
    urls: List[str]


# ============== Report Endpoint (must be before /{job_id} to avoid route conflict) ==============

@router.post("/report")
async def report_expired_job(data: ReportJobRequest, request: Request):
    """
    Report a job as expired/ghost job.
    Jobs with 2+ reports are automatically hidden.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_liveness_service()
    result = await service.report_expired(data.job_id, user["user_id"])
    
    return result


@router.post("/batch")
async def batch_verify_jobs(request: Request):
    """
    Verify multiple jobs in a batch.
    Returns verification status for each job.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        body = await request.json()
        jobs = body.get("jobs", [])
        
        if not jobs:
            return {"verified": [], "count": 0}
        
        service = get_liveness_service()
        results = await service.batch_verify(jobs, max_concurrent=5)
        
        return {
            "verified": results,
            "count": len(results),
            "active_count": sum(1 for r in results if r.get("verification_status", {}).get("is_active", True))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-url")
async def check_url_status(url: str, request: Request):
    """
    Quick check if a URL is still accessible.
    Does not perform full content analysis.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_liveness_service()
    result = await service.check_url_alive(url)
    
    return result
