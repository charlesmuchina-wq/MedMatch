"""
Meeting Recording Transcription Service
Uses OpenAI Whisper via Emergent LLM Key for speech-to-text.
Auto-triggers after cloud upload.
"""
import os
import asyncio
import logging
import tempfile
from datetime import datetime, timezone

from emergentintegrations.llm.openai import OpenAISpeechToText
from services.object_storage import get_object

logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")


async def transcribe_recording(storage_path: str, content_type: str = "video/webm") -> dict:
    """Transcribe a recording stored in cloud storage using Whisper."""
    if not EMERGENT_KEY:
        return {"error": "No LLM key configured", "text": ""}

    try:
        data, _ = get_object(storage_path)

        ext = "webm"
        if "mp4" in content_type:
            ext = "mp4"
        elif "mp3" in content_type:
            ext = "mp3"
        elif "wav" in content_type:
            ext = "wav"

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=True) as tmp:
            tmp.write(data)
            tmp.flush()

            stt = OpenAISpeechToText(api_key=EMERGENT_KEY)
            with open(tmp.name, "rb") as audio_file:
                response = await stt.transcribe(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    language="en",
                    prompt="This is a professional meeting discussion.",
                    timestamp_granularities=["segment"]
                )

        segments = []
        if hasattr(response, "segments"):
            for seg in response.segments:
                segments.append({
                    "start": round(seg.start, 1),
                    "end": round(seg.end, 1),
                    "text": seg.text.strip()
                })

        return {
            "text": response.text if hasattr(response, "text") else str(response),
            "segments": segments,
            "language": getattr(response, "language", "en"),
            "duration": getattr(response, "duration", 0),
            "transcribed_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return {"error": str(e), "text": "", "segments": []}


async def auto_transcribe_and_store(recording_id: str, storage_path: str, content_type: str, db):
    """Background task: transcribe and store result in recording document."""
    try:
        logger.info(f"Starting auto-transcription for {recording_id}")

        await db.karau_recordings.update_one(
            {"recording_id": recording_id},
            {"$set": {"transcription_status": "processing"}}
        )

        result = await transcribe_recording(storage_path, content_type)

        if result.get("error"):
            await db.karau_recordings.update_one(
                {"recording_id": recording_id},
                {"$set": {
                    "transcription_status": "failed",
                    "transcription_error": result["error"]
                }}
            )
            logger.error(f"Transcription failed for {recording_id}: {result['error']}")
        else:
            await db.karau_recordings.update_one(
                {"recording_id": recording_id},
                {"$set": {
                    "transcription": result,
                    "transcription_status": "completed"
                }}
            )
            logger.info(f"Transcription completed for {recording_id}: {len(result.get('text', ''))} chars")

    except Exception as e:
        logger.error(f"Auto-transcription error for {recording_id}: {e}")
        await db.karau_recordings.update_one(
            {"recording_id": recording_id},
            {"$set": {"transcription_status": "failed", "transcription_error": str(e)}}
        )
