"""
ORCID OAuth 2.0 Integration
Allows researchers to sign in with ORCID and auto-import their verified credentials

ORCID OAuth is FREE - you just need to register your app at:
- Sandbox (testing): https://sandbox.orcid.org/developer-tools
- Production: https://orcid.org/developer-tools

Required Environment Variables:
- ORCID_CLIENT_ID: Your registered client ID
- ORCID_CLIENT_SECRET: Your client secret
- ORCID_REDIRECT_URI: Your callback URL (e.g., https://yourdomain.com/api/orcid/callback)
- ORCID_ENVIRONMENT: 'sandbox' or 'production' (default: sandbox)
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import httpx
import os
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orcid", tags=["ORCID OAuth"])

# Environment configuration
ORCID_CLIENT_ID = os.environ.get("ORCID_CLIENT_ID", "")
ORCID_CLIENT_SECRET = os.environ.get("ORCID_CLIENT_SECRET", "")
ORCID_REDIRECT_URI = os.environ.get("ORCID_REDIRECT_URI", "")
ORCID_ENVIRONMENT = os.environ.get("ORCID_ENVIRONMENT", "sandbox")

# ORCID URLs based on environment
ORCID_URLS = {
    "sandbox": {
        "auth": "https://sandbox.orcid.org/oauth/authorize",
        "token": "https://sandbox.orcid.org/oauth/token",
        "api": "https://pub.sandbox.orcid.org/v3.0"
    },
    "production": {
        "auth": "https://orcid.org/oauth/authorize",
        "token": "https://orcid.org/oauth/token",
        "api": "https://pub.orcid.org/v3.0"
    }
}

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "MedMatch")

from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
orcid_connections_collection = db["orcid_connections"]
users_collection = db["users"]

# In-memory state storage (use Redis in production)
oauth_states = {}


class ORCIDConnectionResponse(BaseModel):
    connected: bool
    orcid_id: Optional[str] = None
    name: Optional[str] = None
    education: Optional[List[Dict]] = None
    employment: Optional[List[Dict]] = None
    publications_count: Optional[int] = None


@router.get("/config")
async def get_orcid_config():
    """Check if ORCID OAuth is configured."""
    is_configured = bool(ORCID_CLIENT_ID and ORCID_CLIENT_SECRET and ORCID_REDIRECT_URI)
    
    return {
        "configured": is_configured,
        "environment": ORCID_ENVIRONMENT,
        "client_id_set": bool(ORCID_CLIENT_ID),
        "redirect_uri_set": bool(ORCID_REDIRECT_URI),
        "setup_instructions": None if is_configured else {
            "step1": "Register your app at https://orcid.org/developer-tools (free)",
            "step2": "Get your Client ID and Client Secret",
            "step3": f"Set redirect URI to: {os.environ.get('REACT_APP_BACKEND_URL', 'https://yourdomain.com')}/api/orcid/callback",
            "step4": "Add ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, ORCID_REDIRECT_URI to backend/.env"
        }
    }


@router.get("/auth/url")
async def get_auth_url(user_id: str = Query(..., description="Current user's ID")):
    """
    Generate ORCID OAuth authorization URL.
    
    This starts the OAuth flow - redirect the user to this URL.
    """
    if not ORCID_CLIENT_ID or not ORCID_REDIRECT_URI:
        raise HTTPException(
            status_code=503,
            detail="ORCID OAuth not configured. Please set ORCID_CLIENT_ID and ORCID_REDIRECT_URI."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Build authorization URL
    urls = ORCID_URLS.get(ORCID_ENVIRONMENT, ORCID_URLS["sandbox"])
    
    auth_url = (
        f"{urls['auth']}"
        f"?client_id={ORCID_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=/read-limited"
        f"&redirect_uri={ORCID_REDIRECT_URI}"
        f"&state={state}"
    )
    
    return {
        "auth_url": auth_url,
        "state": state,
        "instructions": "Redirect the user to auth_url. They will sign in to ORCID and authorize your app."
    }


@router.get("/callback")
async def orcid_callback(
    code: str = Query(None, description="Authorization code from ORCID"),
    state: str = Query(None, description="State parameter for CSRF verification"),
    error: str = Query(None, description="Error code if authorization failed"),
    error_description: str = Query(None, description="Error description")
):
    """
    ORCID OAuth callback handler.
    
    This endpoint receives the authorization code after user approves the connection.
    """
    # Handle errors
    if error:
        logger.error(f"ORCID OAuth error: {error} - {error_description}")
        # Redirect to frontend with error
        frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "").replace("/api", "")
        return RedirectResponse(
            url=f"{frontend_url}/profile?orcid_error={error}&message={error_description}"
        )
    
    # Verify state
    if not state or state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")
    
    state_data = oauth_states.pop(state)
    user_id = state_data["user_id"]
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    # Exchange code for access token
    urls = ORCID_URLS.get(ORCID_ENVIRONMENT, ORCID_URLS["sandbox"])
    
    try:
        async with httpx.AsyncClient() as http_client:
            token_response = await http_client.post(
                urls["token"],
                data={
                    "client_id": ORCID_CLIENT_ID,
                    "client_secret": ORCID_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": ORCID_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                logger.error(f"ORCID token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            
            token_data = token_response.json()
            
            # Extract ORCID iD and tokens
            orcid_id = token_data.get("orcid")
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            name = token_data.get("name")
            
            # Fetch full ORCID record
            record_response = await http_client.get(
                f"{urls['api']}/{orcid_id}/record",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            orcid_record = {}
            if record_response.status_code == 200:
                orcid_record = await _parse_orcid_record(record_response.json())
            
            # Store connection in database
            connection_doc = {
                "user_id": user_id,
                "orcid_id": orcid_id,
                "name": name,
                "access_token": access_token,  # In production, encrypt this
                "refresh_token": refresh_token,
                "token_scope": token_data.get("scope"),
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "last_synced": datetime.now(timezone.utc).isoformat(),
                "record": orcid_record
            }
            
            # Upsert connection
            await orcid_connections_collection.update_one(
                {"user_id": user_id},
                {"$set": connection_doc},
                upsert=True
            )
            
            # Update user profile with ORCID data
            await _update_user_with_orcid(user_id, orcid_id, orcid_record)
            
            # Redirect to frontend with success
            frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "").replace("/api", "")
            return RedirectResponse(
                url=f"{frontend_url}/profile?orcid_connected=true&orcid_id={orcid_id}"
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ORCID API timeout")
    except Exception as e:
        logger.error(f"ORCID callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection/{user_id}")
async def get_orcid_connection(user_id: str):
    """Get user's ORCID connection status and imported data."""
    connection = await orcid_connections_collection.find_one({"user_id": user_id})
    
    if not connection:
        return {
            "connected": False,
            "orcid_id": None,
            "message": "No ORCID connection found. Connect your ORCID to import verified credentials."
        }
    
    return {
        "connected": True,
        "orcid_id": connection.get("orcid_id"),
        "orcid_url": f"https://orcid.org/{connection.get('orcid_id')}",
        "name": connection.get("name"),
        "connected_at": connection.get("connected_at"),
        "last_synced": connection.get("last_synced"),
        "record": connection.get("record", {})
    }


@router.post("/sync/{user_id}")
async def sync_orcid_data(user_id: str):
    """
    Refresh ORCID data for a connected user.
    
    Fetches the latest education, employment, and publications from ORCID.
    """
    connection = await orcid_connections_collection.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="No ORCID connection found")
    
    orcid_id = connection.get("orcid_id")
    access_token = connection.get("access_token")
    
    urls = ORCID_URLS.get(ORCID_ENVIRONMENT, ORCID_URLS["sandbox"])
    
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{urls['api']}/{orcid_id}/record",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code == 401:
                # Token expired - user needs to reconnect
                return {
                    "success": False,
                    "error": "token_expired",
                    "message": "ORCID token expired. Please reconnect your ORCID account."
                }
            
            if response.status_code == 200:
                orcid_record = await _parse_orcid_record(response.json())
                
                # Update connection
                await orcid_connections_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "record": orcid_record,
                            "last_synced": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                # Update user profile
                await _update_user_with_orcid(user_id, orcid_id, orcid_record)
                
                return {
                    "success": True,
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                    "record": orcid_record
                }
            else:
                return {
                    "success": False,
                    "error": f"ORCID API returned {response.status_code}"
                }
                
    except Exception as e:
        logger.error(f"ORCID sync error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/disconnect/{user_id}")
async def disconnect_orcid(user_id: str):
    """Disconnect ORCID from user account."""
    result = await orcid_connections_collection.delete_one({"user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No ORCID connection found")
    
    return {
        "success": True,
        "message": "ORCID disconnected successfully"
    }


async def _parse_orcid_record(data: Dict) -> Dict:
    """Parse ORCID API response into a cleaner format."""
    person = data.get("person", {})
    activities = data.get("activities-summary", {})
    
    # Parse name
    name_data = person.get("name", {})
    name = {
        "given_names": name_data.get("given-names", {}).get("value"),
        "family_name": name_data.get("family-name", {}).get("value"),
        "credit_name": name_data.get("credit-name", {}).get("value") if name_data.get("credit-name") else None
    }
    
    # Parse education
    educations = []
    for edu_group in activities.get("educations", {}).get("affiliation-group", []):
        for summary in edu_group.get("summaries", []):
            edu = summary.get("education-summary", {})
            source = edu.get("source", {}).get("source-name", {}).get("value")
            educations.append({
                "institution": edu.get("organization", {}).get("name"),
                "department": edu.get("department-name"),
                "degree": edu.get("role-title"),
                "start_year": edu.get("start-date", {}).get("year", {}).get("value") if edu.get("start-date") else None,
                "end_year": edu.get("end-date", {}).get("year", {}).get("value") if edu.get("end-date") else None,
                "source": source,
                "verified_by_institution": source is not None
            })
    
    # Parse employment
    employments = []
    for emp_group in activities.get("employments", {}).get("affiliation-group", []):
        for summary in emp_group.get("summaries", []):
            emp = summary.get("employment-summary", {})
            employments.append({
                "organization": emp.get("organization", {}).get("name"),
                "department": emp.get("department-name"),
                "role": emp.get("role-title"),
                "start_year": emp.get("start-date", {}).get("year", {}).get("value") if emp.get("start-date") else None,
                "end_year": emp.get("end-date", {}).get("year", {}).get("value") if emp.get("end-date") else None,
                "source": emp.get("source", {}).get("source-name", {}).get("value")
            })
    
    # Count publications
    works = activities.get("works", {}).get("group", [])
    
    return {
        "name": name,
        "education": educations,
        "employment": employments,
        "publications_count": len(works)
    }


async def _update_user_with_orcid(user_id: str, orcid_id: str, record: Dict):
    """Update user profile with ORCID verified data."""
    update_data = {
        "orcid_id": orcid_id,
        "orcid_verified": True,
        "orcid_last_sync": datetime.now(timezone.utc).isoformat()
    }
    
    # Add verified education if available
    if record.get("education"):
        verified_education = [
            edu for edu in record["education"] 
            if edu.get("verified_by_institution")
        ]
        if verified_education:
            update_data["orcid_verified_education"] = verified_education
    
    # Add employment history
    if record.get("employment"):
        update_data["orcid_employment"] = record["employment"]
    
    # Update user
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
