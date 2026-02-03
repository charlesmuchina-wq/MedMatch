"""
LinkedIn Profile Sync Routes
Handles: OAuth flow, profile import, data sync
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
import logging
import os
import httpx

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

# ============== Configuration ==============

LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.environ.get("LINKEDIN_REDIRECT_URI", "")

# ============== Models ==============

class LinkedInAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class LinkedInSyncRequest(BaseModel):
    access_token: str

# ============== Status Endpoint ==============

@router.get("/status")
async def get_linkedin_status(request: Request):
    """Check LinkedIn integration status and user connection"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user has connected LinkedIn
    linkedin_connection = await db.linkedin_connections.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "access_token": 0}  # Don't expose token
    )
    
    return {
        "integration_configured": bool(LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET),
        "user_connected": linkedin_connection is not None,
        "connection_details": {
            "linkedin_name": linkedin_connection.get("name") if linkedin_connection else None,
            "linkedin_email": linkedin_connection.get("email") if linkedin_connection else None,
            "connected_at": linkedin_connection.get("connected_at") if linkedin_connection else None,
            "last_synced": linkedin_connection.get("last_synced") if linkedin_connection else None
        } if linkedin_connection else None
    }

# ============== OAuth Flow ==============

@router.get("/auth-url")
async def get_linkedin_auth_url(redirect_uri: str):
    """Get LinkedIn OAuth authorization URL"""
    if not LINKEDIN_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="LinkedIn integration not configured. Admin needs to set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET."
        )
    
    # LinkedIn OAuth 2.0 scopes
    scopes = "openid profile email"
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={LINKEDIN_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scopes}&"
        f"state={uuid.uuid4().hex}"
    )
    
    return {"auth_url": auth_url}

@router.post("/token")
async def exchange_linkedin_code(auth_request: LinkedInAuthRequest, request: Request):
    """Exchange LinkedIn authorization code for access token"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="LinkedIn integration not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": auth_request.code,
                    "redirect_uri": auth_request.redirect_uri,
                    "client_id": LINKEDIN_CLIENT_ID,
                    "client_secret": LINKEDIN_CLIENT_SECRET
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )
            
            if token_response.status_code != 200:
                logging.error(f"LinkedIn token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange LinkedIn code")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get basic profile info
            profile_response = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30.0
            )
            
            if profile_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get LinkedIn profile")
            
            profile = profile_response.json()
            
            # Store connection
            await db.linkedin_connections.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "user_id": user["user_id"],
                    "access_token": access_token,
                    "expires_in": token_data.get("expires_in"),
                    "linkedin_id": profile.get("sub"),
                    "name": profile.get("name"),
                    "email": profile.get("email"),
                    "picture": profile.get("picture"),
                    "connected_at": datetime.now(timezone.utc).isoformat(),
                    "last_synced": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
            return {
                "message": "LinkedIn connected successfully",
                "profile": {
                    "name": profile.get("name"),
                    "email": profile.get("email"),
                    "picture": profile.get("picture")
                }
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LinkedIn request timed out")
    except Exception as e:
        logging.error(f"LinkedIn connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Profile Sync ==============

@router.post("/sync")
async def sync_linkedin_profile(request: Request):
    """Sync LinkedIn profile data to MedMatch resume"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get stored connection
    connection = await db.linkedin_connections.find_one({"user_id": user["user_id"]})
    if not connection:
        raise HTTPException(status_code=400, detail="LinkedIn not connected. Please connect first.")
    
    access_token = connection.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid LinkedIn connection. Please reconnect.")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get full profile info (basic info from userinfo endpoint)
            profile_response = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30.0
            )
            
            if profile_response.status_code == 401:
                # Token expired, need to reconnect
                await db.linkedin_connections.delete_one({"user_id": user["user_id"]})
                raise HTTPException(status_code=401, detail="LinkedIn token expired. Please reconnect.")
            
            if profile_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile")
            
            profile = profile_response.json()
            
            # Update user's resume with LinkedIn data
            linkedin_data = {
                "linkedin_synced": True,
                "linkedin_id": profile.get("sub"),
                "full_name": profile.get("name"),
                "email": profile.get("email"),
                "profile_picture": profile.get("picture"),
                "linkedin_last_synced": datetime.now(timezone.utc).isoformat()
            }
            
            # Update or create resume with LinkedIn data
            existing_resume = await db.resumes.find_one({"user_id": user["user_id"]})
            
            if existing_resume:
                await db.resumes.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": linkedin_data}
                )
            else:
                # Create new resume from LinkedIn
                resume_doc = {
                    "id": f"resume_{uuid.uuid4().hex[:12]}",
                    "user_id": user["user_id"],
                    **linkedin_data,
                    "skills": [],
                    "experience": [],
                    "education": [],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.resumes.insert_one(resume_doc)
            
            # Update sync timestamp
            await db.linkedin_connections.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"last_synced": datetime.now(timezone.utc).isoformat()}}
            )
            
            return {
                "message": "LinkedIn profile synced successfully",
                "synced_data": {
                    "name": profile.get("name"),
                    "email": profile.get("email"),
                    "picture": profile.get("picture")
                }
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LinkedIn request timed out")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"LinkedIn sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Disconnect ==============

@router.delete("/disconnect")
async def disconnect_linkedin(request: Request):
    """Disconnect LinkedIn from user account"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.linkedin_connections.delete_one({"user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No LinkedIn connection found")
    
    # Remove LinkedIn data from resume
    await db.resumes.update_one(
        {"user_id": user["user_id"]},
        {"$unset": {
            "linkedin_synced": "",
            "linkedin_id": "",
            "linkedin_last_synced": ""
        }}
    )
    
    return {"message": "LinkedIn disconnected successfully"}
