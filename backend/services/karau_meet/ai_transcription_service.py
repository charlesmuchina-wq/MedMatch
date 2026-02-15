"""
AI KARAU Meeting - AI Transcription & Summary Service
Uses OpenAI Whisper for transcription and GPT-5.2 for summaries
"""

import os
import uuid
import json
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
transcripts = db.karau_transcripts
meeting_summaries = db.karau_meeting_summaries
action_items = db.karau_action_items


# ============ AUDIO TRANSCRIPTION (OpenAI Whisper) ============

async def transcribe_audio(
    audio_data: bytes,
    meeting_id: str,
    speaker_id: str = None,
    speaker_name: str = "Unknown",
    language: str = "en",
    file_format: str = "webm"
) -> Dict:
    """
    Transcribe audio using OpenAI Whisper
    
    Args:
        audio_data: Raw audio bytes
        meeting_id: Meeting identifier
        speaker_id: Speaker's user ID
        speaker_name: Speaker's display name
        language: ISO-639-1 language code
        file_format: Audio format (webm, mp3, wav, etc.)
    
    Returns:
        Dict with transcribed text and metadata
    """
    try:
        from emergentintegrations.llm.openai import OpenAISpeechToText
        
        if not EMERGENT_LLM_KEY:
            logger.warning("EMERGENT_LLM_KEY not configured, using mock transcription")
            return await _mock_transcription(meeting_id, speaker_id, speaker_name)
        
        stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
        
        # Create a temporary file-like object for the API
        import io
        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"audio.{file_format}"
        
        # Transcribe with Whisper
        response = await stt.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            language=language,
            temperature=0.0,
            timestamp_granularities=["segment"]
        )
        
        # Create transcript entry
        transcript_entry = {
            "transcript_id": str(uuid.uuid4())[:12],
            "meeting_id": meeting_id,
            "speaker_id": speaker_id,
            "speaker_name": speaker_name,
            "text": response.text,
            "language": language,
            "segments": [],
            "confidence": 1.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": 0
        }
        
        # Extract segments if available
        if hasattr(response, 'segments') and response.segments:
            transcript_entry["segments"] = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                }
                for seg in response.segments
            ]
            if response.segments:
                transcript_entry["duration_seconds"] = response.segments[-1].end
        
        # Store in database
        await transcripts.insert_one(transcript_entry)
        
        # Remove MongoDB _id before returning
        transcript_entry.pop("_id", None)
        
        logger.info(f"Transcribed {len(response.text)} chars for meeting {meeting_id}")
        
        return {
            "success": True,
            "transcript": transcript_entry
        }
        
    except ImportError:
        logger.error("emergentintegrations not installed")
        return await _mock_transcription(meeting_id, speaker_id, speaker_name)
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _mock_transcription(meeting_id: str, speaker_id: str, speaker_name: str) -> Dict:
    """Mock transcription for testing"""
    transcript_entry = {
        "transcript_id": str(uuid.uuid4())[:12],
        "meeting_id": meeting_id,
        "speaker_id": speaker_id,
        "speaker_name": speaker_name,
        "text": "[Mock transcription - Configure EMERGENT_LLM_KEY for real transcription]",
        "language": "en",
        "segments": [],
        "confidence": 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mock_mode": True
    }
    
    await transcripts.insert_one(transcript_entry)
    transcript_entry.pop("_id", None)
    
    return {
        "success": True,
        "transcript": transcript_entry,
        "mock_mode": True
    }


async def get_meeting_transcript(meeting_id: str) -> Dict:
    """Get full transcript for a meeting"""
    
    entries = await transcripts.find(
        {"meeting_id": meeting_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(length=1000)
    
    # Combine all transcript entries
    full_text = []
    speakers = set()
    
    for entry in entries:
        speaker = entry.get("speaker_name", "Unknown")
        text = entry.get("text", "")
        speakers.add(speaker)
        full_text.append(f"{speaker}: {text}")
    
    return {
        "meeting_id": meeting_id,
        "entries": entries,
        "full_transcript": "\n".join(full_text),
        "speakers": list(speakers),
        "entry_count": len(entries)
    }


# ============ AI MEETING SUMMARIES (GPT-5.2) ============

async def generate_meeting_summary(
    meeting_id: str,
    meeting_title: str = "Meeting",
    participants: List[str] = None
) -> Dict:
    """
    Generate an AI-powered meeting summary using GPT-5.2
    
    Args:
        meeting_id: Meeting identifier
        meeting_title: Title of the meeting
        participants: List of participant names
    
    Returns:
        Dict with summary, key points, and decisions
    """
    try:
        from emergentintegrations.llm.openai import LlmChat
        
        # Get the meeting transcript
        transcript_data = await get_meeting_transcript(meeting_id)
        full_transcript = transcript_data.get("full_transcript", "")
        
        if not full_transcript or full_transcript.strip() == "":
            return {
                "success": False,
                "error": "No transcript available for this meeting"
            }
        
        if not EMERGENT_LLM_KEY:
            logger.warning("EMERGENT_LLM_KEY not configured, using mock summary")
            return await _mock_summary(meeting_id, meeting_title, participants or [])
        
        llm = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        # Create the prompt for summary generation
        prompt = f"""You are an AI meeting assistant. Analyze the following meeting transcript and provide:
1. A concise summary (2-3 paragraphs)
2. Key discussion points (bullet points)
3. Decisions made (bullet points)
4. Action items with assignees if mentioned (bullet points)
5. Follow-up topics for next meeting (if any)

Meeting Title: {meeting_title}
Participants: {', '.join(participants or transcript_data.get('speakers', []))}

Transcript:
{full_transcript[:8000]}  # Limit to avoid token limits

Please format your response as JSON with the following structure:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "decisions": ["decision 1", "decision 2", ...],
    "action_items": [{{"task": "...", "assignee": "...", "deadline": "..."}}],
    "follow_ups": ["topic 1", "topic 2", ...]
}}
"""
        
        # Generate summary with GPT-5.2
        response = await llm.chat_completion(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a professional meeting summarizer. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse the response
        response_text = response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            summary_data = json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Fallback: use raw text as summary
            summary_data = {
                "summary": response_text,
                "key_points": [],
                "decisions": [],
                "action_items": [],
                "follow_ups": []
            }
        
        # Create summary record
        summary_record = {
            "summary_id": str(uuid.uuid4())[:12],
            "meeting_id": meeting_id,
            "meeting_title": meeting_title,
            "participants": participants or transcript_data.get("speakers", []),
            "summary": summary_data.get("summary", ""),
            "key_points": summary_data.get("key_points", []),
            "decisions": summary_data.get("decisions", []),
            "action_items": summary_data.get("action_items", []),
            "follow_ups": summary_data.get("follow_ups", []),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "transcript_length": len(full_transcript),
            "model": "gpt-5.2"
        }
        
        # Store in database
        await meeting_summaries.update_one(
            {"meeting_id": meeting_id},
            {"$set": summary_record},
            upsert=True
        )
        
        logger.info(f"Generated summary for meeting {meeting_id}")
        
        return {
            "success": True,
            "summary": summary_record
        }
        
    except ImportError:
        logger.error("emergentintegrations not installed")
        return await _mock_summary(meeting_id, meeting_title, participants or [])
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _mock_summary(meeting_id: str, meeting_title: str, participants: List[str]) -> Dict:
    """Mock summary for testing"""
    summary_record = {
        "summary_id": str(uuid.uuid4())[:12],
        "meeting_id": meeting_id,
        "meeting_title": meeting_title,
        "participants": participants,
        "summary": "[Mock summary - Configure EMERGENT_LLM_KEY for AI-powered summaries]",
        "key_points": ["Key point 1", "Key point 2"],
        "decisions": ["Decision 1"],
        "action_items": [{"task": "Sample task", "assignee": "TBD", "deadline": "TBD"}],
        "follow_ups": ["Follow-up topic"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mock_mode": True
    }
    
    await meeting_summaries.update_one(
        {"meeting_id": meeting_id},
        {"$set": summary_record},
        upsert=True
    )
    
    return {
        "success": True,
        "summary": summary_record,
        "mock_mode": True
    }


async def get_meeting_summary(meeting_id: str) -> Optional[Dict]:
    """Get summary for a meeting"""
    
    summary = await meeting_summaries.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    
    return summary


# ============ ACTION ITEM EXTRACTION ============

async def extract_action_items(
    meeting_id: str,
    transcript_text: str = None
) -> Dict:
    """
    Extract action items from meeting transcript using GPT-5.2
    
    Args:
        meeting_id: Meeting identifier
        transcript_text: Optional transcript text (will fetch if not provided)
    
    Returns:
        Dict with extracted action items
    """
    try:
        from emergentintegrations.llm.openai import LlmChat
        
        # Get transcript if not provided
        if not transcript_text:
            transcript_data = await get_meeting_transcript(meeting_id)
            transcript_text = transcript_data.get("full_transcript", "")
        
        if not transcript_text:
            return {
                "success": False,
                "error": "No transcript available"
            }
        
        if not EMERGENT_LLM_KEY:
            return {
                "success": True,
                "action_items": [],
                "mock_mode": True
            }
        
        llm = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        prompt = f"""Extract action items from this meeting transcript. For each action item, identify:
1. The task description
2. The assignee (who should do it)
3. The deadline or timeframe (if mentioned)
4. Priority (high/medium/low based on context)

Transcript:
{transcript_text[:6000]}

Respond with a JSON array of action items:
[
    {{"task": "...", "assignee": "...", "deadline": "...", "priority": "..."}}
]
"""
        
        response = await llm.chat_completion(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You extract action items from meeting transcripts. Always respond with valid JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        
        response_text = response.choices[0].message.content
        
        # Parse action items
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            items = json.loads(response_text.strip())
            if not isinstance(items, list):
                items = []
        except json.JSONDecodeError:
            items = []
        
        # Store action items
        for item in items:
            action_item = {
                "action_id": str(uuid.uuid4())[:12],
                "meeting_id": meeting_id,
                "task": item.get("task", ""),
                "assignee": item.get("assignee", "Unassigned"),
                "deadline": item.get("deadline", "Not specified"),
                "priority": item.get("priority", "medium"),
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "extracted_by_ai": True
            }
            await action_items.insert_one(action_item)
        
        return {
            "success": True,
            "action_items": items,
            "count": len(items)
        }
        
    except Exception as e:
        logger.error(f"Action item extraction error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_action_items(meeting_id: str) -> List[Dict]:
    """Get action items for a meeting"""
    
    items = await action_items.find(
        {"meeting_id": meeting_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(length=100)
    
    return items


async def update_action_item_status(
    action_id: str,
    status: str,
    user_id: str
) -> Dict:
    """Update action item status"""
    
    valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        return {"success": False, "error": f"Invalid status. Use: {valid_statuses}"}
    
    result = await action_items.update_one(
        {"action_id": action_id},
        {"$set": {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": user_id
        }}
    )
    
    if result.modified_count == 0:
        return {"success": False, "error": "Action item not found"}
    
    return {"success": True, "status": status}
