"""
Enhanced Search API Routes
Provides:
- Autocomplete suggestions
- Spell correction
- Fuzzy search
- CTR tracking
- Search analytics
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import logging

from services.search_engine import get_search_service
from routes.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search Engine"])
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    page: int = 1
    limit: int = 20


class ClickTrackRequest(BaseModel):
    query: str
    result_id: str
    position: int


class AutocompleteResponse(BaseModel):
    suggestions: List[Dict]
    query: str


# ============== Autocomplete Endpoint ==============

@router.get("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """
    Get autocomplete suggestions for a partial query.
    Returns suggestions from:
    - Popular searches
    - User's search history
    - Job titles in database
    - Fuzzy matches
    """
    try:
        search_service = get_search_service()
        user_id = str(current_user.get("_id", "")) if current_user else None
        
        suggestions = await search_service.get_autocomplete_suggestions(
            partial_query=q,
            limit=limit,
            user_id=user_id
        )
        
        return {
            "suggestions": suggestions,
            "query": q
        }
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get autocomplete suggestions")


# ============== Spell Check Endpoint ==============

@router.get("/spell-check")
async def check_spelling(
    q: str = Query(..., min_length=1, description="Query to check")
):
    """
    Check and correct spelling in a search query.
    Returns the corrected query if corrections were made.
    """
    try:
        search_service = get_search_service()
        corrected, was_corrected = search_service.correct_spelling(q)
        
        return {
            "original": q,
            "corrected": corrected if was_corrected else None,
            "was_corrected": was_corrected
        }
    except Exception as e:
        logger.error(f"Spell check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check spelling")


# ============== Intent Extraction Endpoint ==============

@router.get("/intent")
async def extract_intent(
    q: str = Query(..., min_length=1, description="Query to analyze")
):
    """
    Extract search intent from a natural language query.
    Returns structured intent with job title, location, job type, etc.
    """
    try:
        search_service = get_search_service()
        intent = search_service.extract_search_intent(q)
        
        return {
            "query": q,
            "intent": intent
        }
    except Exception as e:
        logger.error(f"Intent extraction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract intent")


# ============== Enhanced Search Endpoint ==============

@router.post("/enhanced")
async def enhanced_search(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform enhanced search with:
    - Spell correction
    - Synonym expansion
    - Fuzzy matching
    - Semantic intent extraction
    - CTR-based ranking
    """
    try:
        search_service = get_search_service()
        user_id = str(current_user.get("_id", "")) if current_user else None
        
        filters = {}
        if request.location:
            filters["location"] = request.location
        if request.job_type:
            filters["job_type"] = request.job_type
        if request.experience_level:
            filters["experience_level"] = request.experience_level
        if request.salary_min:
            filters["salary_min"] = request.salary_min
        if request.salary_max:
            filters["salary_max"] = request.salary_max
        
        results = await search_service.enhanced_search(
            query=request.query,
            user_id=user_id,
            filters=filters if filters else None,
            page=request.page,
            limit=request.limit
        )
        
        return results
    except Exception as e:
        logger.error(f"Enhanced search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


# ============== CTR Tracking Endpoints ==============

@router.post("/track-click")
async def track_click(
    request: ClickTrackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Track when a user clicks on a search result.
    Used to improve search ranking based on CTR.
    """
    try:
        search_service = get_search_service()
        await search_service.track_click(
            query=request.query,
            result_id=request.result_id,
            position=request.position
        )
        return {"status": "tracked"}
    except Exception as e:
        logger.error(f"Click tracking error: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/track-impression")
async def track_impression(
    query: str = Query(...),
    result_ids: List[str] = []
):
    """
    Track impressions for search results.
    Used to calculate CTR for ranking improvements.
    """
    try:
        search_service = get_search_service()
        await search_service.track_impression(query, result_ids)
        return {"status": "tracked", "count": len(result_ids)}
    except Exception as e:
        logger.error(f"Impression tracking error: {e}")
        return {"status": "error", "message": str(e)}


# ============== Search History Endpoint ==============

@router.get("/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's recent search history.
    """
    try:
        search_service = get_search_service()
        user_id = str(current_user.get("_id", ""))
        
        history = search_service.search_history.get(user_id, [])[-limit:]
        
        return {
            "searches": list(reversed(history)),
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Search history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search history")


# ============== Popular Searches Endpoint ==============

@router.get("/popular")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get popular/trending search queries.
    """
    try:
        search_service = get_search_service()
        popular = search_service.popular_searches[-limit:]
        
        return {
            "searches": list(reversed(popular)),
            "count": len(popular)
        }
    except Exception as e:
        logger.error(f"Popular searches error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular searches")


# ============== Synonym Expansion Endpoint ==============

@router.get("/expand")
async def expand_query(
    q: str = Query(..., min_length=1, description="Query to expand")
):
    """
    Expand a query with synonyms for broader search.
    """
    try:
        search_service = get_search_service()
        expanded = search_service.expand_synonyms(q)
        
        return {
            "original": q,
            "expanded": expanded
        }
    except Exception as e:
        logger.error(f"Query expansion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to expand query")
