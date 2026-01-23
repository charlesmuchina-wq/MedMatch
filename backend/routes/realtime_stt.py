"""
Real-time Speech-to-Text Routes
WebSocket-based live audio transcription using OpenAI Whisper
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import logging
import os
import tempfile
import uuid
import base64
from datetime import datetime, timezone
import io

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

# Import STT from the correct location
try:
    from emergentintegrations.llm.openai import OpenAISpeechToText
except ImportError:
    # Fallback for different package structure
    OpenAISpeechToText = None

router = APIRouter(prefix="/realtime-stt", tags=["Real-time Speech-to-Text"])

# Active WebSocket connections for real-time transcription
active_connections: Dict[str, WebSocket] = {}

# ============== Models ==============

class TranscriptionResult(BaseModel):
    text: str
    is_final: bool
    confidence: float = 1.0
    language: str = "en"
    duration_seconds: float = 0.0

class TranscriptionSession(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    status: str  # active, completed, error
    transcription: str = ""
    word_count: int = 0

# ============== Helper Functions ==============

async def transcribe_audio_chunk(audio_data: bytes, format: str = "webm") -> Optional[str]:
    """Transcribe a chunk of audio using Whisper"""
    if not EMERGENT_LLM_KEY:
        return None
    
    try:
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
            result = await stt.transcribe(
                file_path=temp_path,
                model="whisper-1",
                response_format="verbose_json"
            )
            
            if isinstance(result, dict):
                return result.get("text", "")
            return str(result) if result else ""
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return None

# ============== REST Endpoints ==============

@router.get("/status")
async def get_realtime_stt_status(request: Request):
    """Check real-time STT service status and capabilities"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "available": bool(EMERGENT_LLM_KEY),
        "model": "whisper-1",
        "features": {
            "streaming": True,
            "real_time": True,
            "languages": ["en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"],
            "max_chunk_duration_seconds": 30,
            "supported_formats": ["webm", "wav", "mp3", "m4a", "ogg"]
        },
        "websocket_endpoint": "/api/realtime-stt/stream",
        "active_sessions": len(active_connections)
    }

@router.post("/transcribe")
async def transcribe_audio_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = "en"
):
    """Transcribe an audio file (non-streaming)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="STT service not configured")
    
    # Check file size (max 25MB)
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max size is 25MB")
    
    # Save to temp file
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
        result = await stt.transcribe(
            file_path=temp_path,
            model="whisper-1",
            language=language if language != "auto" else None,
            response_format="verbose_json"
        )
        
        text = ""
        duration = 0.0
        words = []
        
        if isinstance(result, dict):
            text = result.get("text", "")
            duration = result.get("duration", 0.0)
            words = result.get("words", [])
        else:
            text = str(result) if result else ""
        
        # Save transcription to history
        transcription_record = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "text": text,
            "duration_seconds": duration,
            "word_count": len(text.split()),
            "language": language,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.transcription_history.insert_one(transcription_record)
        
        return {
            "success": True,
            "transcription": {
                "text": text,
                "duration_seconds": duration,
                "word_count": len(text.split()),
                "words": words[:50],  # First 50 words with timestamps
                "language": language
            }
        }
        
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/transcribe-base64")
async def transcribe_audio_base64(request: Request):
    """Transcribe audio from base64 encoded data"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="STT service not configured")
    
    body = await request.json()
    audio_base64 = body.get("audio")
    format = body.get("format", "webm")
    language = body.get("language", "en")
    
    if not audio_base64:
        raise HTTPException(status_code=400, detail="Missing audio data")
    
    try:
        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
            result = await stt.transcribe(
                file_path=temp_path,
                model="whisper-1",
                language=language if language != "auto" else None,
                response_format="verbose_json"
            )
            
            text = ""
            duration = 0.0
            
            if isinstance(result, dict):
                text = result.get("text", "")
                duration = result.get("duration", 0.0)
            else:
                text = str(result) if result else ""
            
            return {
                "success": True,
                "text": text,
                "duration_seconds": duration,
                "word_count": len(text.split()),
                "is_final": True
            }
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logging.error(f"Base64 transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/history")
async def get_transcription_history(request: Request, limit: int = 20):
    """Get user's transcription history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    cursor = db.transcription_history.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    
    history = await cursor.to_list(length=limit)
    
    return {
        "history": history,
        "count": len(history)
    }

@router.delete("/history/{transcription_id}")
async def delete_transcription(transcription_id: str, request: Request):
    """Delete a transcription from history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.transcription_history.delete_one({
        "id": transcription_id,
        "user_id": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return {"success": True, "message": "Transcription deleted"}

# ============== WebSocket Endpoint for Streaming ==============

@router.websocket("/stream")
async def websocket_transcription(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription.
    
    Client sends: base64 encoded audio chunks
    Server responds: transcription results
    
    Protocol:
    1. Client connects
    2. Client sends JSON: {"type": "start", "token": "<jwt_token>", "language": "en"}
    3. Client sends JSON: {"type": "audio", "data": "<base64_audio>", "format": "webm"}
    4. Server responds: {"type": "transcription", "text": "...", "is_final": false}
    5. Client sends JSON: {"type": "stop"}
    6. Server responds: {"type": "final", "text": "...", "duration": 0.0}
    """
    await websocket.accept()
    
    session_id = str(uuid.uuid4())
    user_id = None
    full_transcription = ""
    audio_buffer = bytearray()
    language = "en"
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "start":
                # Authenticate user
                token = data.get("token")
                language = data.get("language", "en")
                
                if not token:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Authentication required"
                    })
                    break
                
                # Verify token (simplified - in production use proper JWT validation)
                from routes.auth import verify_token
                try:
                    payload = verify_token(token)
                    user_id = payload.get("sub")
                    
                    active_connections[session_id] = websocket
                    
                    await websocket.send_json({
                        "type": "ready",
                        "session_id": session_id,
                        "message": "Ready to receive audio"
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid token"
                    })
                    break
            
            elif msg_type == "audio":
                if not user_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Not authenticated"
                    })
                    continue
                
                audio_base64 = data.get("data")
                audio_format = data.get("format", "webm")
                
                if audio_base64:
                    try:
                        audio_chunk = base64.b64decode(audio_base64)
                        audio_buffer.extend(audio_chunk)
                        
                        # Transcribe when buffer reaches ~1 second of audio (about 16KB for webm)
                        if len(audio_buffer) >= 16000:
                            transcription = await transcribe_audio_chunk(
                                bytes(audio_buffer), 
                                audio_format
                            )
                            
                            if transcription:
                                full_transcription += " " + transcription
                                await websocket.send_json({
                                    "type": "transcription",
                                    "text": transcription,
                                    "full_text": full_transcription.strip(),
                                    "is_final": False
                                })
                            
                            audio_buffer.clear()
                            
                    except Exception as e:
                        logging.error(f"Audio processing error: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Audio processing error: {str(e)}"
                        })
            
            elif msg_type == "stop":
                # Process remaining audio in buffer
                if audio_buffer:
                    transcription = await transcribe_audio_chunk(bytes(audio_buffer), "webm")
                    if transcription:
                        full_transcription += " " + transcription
                
                # Send final result
                await websocket.send_json({
                    "type": "final",
                    "text": full_transcription.strip(),
                    "word_count": len(full_transcription.split()),
                    "session_id": session_id
                })
                
                # Save to history if user is authenticated
                if user_id and full_transcription.strip():
                    await db.transcription_history.insert_one({
                        "id": session_id,
                        "user_id": user_id,
                        "text": full_transcription.strip(),
                        "word_count": len(full_transcription.split()),
                        "language": language,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "type": "realtime"
                    })
                
                break
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        if session_id in active_connections:
            del active_connections[session_id]
