"""
Cloud Storage Routes
Handles: Google Drive, Dropbox, OneDrive, iCloud file imports
Supports user-managed permissions for personal cloud storage
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import httpx
import logging
import os

router = APIRouter(prefix="/cloud", tags=["Cloud Storage"])

# ============== Configuration ==============

# Environment variables for cloud storage APIs
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY", "")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET", "")
ONEDRIVE_CLIENT_ID = os.environ.get("ONEDRIVE_CLIENT_ID", "")
ONEDRIVE_CLIENT_SECRET = os.environ.get("ONEDRIVE_CLIENT_SECRET", "")
ONEDRIVE_REDIRECT_URI = os.environ.get("ONEDRIVE_REDIRECT_URI", "")

# ============== Models ==============

class GoogleDriveDownloadRequest(BaseModel):
    file_id: str
    access_token: str

class DropboxDownloadRequest(BaseModel):
    file_path: str
    access_token: str

class OneDriveDownloadRequest(BaseModel):
    item_id: str
    access_token: str

class DropboxAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class OneDriveAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class CloudFile(BaseModel):
    id: str
    name: str
    mime_type: Optional[str] = None
    size: Optional[int] = None
    modified_at: Optional[str] = None
    source: str  # "google_drive", "dropbox", "onedrive", "icloud"

# ============== Status Endpoint ==============

@router.get("/status")
async def get_cloud_storage_status():
    """
    Get configuration status for all cloud storage integrations.
    Helps frontend know which integrations are available.
    """
    return {
        "google_drive": {
            "configured": True,  # Uses user's OAuth, no server keys needed
            "status": "active",
            "description": "Users sign in with their Google account"
        },
        "dropbox": {
            "configured": bool(DROPBOX_APP_KEY and DROPBOX_APP_SECRET),
            "status": "active" if DROPBOX_APP_KEY else "pending_config",
            "description": "Dropbox App Folder integration",
            "requires_keys": not bool(DROPBOX_APP_KEY)
        },
        "onedrive": {
            "configured": bool(ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET),
            "status": "active" if ONEDRIVE_CLIENT_ID else "pending_config",
            "description": "Microsoft OneDrive integration",
            "requires_keys": not bool(ONEDRIVE_CLIENT_ID)
        },
        "icloud": {
            "configured": False,
            "status": "ios_only",
            "description": "Available via iOS Share Sheet - no server integration needed"
        },
        "document_scanning": {
            "adobe_scan": {
                "supported": True,
                "method": "share_sheet",
                "description": "Users can share scanned PDFs from Adobe Scan"
            },
            "swift_scan": {
                "supported": True,
                "method": "share_sheet",
                "description": "Users can share scanned documents from SwiftScan"
            }
        }
    }

# ============== Google Drive ==============

@router.post("/google-drive/download")
async def download_google_drive_file(request: GoogleDriveDownloadRequest):
    """
    Proxy endpoint to download files from Google Drive.
    This avoids CORS issues when downloading from the frontend.
    User provides their own OAuth access_token.
    """
    try:
        download_url = f"https://www.googleapis.com/drive/v3/files/{request.file_id}?alt=media"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                download_url,
                headers={"Authorization": f"Bearer {request.access_token}"},
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to download file from Google Drive: {response.text}"
                )
            
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": "attachment; filename=resume"
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Google Drive timed out")
    except Exception as e:
        logging.error(f"Google Drive download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google-drive/list")
async def list_google_drive_files(access_token: str, folder_id: str = "root"):
    """
    List files in a Google Drive folder.
    User provides their own OAuth access_token.
    """
    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and (mimeType='application/pdf' or mimeType='application/msword' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')",
            "fields": "files(id, name, mimeType, size, modifiedTime)",
            "orderBy": "modifiedTime desc",
            "pageSize": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to list files")
            
            data = response.json()
            files = [
                CloudFile(
                    id=f["id"],
                    name=f["name"],
                    mime_type=f.get("mimeType"),
                    size=int(f.get("size", 0)),
                    modified_at=f.get("modifiedTime"),
                    source="google_drive"
                )
                for f in data.get("files", [])
            ]
            
            return {"files": files, "count": len(files)}
            
    except Exception as e:
        logging.error(f"Google Drive list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Dropbox ==============

@router.get("/dropbox/auth-url")
async def get_dropbox_auth_url(redirect_uri: str):
    """
    Get Dropbox OAuth authorization URL.
    Frontend redirects user here to authorize app access.
    """
    if not DROPBOX_APP_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dropbox integration not configured. Admin needs to set DROPBOX_APP_KEY and DROPBOX_APP_SECRET."
        )
    
    auth_url = (
        f"https://www.dropbox.com/oauth2/authorize?"
        f"client_id={DROPBOX_APP_KEY}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"token_access_type=offline"
    )
    
    return {"auth_url": auth_url}

@router.post("/dropbox/token")
async def exchange_dropbox_code(request: DropboxAuthRequest):
    """
    Exchange Dropbox authorization code for access token.
    """
    if not DROPBOX_APP_KEY or not DROPBOX_APP_SECRET:
        raise HTTPException(status_code=503, detail="Dropbox integration not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.dropboxapi.com/oauth2/token",
                data={
                    "code": request.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": request.redirect_uri,
                    "client_id": DROPBOX_APP_KEY,
                    "client_secret": DROPBOX_APP_SECRET
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange Dropbox code")
            
            return response.json()
            
    except Exception as e:
        logging.error(f"Dropbox token exchange error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dropbox/download")
async def download_dropbox_file(request: DropboxDownloadRequest):
    """
    Download a file from Dropbox.
    User provides their own access_token.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://content.dropboxapi.com/2/files/download",
                headers={
                    "Authorization": f"Bearer {request.access_token}",
                    "Dropbox-API-Arg": f'{{"path": "{request.file_path}"}}'
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to download file from Dropbox"
                )
            
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={"Content-Disposition": "attachment; filename=resume"}
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Dropbox timed out")
    except Exception as e:
        logging.error(f"Dropbox download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dropbox/list")
async def list_dropbox_files(access_token: str, folder_path: str = ""):
    """
    List files in a Dropbox folder.
    Filters for document files (PDF, DOC, DOCX).
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.dropboxapi.com/2/files/list_folder",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"path": folder_path if folder_path else "", "recursive": False},
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to list Dropbox files")
            
            data = response.json()
            
            # Filter for document files
            doc_extensions = {".pdf", ".doc", ".docx"}
            files = [
                CloudFile(
                    id=entry["id"],
                    name=entry["name"],
                    mime_type=None,
                    size=entry.get("size", 0),
                    modified_at=entry.get("server_modified"),
                    source="dropbox"
                )
                for entry in data.get("entries", [])
                if entry.get(".tag") == "file" and 
                   any(entry["name"].lower().endswith(ext) for ext in doc_extensions)
            ]
            
            return {"files": files, "count": len(files)}
            
    except Exception as e:
        logging.error(f"Dropbox list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== OneDrive ==============

@router.get("/onedrive/auth-url")
async def get_onedrive_auth_url(redirect_uri: str):
    """
    Get Microsoft OneDrive OAuth authorization URL.
    """
    if not ONEDRIVE_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="OneDrive integration not configured. Admin needs to set ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET."
        )
    
    scopes = "files.read files.read.all offline_access"
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={ONEDRIVE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scopes}"
    )
    
    return {"auth_url": auth_url}

@router.post("/onedrive/token")
async def exchange_onedrive_code(request: OneDriveAuthRequest):
    """
    Exchange OneDrive authorization code for access token.
    """
    if not ONEDRIVE_CLIENT_ID or not ONEDRIVE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="OneDrive integration not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data={
                    "client_id": ONEDRIVE_CLIENT_ID,
                    "client_secret": ONEDRIVE_CLIENT_SECRET,
                    "code": request.code,
                    "redirect_uri": request.redirect_uri,
                    "grant_type": "authorization_code"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange OneDrive code")
            
            return response.json()
            
    except Exception as e:
        logging.error(f"OneDrive token exchange error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/onedrive/download")
async def download_onedrive_file(request: OneDriveDownloadRequest):
    """
    Download a file from OneDrive.
    User provides their own access_token.
    """
    try:
        # First get the download URL
        async with httpx.AsyncClient() as client:
            # Get file metadata with download URL
            meta_response = await client.get(
                f"https://graph.microsoft.com/v1.0/me/drive/items/{request.item_id}",
                headers={"Authorization": f"Bearer {request.access_token}"},
                timeout=30.0
            )
            
            if meta_response.status_code != 200:
                raise HTTPException(status_code=meta_response.status_code, detail="Failed to get file info")
            
            file_data = meta_response.json()
            download_url = file_data.get("@microsoft.graph.downloadUrl")
            
            if not download_url:
                raise HTTPException(status_code=400, detail="No download URL available")
            
            # Download the file
            response = await client.get(download_url, timeout=60.0)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to download file")
            
            return Response(
                content=response.content,
                media_type=file_data.get("file", {}).get("mimeType", "application/octet-stream"),
                headers={"Content-Disposition": f"attachment; filename={file_data.get('name', 'resume')}"}
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to OneDrive timed out")
    except Exception as e:
        logging.error(f"OneDrive download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/onedrive/list")
async def list_onedrive_files(access_token: str, folder_id: str = "root"):
    """
    List files in a OneDrive folder.
    Filters for document files (PDF, DOC, DOCX).
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "$filter": "file ne null",
                    "$select": "id,name,size,lastModifiedDateTime,file",
                    "$orderby": "lastModifiedDateTime desc",
                    "$top": 50
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to list OneDrive files")
            
            data = response.json()
            
            # Filter for document files
            doc_extensions = {".pdf", ".doc", ".docx"}
            files = [
                CloudFile(
                    id=item["id"],
                    name=item["name"],
                    mime_type=item.get("file", {}).get("mimeType"),
                    size=item.get("size", 0),
                    modified_at=item.get("lastModifiedDateTime"),
                    source="onedrive"
                )
                for item in data.get("value", [])
                if any(item["name"].lower().endswith(ext) for ext in doc_extensions)
            ]
            
            return {"files": files, "count": len(files)}
            
    except Exception as e:
        logging.error(f"OneDrive list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Document Scanning Integration Info ==============

@router.get("/scanning-apps")
async def get_scanning_app_info():
    """
    Return information about supported document scanning apps.
    These work via share/export functionality, no server integration needed.
    """
    return {
        "supported_apps": [
            {
                "name": "Adobe Scan",
                "platforms": ["iOS", "Android"],
                "integration_method": "share_sheet",
                "instructions": "In Adobe Scan, tap Share > 'Open In' and select MedMatch",
                "supported_formats": ["PDF"],
                "app_store_url": "https://apps.apple.com/app/adobe-scan/id1199564834",
                "play_store_url": "https://play.google.com/store/apps/details?id=com.adobe.scan.android"
            },
            {
                "name": "SwiftScan",
                "platforms": ["iOS", "Android"],
                "integration_method": "share_sheet",
                "instructions": "In SwiftScan, use 'Share' to send scanned documents to MedMatch",
                "supported_formats": ["PDF", "JPG"],
                "app_store_url": "https://apps.apple.com/app/swiftscan/id834854351",
                "play_store_url": "https://play.google.com/store/apps/details?id=net.doo.snap"
            },
            {
                "name": "Microsoft Lens",
                "platforms": ["iOS", "Android"],
                "integration_method": "share_sheet",
                "instructions": "Scan your document and use 'Share' to send to MedMatch",
                "supported_formats": ["PDF", "Word"],
                "app_store_url": "https://apps.apple.com/app/microsoft-lens/id975925059",
                "play_store_url": "https://play.google.com/store/apps/details?id=com.microsoft.office.officelens"
            }
        ],
        "usage_tips": [
            "For best results, scan in good lighting with documents flat",
            "PDF format is recommended for resume uploads",
            "Multi-page documents are supported"
        ]
    }

# ============== Webhook Integration (Zapier/Make) ==============

@router.get("/webhook-info")
async def get_webhook_integration_info():
    """
    Return information about webhook integrations for workflow automation.
    """
    return {
        "supported_platforms": [
            {
                "name": "Zapier",
                "description": "Connect MedMatch to 5,000+ apps",
                "use_cases": [
                    "Auto-upload resumes from email attachments",
                    "Sync job applications to spreadsheets",
                    "Get Slack notifications for new matches"
                ],
                "setup_url": "https://zapier.com/apps"
            },
            {
                "name": "Make (Integromat)",
                "description": "Advanced workflow automation",
                "use_cases": [
                    "Watch a cloud folder for new resumes",
                    "Auto-generate cover letters on new job matches",
                    "Sync interview schedules to calendar"
                ],
                "setup_url": "https://www.make.com"
            }
        ],
        "webhook_endpoints": {
            "resume_upload": "/api/webhooks/resume",
            "job_alert": "/api/webhooks/job-alert",
            "application_status": "/api/webhooks/application"
        },
        "authentication": "Bearer token required - generate from Settings > API Access"
    }
