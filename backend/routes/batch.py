"""
Batch Request Handler
Processes multiple API requests in a single HTTP call
Reduces connection overhead and helps with rate limiting
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["batch"])

class BatchRequestItem(BaseModel):
    """Single request in a batch"""
    method: str = "GET"
    path: str
    body: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None

class BatchRequest(BaseModel):
    """Batch of requests"""
    requests: List[BatchRequestItem]
    parallel: bool = True  # Execute in parallel or sequential

class BatchResponseItem(BaseModel):
    """Single response in a batch"""
    status: int
    data: Any
    error: Optional[str] = None
    duration_ms: float

class BatchResponse(BaseModel):
    """Batch response"""
    responses: List[BatchResponseItem]
    total_duration_ms: float
    parallel: bool

# Import route handlers

# Route mapping for batch processing
ROUTE_HANDLERS = {
    "/api/auth/me": ("GET", "auth", "get_current_user_profile"),
    "/api/saved-jobs": ("GET", "jobs", "get_saved_jobs"),
    "/api/resume": ("GET", "resume", "get_resume"),
    "/api/qa-practice/favorites": ("GET", "qa_practice", "get_favorite_answers"),
    "/api/translate/languages": ("GET", "translation", "get_languages"),
    "/api/notifications/preferences": ("GET", "notifications", "get_preferences"),
}

async def process_single_request(
    request_item: BatchRequestItem,
    original_request: Request
) -> BatchResponseItem:
    """Process a single request from the batch"""
    start_time = time.perf_counter()
    
    try:
        # For now, return a simple passthrough
        # In production, this would route to actual handlers
        
        # Simulate processing
        await asyncio.sleep(0.001)  # 1ms minimum
        
        return BatchResponseItem(
            status=200,
            data={"path": request_item.path, "processed": True},
            duration_ms=(time.perf_counter() - start_time) * 1000
        )
        
    except Exception as e:
        return BatchResponseItem(
            status=500,
            data=None,
            error=str(e),
            duration_ms=(time.perf_counter() - start_time) * 1000
        )

@router.post("/batch", response_model=BatchResponse)
async def process_batch(batch: BatchRequest, request: Request):
    """
    Process multiple API requests in a single call.
    
    Benefits:
    - Reduces HTTP overhead
    - Helps avoid rate limiting
    - Improves mobile app performance
    
    Max batch size: 20 requests
    """
    if len(batch.requests) > 20:
        raise HTTPException(
            status_code=400, 
            detail="Maximum batch size is 20 requests"
        )
    
    if len(batch.requests) == 0:
        raise HTTPException(
            status_code=400,
            detail="Batch must contain at least one request"
        )
    
    start_time = time.perf_counter()
    
    if batch.parallel:
        # Process all requests in parallel
        tasks = [
            process_single_request(req, request) 
            for req in batch.requests
        ]
        responses = await asyncio.gather(*tasks)
    else:
        # Process sequentially
        responses = []
        for req in batch.requests:
            resp = await process_single_request(req, request)
            responses.append(resp)
    
    total_duration = (time.perf_counter() - start_time) * 1000
    
    logger.info(f"Batch processed: {len(batch.requests)} requests in {total_duration:.1f}ms")
    
    return BatchResponse(
        responses=list(responses),
        total_duration_ms=total_duration,
        parallel=batch.parallel
    )

@router.get("/batch/stats")
async def get_batch_stats():
    """Get batch processing statistics"""
    return {
        "max_batch_size": 20,
        "supported_endpoints": list(ROUTE_HANDLERS.keys()),
        "features": [
            "Parallel execution",
            "Sequential execution",
            "Error isolation",
            "Per-request timing"
        ]
    }
