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
    result = await get_ai_answer(req.meeting_id, req.question)
    return {"answer": result["answer"], "follow_up_suggestions": result.get("follow_up_suggestions", []), "meeting_id": req.meeting_id}


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


@router.get("/ai-assistant/insights/{meeting_id}")
async def get_insights(meeting_id: str, user: dict = Depends(require_auth)):
    """Get structured meeting insights (action items, key points, topics)."""
    from services.karau_meet.ai_assistant_service import get_meeting_insights
    return await get_meeting_insights(meeting_id)


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


# ===== Agentic AI Features =====

class ResearchRequest(BaseModel):
    meeting_id: str
    topic: str
    context: str = ""


class VoiceCommandRequest(BaseModel):
    meeting_id: str
    command_text: str
    webinar_id: Optional[str] = None


class SentimentSegment(BaseModel):
    meeting_id: str
    text: str
    speaker: str = "Unknown"


class PredictScheduleRequest(BaseModel):
    participants: List[str] = []
    duration_minutes: int = 30
    meeting_type: str = "general"
    timezone: str = "UTC"


class ActionItemAssign(BaseModel):
    meeting_id: str
    action_item: str
    assignee: str
    due_date: Optional[str] = None


@router.post("/ai-agent/research")
async def ai_research_topic(req: ResearchRequest, user: dict = Depends(require_auth)):
    """Agentic AI researches a topic in real-time during a meeting."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    chat = _make_chat(
        f"research-{req.meeting_id}-{req.topic[:20]}",
        "You are an AI research agent in a live meeting. Provide concise, factual, well-structured research on the requested topic. Include key statistics, recent developments, and actionable insights. Keep responses under 300 words. Format with bullet points for clarity."
    )

    prompt = f"Research this topic for our live meeting discussion:\nTopic: {req.topic}"
    if req.context:
        prompt += f"\nMeeting context: {req.context}"

    result = await chat.send_message(UserMessage(text=prompt))
    research_text = result if isinstance(result, str) else str(result)

    # Store research in meeting record
    await db.karau_meetings.update_one(
        {"meeting_id": req.meeting_id},
        {"$push": {"ai_research": {
            "topic": req.topic,
            "result": research_text,
            "requested_by": user["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }}},
        upsert=True
    )

    return {
        "research": research_text,
        "topic": req.topic,
        "follow_up_suggestions": [
            f"What are the risks of {req.topic}?",
            f"How does {req.topic} compare to alternatives?",
            f"What are the latest trends in {req.topic}?"
        ]
    }


@router.post("/ai-agent/assign-action")
async def assign_action_item(req: ActionItemAssign, user: dict = Depends(require_auth)):
    """AI auto-assigns an action item to a participant."""
    action = {
        "action_id": str(__import__('uuid').uuid4())[:8].upper(),
        "action_item": req.action_item,
        "assignee": req.assignee,
        "assigned_by": user.get("name", user["user_id"]),
        "due_date": req.due_date,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.karau_meetings.update_one(
        {"meeting_id": req.meeting_id},
        {"$push": {"action_items": action}},
        upsert=True
    )
    return {"success": True, "action": action}


@router.get("/ai-agent/actions/{meeting_id}")
async def get_action_items(meeting_id: str, user: dict = Depends(require_auth)):
    """Get all action items for a meeting."""
    meeting = await db.karau_meetings.find_one(
        {"meeting_id": meeting_id}, {"_id": 0, "action_items": 1}
    )
    return {"action_items": meeting.get("action_items", []) if meeting else []}


@router.post("/voice-command/execute")
async def execute_voice_command(req: VoiceCommandRequest, user: dict = Depends(require_auth)):
    """Parse and execute a voice command using AI."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    chat = _make_chat(
        f"voice-cmd-{req.meeting_id}",
        """You are a voice command parser for a video meeting platform. Parse the user's natural language command and return a JSON response.

Supported commands:
- {"action": "mute_all"} - Mute all participants
- {"action": "unmute_all"} - Unmute all
- {"action": "start_recording"} - Start recording
- {"action": "stop_recording"} - Stop recording
- {"action": "summarize", "params": {"minutes": N}} - Summarize last N minutes
- {"action": "schedule_followup", "params": {"topic": "...", "duration": N}} - Schedule a follow-up
- {"action": "set_timer", "params": {"minutes": N, "label": "..."}} - Set a timer
- {"action": "search", "params": {"query": "..."}} - Research a topic
- {"action": "assign_action", "params": {"task": "...", "assignee": "..."}} - Assign an action item
- {"action": "toggle_captions"} - Toggle live captions
- {"action": "end_meeting"} - End the meeting
- {"action": "unknown", "params": {"original": "..."}} - Unrecognized command

Return ONLY valid JSON. No explanation."""
    )

    result = await chat.send_message(UserMessage(text=req.command_text))
    result_text = result if isinstance(result, str) else str(result)

    try:
        import json
        parsed = json.loads(result_text.strip().strip("```json").strip("```"))
    except Exception:
        parsed = {"action": "unknown", "params": {"original": req.command_text}}

    # Store command log
    await db.karau_meetings.update_one(
        {"meeting_id": req.meeting_id},
        {"$push": {"voice_commands": {
            "command": req.command_text,
            "parsed": parsed,
            "user_id": user["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }}},
        upsert=True
    )

    return {
        "command": parsed,
        "original_text": req.command_text,
        "executed": parsed.get("action") != "unknown"
    }


@router.post("/sentiment/analyze")
async def analyze_sentiment(req: SentimentSegment, user: dict = Depends(require_auth)):
    """Analyze sentiment and engagement from a transcript segment."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    chat = _make_chat(
        f"sentiment-{req.meeting_id}",
        """Analyze the sentiment and engagement level of this meeting transcript segment. Return ONLY valid JSON:
{
  "sentiment": "positive"|"neutral"|"negative"|"confused"|"excited",
  "engagement_level": 1-10,
  "energy": "high"|"medium"|"low",
  "key_emotion": "focused"|"enthusiastic"|"bored"|"frustrated"|"curious"|"agreeable",
  "alert": null or "Engagement dropping - consider a break" or "High energy - good time for decisions"
}"""
    )

    result = await chat.send_message(
        UserMessage(text=f"Speaker: {req.speaker}\nText: \"{req.text}\"")
    )
    result_text = result if isinstance(result, str) else str(result)

    try:
        import json
        parsed = json.loads(result_text.strip().strip("```json").strip("```"))
    except Exception:
        parsed = {"sentiment": "neutral", "engagement_level": 5, "energy": "medium", "key_emotion": "focused", "alert": None}

    # Store sentiment data
    await db.karau_meetings.update_one(
        {"meeting_id": req.meeting_id},
        {"$push": {"sentiment_log": {
            **parsed,
            "speaker": req.speaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }}},
        upsert=True
    )

    return parsed


@router.get("/sentiment/dashboard/{meeting_id}")
async def get_sentiment_dashboard(meeting_id: str, user: dict = Depends(require_auth)):
    """Get real-time engagement and sentiment dashboard for a meeting."""
    meeting = await db.karau_meetings.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0, "sentiment_log": 1, "action_items": 1, "ai_research": 1}
    )
    if not meeting:
        return {"engagement_score": 0, "sentiment_log": [], "action_items": [], "alerts": []}

    log = meeting.get("sentiment_log", [])
    recent = log[-10:] if log else []

    # Calculate aggregate metrics
    avg_engagement = sum(s.get("engagement_level", 5) for s in recent) / len(recent) if recent else 5
    energy_counts = {}
    for s in recent:
        e = s.get("energy", "medium")
        energy_counts[e] = energy_counts.get(e, 0) + 1
    dominant_energy = max(energy_counts, key=energy_counts.get) if energy_counts else "medium"

    # Generate alerts
    alerts = []
    if avg_engagement < 4:
        alerts.append({"type": "warning", "message": "Engagement dropping - consider a break or interactive activity"})
    elif avg_engagement > 8:
        alerts.append({"type": "positive", "message": "High engagement - great time for key decisions"})

    sentiment_counts = {}
    for s in recent:
        sent = s.get("sentiment", "neutral")
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
    if sentiment_counts.get("confused", 0) > 2:
        alerts.append({"type": "warning", "message": "Multiple confused signals detected - consider clarifying"})

    return {
        "engagement_score": round(avg_engagement, 1),
        "dominant_energy": dominant_energy,
        "sentiment_breakdown": sentiment_counts,
        "alerts": alerts,
        "recent_log": recent,
        "action_items_count": len(meeting.get("action_items", [])),
        "research_count": len(meeting.get("ai_research", []))
    }


@router.post("/scheduling/predict")
async def predict_optimal_schedule(req: PredictScheduleRequest, user: dict = Depends(require_auth)):
    """AI predicts optimal meeting times based on patterns."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    # Get user's recent meeting history for pattern analysis
    recent_meetings = await db.karau_meetings.find(
        {"host_id": user["user_id"]},
        {"_id": 0, "scheduled_time": 1, "duration": 1, "engagement_score": 1}
    ).sort("scheduled_time", -1).limit(20).to_list(20)

    history_summary = "No previous meeting data" if not recent_meetings else f"{len(recent_meetings)} recent meetings found"

    chat = _make_chat(
        f"schedule-{user['user_id']}",
        """You are a scheduling AI. Based on meeting patterns, suggest 3 optimal meeting times. Return ONLY valid JSON:
{
  "suggestions": [
    {"day": "Monday", "time": "10:00", "reason": "High team energy after weekend"},
    {"day": "Wednesday", "time": "14:00", "reason": "Mid-week check-in, post-lunch focus"},
    {"day": "Friday", "time": "09:00", "reason": "Early wrap-up before weekend"}
  ],
  "avoid": [
    {"day": "Monday", "time": "08:00", "reason": "Low engagement typically on Monday mornings"}
  ],
  "tips": ["Keep stand-ups under 15 min", "Schedule deep-work discussions before lunch"]
}"""
    )

    result = await chat.send_message(
        UserMessage(text=f"Meeting type: {req.meeting_type}\nDuration: {req.duration_minutes}min\nTimezone: {req.timezone}\nParticipants: {len(req.participants)}\nHistory: {history_summary}")
    )
    result_text = result if isinstance(result, str) else str(result)

    try:
        import json
        parsed = json.loads(result_text.strip().strip("```json").strip("```"))
    except Exception:
        parsed = {
            "suggestions": [
                {"day": "Tuesday", "time": "10:00", "reason": "Optimal mid-morning focus"},
                {"day": "Thursday", "time": "14:00", "reason": "Post-lunch collaborative window"},
                {"day": "Wednesday", "time": "09:30", "reason": "Mid-week planning alignment"}
            ],
            "avoid": [],
            "tips": ["Schedule important decisions for mid-morning when focus is highest"]
        }

    return parsed



# ===== AI Meeting Coach =====

class CoachRequest(BaseModel):
    meeting_id: str
    transcript_segment: str = ""
    speaker: str = ""
    speaking_duration_seconds: float = 0
    total_meeting_seconds: float = 0
    engagement_score: float = 5.0
    participant_count: int = 2


@router.post("/ai-coach/tip")
async def get_coaching_tip(req: CoachRequest, user: dict = Depends(require_auth)):
    """AI Meeting Coach provides real-time private tips to the presenter/host."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    chat = _make_chat(
        f"coach-{req.meeting_id}",
        """You are an AI Meeting Coach providing real-time, private coaching tips to a meeting presenter. Analyze the context and provide ONE actionable coaching tip. Return ONLY valid JSON:
{
  "tip": "Consider asking participants for their input - you've been presenting for a while",
  "category": "engagement"|"pacing"|"clarity"|"energy"|"interaction"|"time_management",
  "urgency": "low"|"medium"|"high",
  "emoji": "an appropriate single emoji character"
}
Be specific, constructive, and brief. Only flag genuine improvement opportunities."""
    )

    context = f"""Meeting context:
- Speaker: {req.speaker}
- Speaking duration: {req.speaking_duration_seconds}s continuously
- Total meeting time: {req.total_meeting_seconds}s
- Current engagement score: {req.engagement_score}/10
- Participants: {req.participant_count}
- Latest transcript: "{req.transcript_segment[:300]}" """

    result = await chat.send_message(UserMessage(text=context))
    result_text = result if isinstance(result, str) else str(result)

    try:
        import json
        parsed = json.loads(result_text.strip().strip("```json").strip("```"))
    except Exception:
        parsed = {"tip": "Keep up the good work!", "category": "engagement", "urgency": "low", "emoji": ""}

    await db.karau_meetings.update_one(
        {"meeting_id": req.meeting_id},
        {"$push": {"coach_tips": {
            **parsed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": {"engagement": req.engagement_score, "duration": req.speaking_duration_seconds}
        }}},
        upsert=True
    )

    return parsed


@router.get("/ai-coach/report/{meeting_id}")
async def get_coach_report(meeting_id: str, user: dict = Depends(require_auth)):
    """Get post-meeting coaching summary report."""
    from services.karau_meet.ai_assistant_service import _make_chat
    from emergentintegrations.llm.chat import UserMessage

    meeting = await db.karau_meetings.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0, "coach_tips": 1, "sentiment_log": 1, "action_items": 1}
    )
    if not meeting or not meeting.get("coach_tips"):
        return {"report": "No coaching data available for this meeting.", "tips_count": 0, "areas": []}

    tips = meeting.get("coach_tips", [])
    sentiments = meeting.get("sentiment_log", [])

    categories = {}
    for t in tips:
        cat = t.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    chat = _make_chat(
        f"coach-report-{meeting_id}",
        "You are an AI Meeting Coach. Generate a brief, constructive post-meeting coaching report. Be encouraging but honest. Under 200 words."
    )

    summary_input = f"Tips given: {len(tips)}. Categories: {categories}. Avg engagement: {sum(s.get('engagement_level', 5) for s in sentiments[-10:]) / max(len(sentiments[-10:]), 1):.1f}/10. Action items: {len(meeting.get('action_items', []))}."

    result = await chat.send_message(UserMessage(text=summary_input))
    report_text = result if isinstance(result, str) else str(result)

    return {
        "report": report_text,
        "tips_count": len(tips),
        "areas": [{"category": k, "count": v} for k, v in sorted(categories.items(), key=lambda x: -x[1])],
        "improvement_focus": max(categories, key=categories.get) if categories else "none"
    }
