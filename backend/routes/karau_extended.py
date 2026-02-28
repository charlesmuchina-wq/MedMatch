"""
AI KARAU Extended Features:
- Real-time translation
- AI Meeting Assistant  
- CRM Webhook Integration
- Industry Meeting Templates
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from utils.database import db
from routes.auth import require_auth

router = APIRouter(prefix="/karau-features", tags=["karau-features"])


# ===== Translation =====

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "en"


class TranslateBatchRequest(BaseModel):
    texts: List[str]
    target_lang: str
    source_lang: str = "en"


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation."""
    from services.karau_meet.translation_service import SUPPORTED_LANGUAGES
    return {"languages": [{"code": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()]}


@router.post("/translate")
async def translate_text_endpoint(req: TranslateRequest, user: dict = Depends(require_auth)):
    """Translate a single text."""
    from services.karau_meet.translation_service import translate_text
    translated = await translate_text(req.text, req.target_lang, req.source_lang)
    return {"translated_text": translated, "source_lang": req.source_lang, "target_lang": req.target_lang}


@router.post("/translate/batch")
async def translate_batch_endpoint(req: TranslateBatchRequest, user: dict = Depends(require_auth)):
    """Translate multiple texts at once."""
    from services.karau_meet.translation_service import translate_batch
    translations = await translate_batch(req.texts, req.target_lang, req.source_lang)
    return {"translations": translations, "target_lang": req.target_lang}


# ===== AI Meeting Assistant =====

class AskAssistantRequest(BaseModel):
    meeting_id: str
    question: str


class ProcessSegmentRequest(BaseModel):
    meeting_id: str
    segment: str
    speaker: str = "Unknown"


@router.post("/ai-assistant/ask")
async def ask_ai_assistant(req: AskAssistantRequest, user: dict = Depends(require_auth)):
    """Ask the AI assistant a question about the meeting."""
    from services.karau_meet.ai_assistant_service import get_ai_answer
    answer = await get_ai_answer(req.meeting_id, req.question)
    return {"answer": answer, "meeting_id": req.meeting_id}


@router.post("/ai-assistant/process-segment")
async def process_segment(req: ProcessSegmentRequest, user: dict = Depends(require_auth)):
    """Process a transcript segment for insights."""
    from services.karau_meet.ai_assistant_service import process_transcript_segment
    result = await process_transcript_segment(req.meeting_id, req.segment, req.speaker)
    return {"insights": result}


@router.post("/ai-assistant/generate-summary/{meeting_id}")
async def generate_summary(meeting_id: str, user: dict = Depends(require_auth)):
    """Generate a comprehensive meeting summary."""
    from services.karau_meet.ai_assistant_service import generate_meeting_summary
    summary = await generate_meeting_summary(meeting_id)
    if summary:
        return {"summary": summary, "meeting_id": meeting_id}
    raise HTTPException(status_code=500, detail="Failed to generate summary")


# ===== CRM Webhook Integration =====

class WebhookConfig(BaseModel):
    webhook_url: str
    events: List[str] = ["meeting_ended", "meeting_created"]
    headers: dict = {}
    is_active: bool = True
    name: str = "Custom CRM"


@router.get("/webhooks")
async def get_webhooks(user: dict = Depends(require_auth)):
    """Get configured webhooks for the user's organization."""
    org_id = user.get("org_id")
    webhooks = await db.karau_webhooks.find(
        {"org_id": org_id} if org_id else {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(50)
    return {"webhooks": webhooks}


@router.post("/webhooks")
async def create_webhook(config: WebhookConfig, user: dict = Depends(require_auth)):
    """Configure a new webhook for CRM integration."""
    import uuid
    webhook = {
        "webhook_id": str(uuid.uuid4())[:8].upper(),
        "user_id": user["user_id"],
        "org_id": user.get("org_id"),
        "webhook_url": config.webhook_url,
        "events": config.events,
        "headers": config.headers,
        "is_active": config.is_active,
        "name": config.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_triggered": None,
        "trigger_count": 0
    }
    await db.karau_webhooks.insert_one(webhook)
    webhook.pop("_id", None)
    return webhook


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, user: dict = Depends(require_auth)):
    """Delete a webhook configuration."""
    result = await db.karau_webhooks.delete_one({"webhook_id": webhook_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"deleted": True}


@router.post("/webhooks/test/{webhook_id}")
async def test_webhook(webhook_id: str, user: dict = Depends(require_auth)):
    """Send a test payload to a webhook."""
    import httpx
    webhook = await db.karau_webhooks.find_one({"webhook_id": webhook_id}, {"_id": 0})
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    test_payload = {
        "event": "test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "meeting_id": "TEST-123",
            "title": "Test Meeting",
            "source": "AI KARAU"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                webhook["webhook_url"],
                json=test_payload,
                headers=webhook.get("headers", {})
            )
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_body": response.text[:200]
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== Industry Templates =====

INDUSTRY_TEMPLATES = [
    {
        "template_id": "interview-structured",
        "name": "Structured Interview",
        "industry": "HR / Recruitment",
        "description": "Structured interview with AI scoring, time-boxed sections, and automated candidate evaluation.",
        "icon": "users",
        "settings": {
            "ai_notes": True,
            "recording": True,
            "noise_cancellation": True,
            "auto_captions": True,
            "max_duration_minutes": 60,
            "sections": [
                {"name": "Introduction", "duration": 5},
                {"name": "Technical Questions", "duration": 25},
                {"name": "Behavioral Questions", "duration": 20},
                {"name": "Q&A", "duration": 10}
            ]
        }
    },
    {
        "template_id": "product-demo",
        "name": "Product Demo",
        "industry": "Sales",
        "description": "Sales demo with screen sharing, real-time Q&A, and follow-up action items.",
        "icon": "monitor-play",
        "settings": {
            "ai_notes": True,
            "recording": True,
            "screen_sharing_default": True,
            "noise_cancellation": True,
            "max_duration_minutes": 45,
            "sections": [
                {"name": "Introduction & Agenda", "duration": 5},
                {"name": "Product Walkthrough", "duration": 25},
                {"name": "Q&A", "duration": 10},
                {"name": "Next Steps", "duration": 5}
            ]
        }
    },
    {
        "template_id": "clinical-review",
        "name": "Clinical Case Review",
        "industry": "Healthcare / Life Sciences",
        "description": "HIPAA-compliant clinical review with structured documentation and multi-language support.",
        "icon": "heart-pulse",
        "settings": {
            "ai_notes": True,
            "recording": True,
            "noise_cancellation": True,
            "auto_captions": True,
            "hipaa_mode": True,
            "max_duration_minutes": 90,
            "sections": [
                {"name": "Case Presentation", "duration": 15},
                {"name": "Lab Results Review", "duration": 20},
                {"name": "Discussion", "duration": 30},
                {"name": "Treatment Plan", "duration": 15},
                {"name": "Action Items", "duration": 10}
            ]
        }
    },
    {
        "template_id": "standup",
        "name": "Daily Standup",
        "industry": "Engineering",
        "description": "Quick daily sync with time-boxed updates per participant and auto-generated summary.",
        "icon": "zap",
        "settings": {
            "ai_notes": True,
            "recording": False,
            "noise_cancellation": True,
            "max_duration_minutes": 15,
            "sections": [
                {"name": "Yesterday", "duration": 5},
                {"name": "Today", "duration": 5},
                {"name": "Blockers", "duration": 5}
            ]
        }
    },
    {
        "template_id": "board-meeting",
        "name": "Board Meeting",
        "industry": "Corporate",
        "description": "Formal board meeting with agenda tracking, voting, and compliance recording.",
        "icon": "building-2",
        "settings": {
            "ai_notes": True,
            "recording": True,
            "noise_cancellation": True,
            "auto_captions": True,
            "max_duration_minutes": 120,
            "sections": [
                {"name": "Call to Order", "duration": 5},
                {"name": "Previous Minutes", "duration": 10},
                {"name": "Financial Review", "duration": 30},
                {"name": "Strategic Discussion", "duration": 40},
                {"name": "Voting", "duration": 15},
                {"name": "Adjournment", "duration": 5}
            ]
        }
    },
    {
        "template_id": "consultation",
        "name": "Client Consultation",
        "industry": "Professional Services",
        "description": "Client consultation with intake form, multi-language support, and follow-up scheduling.",
        "icon": "message-square",
        "settings": {
            "ai_notes": True,
            "recording": True,
            "noise_cancellation": True,
            "auto_captions": True,
            "max_duration_minutes": 60,
            "sections": [
                {"name": "Client Background", "duration": 10},
                {"name": "Needs Assessment", "duration": 20},
                {"name": "Solution Discussion", "duration": 20},
                {"name": "Next Steps", "duration": 10}
            ]
        }
    }
]


@router.get("/templates")
async def get_industry_templates():
    """Get available industry meeting templates."""
    return {"templates": INDUSTRY_TEMPLATES}


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID."""
    for t in INDUSTRY_TEMPLATES:
        if t["template_id"] == template_id:
            return t
    raise HTTPException(status_code=404, detail="Template not found")
