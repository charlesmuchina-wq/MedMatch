"""
Cloud Storage Routes
Handles: Google Drive, Dropbox, OneDrive file imports
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import httpx
import logging

router = APIRouter(prefix="/cloud", tags=["Cloud Storage"])

# ============== Models ==============

class GoogleDriveDownloadRequest(BaseModel):
    file_id: str
    access_token: str

# ============== Routes ==============

@router.post("/google-drive/download")
async def download_google_drive_file(request: GoogleDriveDownloadRequest):
    """
    Proxy endpoint to download files from Google Drive.
    This avoids CORS issues when downloading from the frontend.
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
            
            # Get content type from response
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            # Return the file content
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
