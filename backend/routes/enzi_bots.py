"""
ENZI Bot Store — Full Marketplace with AI-Powered Bot Actions
18 specialized bots across 4 categories:
  1. Job Toolkit (Recruitment & Job Seeker)
  2. AI Meeting Portal
  3. AI Messenger
  4. AI Quality & Security Audit
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
import logging

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

router = APIRouter(prefix="/lumi/bots", tags=["ENZI Bot Store"])

# ═══════════════════════════════════════════════════════════════
# BOT CATALOG — 18 Specialized Bots
# ═══════════════════════════════════════════════════════════════

BOT_CATALOG = {
    # ── Category 1: Job Toolkit ──
    "talent_matcher": {
        "name": "Talent Matcher",
        "description": "Analyzes 800M+ global profiles to find candidates matching natural language queries.",
        "icon": "user-search",
        "category": "Job Toolkit",
        "subcategory": "Recruitment",
        "featured": True,
        "default_config": {"search_scope": "global", "min_match_score": 75, "include_passive": True},
        "commands": ["/match <query>", "/talent-pool", "/shortlist"],
        "install_count": 3240,
        "rating": 4.8,
    },
    "resume_architect": {
        "name": "Resume & Cover Letter Architect",
        "description": "Generates tailored, ATS-optimized resumes and cover letters from a job link.",
        "icon": "file-text",
        "category": "Job Toolkit",
        "subcategory": "Job Seeker",
        "featured": True,
        "default_config": {"format": "modern", "ats_optimize": True, "language": "en"},
        "commands": ["/build-resume <job-url>", "/cover-letter", "/ats-check"],
        "install_count": 5180,
        "rating": 4.9,
    },
    "interview_copilot": {
        "name": "Interview Copilot",
        "description": "Real-time suggestions, speech-to-text practice, and feedback on filler words and body language.",
        "icon": "mic",
        "category": "Job Toolkit",
        "subcategory": "Job Seeker",
        "featured": False,
        "default_config": {"feedback_mode": "real-time", "track_fillers": True, "body_language": True},
        "commands": ["/mock-interview", "/practice", "/feedback"],
        "install_count": 2870,
        "rating": 4.7,
    },
    "ez_sourcing": {
        "name": "EZ Sourcing Agent",
        "description": "Autonomous multi-step sourcing with email verification and personalized outreach sequences.",
        "icon": "zap",
        "category": "Job Toolkit",
        "subcategory": "Recruitment",
        "featured": False,
        "default_config": {"auto_verify_email": True, "sequence_steps": 3, "follow_up_days": 3},
        "commands": ["/source <role>", "/outreach", "/sequence"],
        "install_count": 1950,
        "rating": 4.5,
    },
    "salary_negotiator": {
        "name": "Salary Negotiator",
        "description": "Analyzes thousands of listings to estimate fair compensation and runs mock negotiations.",
        "icon": "dollar-sign",
        "category": "Job Toolkit",
        "subcategory": "Job Seeker",
        "featured": False,
        "default_config": {"region": "US", "include_benefits": True, "mock_mode": True},
        "commands": ["/salary <role>", "/negotiate", "/benchmark"],
        "install_count": 2120,
        "rating": 4.6,
    },

    # ── Category 2: AI Meeting Portal ──
    "note_taker": {
        "name": "Automated Note-Taker",
        "description": "Records and transcribes meetings in real-time, extracting action items and key insights.",
        "icon": "edit",
        "category": "AI Meeting",
        "subcategory": "Transcription",
        "featured": True,
        "default_config": {"auto_record": True, "extract_actions": True, "language": "en"},
        "commands": ["/notes", "/action-items", "/transcript"],
        "install_count": 8920,
        "rating": 4.9,
    },
    "smart_scheduler": {
        "name": "Smart Scheduler",
        "description": "Syncs calendars, finds optimal meeting times, and sends automated invites and reminders.",
        "icon": "calendar",
        "category": "AI Meeting",
        "subcategory": "Scheduling",
        "featured": False,
        "default_config": {"calendar_sync": True, "auto_reminders": True, "buffer_minutes": 10},
        "commands": ["/schedule", "/find-time", "/remind"],
        "install_count": 4150,
        "rating": 4.7,
    },
    "search_copilot": {
        "name": "Search Copilot",
        "description": "Ask AI questions across past meeting transcripts and summaries to retrieve context.",
        "icon": "search",
        "category": "AI Meeting",
        "subcategory": "Intelligence",
        "featured": True,
        "default_config": {"search_depth": "all", "include_summaries": True},
        "commands": ["/ask <question>", "/find-meeting", "/recall"],
        "install_count": 3680,
        "rating": 4.8,
    },
    "attendance_tracker": {
        "name": "Attendance & Participation Tracker",
        "description": "Generates attendance sheets and analyzes participant engagement by tracking talk time.",
        "icon": "users",
        "category": "AI Meeting",
        "subcategory": "Analytics",
        "featured": False,
        "default_config": {"track_talk_time": True, "auto_sheet": True, "engagement_alerts": False},
        "commands": ["/attendance", "/engagement", "/report"],
        "install_count": 2340,
        "rating": 4.4,
    },
    "summary_generator": {
        "name": "Summary Generator",
        "description": "Converts full transcripts into 2-min highlight reels or structured summaries.",
        "icon": "brain",
        "category": "AI Meeting",
        "subcategory": "Intelligence",
        "featured": False,
        "default_config": {"format": "structured", "include_highlights": True, "auto_generate": True},
        "commands": ["/summarize", "/highlights", "/digest"],
        "install_count": 5470,
        "rating": 4.8,
    },

    # ── Category 3: AI Messenger ──
    "knowledge_layer": {
        "name": "Knowledge Layer Bot",
        "description": "Plugs into existing tools (Docs, Slack, Teams) to answer team questions using company-wide data.",
        "icon": "book-open",
        "category": "AI Messenger",
        "subcategory": "Knowledge",
        "featured": True,
        "default_config": {"sources": ["docs", "slack", "teams"], "auto_index": True},
        "commands": ["/ask <question>", "/index", "/sources"],
        "install_count": 6120,
        "rating": 4.9,
    },
    "multilingual_translator": {
        "name": "Multilingual Translator",
        "description": "Real-time bilingual transcription and translation for global team communication.",
        "icon": "globe",
        "category": "AI Messenger",
        "subcategory": "Communication",
        "featured": False,
        "default_config": {"target_language": "en", "auto_detect": True, "inline_translation": True},
        "commands": ["/translate <lang>", "/detect", "/toggle-auto"],
        "install_count": 4780,
        "rating": 4.7,
    },
    "omnichannel_assistant": {
        "name": "Omnichannel Assistant",
        "description": "Manages SMS, WhatsApp, and web chat from a single interface for consistent messaging.",
        "icon": "message-circle",
        "category": "AI Messenger",
        "subcategory": "Communication",
        "featured": False,
        "default_config": {"channels": ["sms", "whatsapp", "webchat"], "unified_inbox": True},
        "commands": ["/inbox", "/route <channel>", "/broadcast"],
        "install_count": 2890,
        "rating": 4.5,
    },

    # ── Category 4: AI Quality & Security Audit ──
    "compliance_audit": {
        "name": "AI Compliance Audit Bot",
        "description": "Checks against USA, EU, and UK regulations (HIPAA, GDPR), providing risk scores and PDF reports.",
        "icon": "shield",
        "category": "Security & QA",
        "subcategory": "Compliance",
        "featured": True,
        "default_config": {"frameworks": ["HIPAA", "GDPR", "SOC2"], "auto_scan": True, "report_format": "pdf"},
        "commands": ["/audit", "/risk-score", "/compliance-report"],
        "install_count": 3420,
        "rating": 4.8,
    },
    "visual_testing": {
        "name": "UI/UX Visual Testing Bot",
        "description": "Automated functional and visual testing to ensure consistent UX across devices.",
        "icon": "monitor",
        "category": "Security & QA",
        "subcategory": "Testing",
        "featured": False,
        "default_config": {"devices": ["desktop", "mobile", "tablet"], "auto_regression": True},
        "commands": ["/test-ui", "/screenshot-diff", "/regression"],
        "install_count": 1560,
        "rating": 4.3,
    },
    "bias_auditor": {
        "name": "Data Integrity & Bias Auditor",
        "description": "Scans recruitment datasets to identify hidden patterns, discrepancies, and potential bias.",
        "icon": "scale",
        "category": "Security & QA",
        "subcategory": "Compliance",
        "featured": False,
        "default_config": {"scan_frequency": "weekly", "bias_categories": ["gender", "age", "ethnicity"], "auto_alert": True},
        "commands": ["/audit-data", "/bias-report", "/fairness-score"],
        "install_count": 1890,
        "rating": 4.6,
    },
    "threat_scanner": {
        "name": "Threat & Conduct Scanner",
        "description": "Monitors communication for threats, scams, and inappropriate conduct using NLU.",
        "icon": "alert-triangle",
        "category": "Security & QA",
        "subcategory": "Security",
        "featured": False,
        "default_config": {"scan_mode": "realtime", "sensitivity": "medium", "auto_flag": True},
        "commands": ["/scan", "/threats", "/conduct-report"],
        "install_count": 2650,
        "rating": 4.7,
    },
    "translation_qa": {
        "name": "Translation QA Bot",
        "description": "Audits AI translations for accuracy, tone, and cultural context to prevent breakdowns.",
        "icon": "check-circle",
        "category": "Security & QA",
        "subcategory": "Testing",
        "featured": False,
        "default_config": {"check_tone": True, "check_cultural": True, "languages": ["es", "fr", "de", "ja", "zh"]},
        "commands": ["/qa-translate", "/tone-check", "/cultural-review"],
        "install_count": 1230,
        "rating": 4.4,
    },
}

CATEGORY_ORDER = ["Job Toolkit", "AI Meeting", "AI Messenger", "Security & QA"]

# Bot action definitions (UI buttons)
BOT_ACTIONS = {
    "talent_matcher": {"actions": [{"id": "match", "label": "Find Talent", "icon": "user-search"}]},
    "resume_architect": {"actions": [{"id": "build_resume", "label": "Build Resume", "icon": "file-text"}]},
    "interview_copilot": {"actions": [{"id": "mock_interview", "label": "Mock Interview", "icon": "mic"}]},
    "ez_sourcing": {"actions": [{"id": "source", "label": "Start Sourcing", "icon": "zap"}]},
    "salary_negotiator": {"actions": [{"id": "benchmark", "label": "Salary Benchmark", "icon": "dollar-sign"}]},
    "note_taker": {"actions": [{"id": "notes", "label": "Start Notes", "icon": "edit"}]},
    "smart_scheduler": {"actions": [{"id": "schedule", "label": "Schedule Meeting", "icon": "calendar"}]},
    "search_copilot": {"actions": [{"id": "ask", "label": "Ask AI", "icon": "search"}]},
    "attendance_tracker": {"actions": [{"id": "attendance", "label": "Attendance Report", "icon": "users"}]},
    "summary_generator": {"actions": [{"id": "summarize", "label": "Summarize", "icon": "brain"}]},
    "knowledge_layer": {"actions": [{"id": "ask", "label": "Ask Knowledge", "icon": "book-open"}]},
    "multilingual_translator": {"actions": [{"id": "translate", "label": "Translate", "icon": "globe"}]},
    "omnichannel_assistant": {"actions": [{"id": "inbox", "label": "Unified Inbox", "icon": "message-circle"}]},
    "compliance_audit": {"actions": [{"id": "audit", "label": "Run Audit", "icon": "shield"}]},
    "visual_testing": {"actions": [{"id": "test", "label": "Run UI Tests", "icon": "monitor"}]},
    "bias_auditor": {"actions": [{"id": "audit_data", "label": "Audit Data", "icon": "scale"}]},
    "threat_scanner": {"actions": [{"id": "scan", "label": "Scan Threats", "icon": "alert-triangle"}]},
    "translation_qa": {"actions": [{"id": "qa", "label": "QA Translations", "icon": "check-circle"}]},
}

# System prompts for each bot
BOT_SYSTEM_PROMPTS = {
    "talent_matcher": "You are Talent Matcher, an AI recruitment assistant. Analyze requirements and suggest ideal candidate profiles with match scores. Be specific about skills, experience levels, and sourcing strategies. Format with markdown. Keep responses concise (under 300 words).",
    "resume_architect": "You are Resume Architect, an ATS-optimization expert. Help create tailored resumes and cover letters. Provide actionable formatting tips and keyword suggestions. Format with markdown. Keep responses concise (under 300 words).",
    "interview_copilot": "You are Interview Copilot, a mock interview coach. Generate realistic interview questions, provide feedback on answers, and coach on communication skills. Format with markdown. Keep responses concise (under 300 words).",
    "ez_sourcing": "You are EZ Sourcing Agent, an autonomous recruitment sourcer. Create multi-step outreach sequences, suggest sourcing channels, and draft personalized messages. Format with markdown. Keep responses concise (under 300 words).",
    "salary_negotiator": "You are Salary Negotiator, a compensation analysis expert. Provide market benchmarks, negotiation scripts, and total compensation breakdowns. Format with markdown. Keep responses concise (under 300 words).",
    "note_taker": "You are Automated Note-Taker. Analyze the conversation and extract key discussion points, action items, decisions made, and follow-ups needed. Format as a structured meeting notes document with markdown.",
    "smart_scheduler": "You are Smart Scheduler. Suggest optimal meeting times, draft agendas, and create reminder schedules. Be practical and consider timezone awareness. Format with markdown. Keep responses concise.",
    "search_copilot": "You are Search Copilot. Answer questions based on the conversation context provided. Cite specific messages when referencing past discussions. Format with markdown. Keep responses concise.",
    "attendance_tracker": "You are Attendance & Participation Tracker. Analyze conversation participants, their activity levels, and generate engagement reports. Format with markdown tables.",
    "summary_generator": "You are Summary Generator. Create structured summaries from conversations with sections: Key Points, Decisions, Action Items, and Next Steps. Format with markdown. Be concise but thorough.",
    "knowledge_layer": "You are Knowledge Layer Bot. Answer questions using the conversation context as your knowledge base. If the answer isn't in the context, say so. Be precise and cite sources. Format with markdown.",
    "multilingual_translator": "You are Multilingual Translator. Translate messages accurately while preserving tone and context. Provide the translation with a brief note about any cultural nuances. Format with markdown.",
    "omnichannel_assistant": "You are Omnichannel Assistant. Help manage multi-channel communications. Draft responses suitable for different platforms (SMS, WhatsApp, email). Format with markdown.",
    "compliance_audit": "You are AI Compliance Audit Bot. Analyze conversations for regulatory compliance (HIPAA, GDPR, SOC2). Identify risks, assign severity levels, and recommend remediation. Format as a structured audit report with markdown.",
    "visual_testing": "You are UI/UX Visual Testing Bot. Generate test plans, identify potential UI issues, and suggest testing strategies. Format with markdown checklists.",
    "bias_auditor": "You are Data Integrity & Bias Auditor. Analyze text for potential bias patterns in recruitment contexts. Identify issues and suggest fairer alternatives. Format as a structured report with markdown.",
    "threat_scanner": "You are Threat & Conduct Scanner. Analyze messages for potential security threats, scams, phishing attempts, and inappropriate conduct. Assign risk levels. Format as a security report with markdown.",
    "translation_qa": "You are Translation QA Bot. Review translations for accuracy, tone consistency, and cultural appropriateness. Provide quality scores and improvement suggestions. Format with markdown.",
}

# Slash command mapping: command prefix → bot_id
SLASH_COMMANDS = {}
for bot_id, bot_info in BOT_CATALOG.items():
    for cmd in bot_info.get("commands", []):
        # Extract the base command (e.g., "/match" from "/match <query>")
        base_cmd = cmd.split(" ")[0].lower()
        SLASH_COMMANDS[base_cmd] = bot_id


async def get_channel_context(channel_id: str, limit: int = 15) -> str:
    """Get recent messages from channel for context"""
    msgs = await db.lumi_messages.find(
        {"channel_id": channel_id, "type": {"$ne": "system"}},
        {"_id": 0, "sender_name": 1, "content": 1, "created_at": 1}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    if not msgs:
        return "No recent messages in this channel."
    msgs.reverse()
    lines = []
    for m in msgs:
        lines.append(f"[{m.get('sender_name', 'Unknown')}]: {m.get('content', '')}")
    return "\n".join(lines)


async def generate_bot_response(bot_id: str, user_query: str, channel_id: str, config: dict = None) -> str:
    """Generate an AI-powered bot response"""
    if not EMERGENT_LLM_KEY:
        return f"**{BOT_CATALOG.get(bot_id, {}).get('name', 'Bot')}** — AI key not configured. Please set EMERGENT_LLM_KEY."

    system_prompt = BOT_SYSTEM_PROMPTS.get(bot_id, "You are a helpful AI bot assistant.")
    bot_name = BOT_CATALOG.get(bot_id, {}).get("name", "Bot")

    # Get channel context
    context = await get_channel_context(channel_id)

    # Build the user message with context
    full_prompt = f"Channel conversation context:\n---\n{context}\n---\n\n"
    if user_query:
        full_prompt += f"User request: {user_query}"
    else:
        full_prompt += "The user triggered your action. Provide a helpful response based on the channel context above."

    # Add config context if available
    if config:
        config_str = ", ".join(f"{k}={v}" for k, v in config.items() if not isinstance(v, (list, dict)))
        full_prompt += f"\n\nBot configuration: {config_str}"

    try:
        session_id = f"bot_{bot_id}_{channel_id}_{uuid.uuid4().hex[:8]}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        )
        chat.with_model("openai", "gpt-4o")

        response = await chat.send_message(UserMessage(text=full_prompt))
        return f"**{bot_name}**\n\n{response}"
    except Exception as e:
        logger.error(f"Bot AI error for {bot_id}: {e}")
        return f"**{bot_name}** — I encountered an issue processing your request. Please try again."


async def handle_slash_command(content: str, channel_id: str, user_id: str) -> dict | None:
    """Check if a message is a slash command and handle it. Returns bot response info or None."""
    if not content.startswith("/"):
        return None

    parts = content.split(" ", 1)
    base_cmd = parts[0].lower()
    query = parts[1] if len(parts) > 1 else ""

    bot_id = SLASH_COMMANDS.get(base_cmd)
    if not bot_id:
        return None

    # Check if bot is installed in this channel
    installed = await db.enzi_installed_bots.find_one(
        {"bot_id": bot_id, "channel_id": channel_id, "is_active": True}
    )
    if not installed:
        return None

    response = await generate_bot_response(bot_id, query, channel_id, installed.get("config"))
    bot_info = BOT_CATALOG.get(bot_id, {})

    msg_id = str(uuid.uuid4())
    await db.lumi_messages.insert_one({
        "id": msg_id,
        "channel_id": channel_id,
        "content": response,
        "sender_id": f"bot_{bot_id}",
        "sender_name": f"[Bot] {bot_info.get('name', bot_id)}",
        "type": "bot_action",
        "bot_id": bot_id,
        "action": base_cmd,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"message_id": msg_id, "content": response, "bot_name": bot_info.get("name", bot_id), "bot_id": bot_id}


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/catalog")
async def get_bot_catalog(category: Optional[str] = None, featured: Optional[bool] = None):
    """Browse available bots with optional filters"""
    bots = []
    for k, v in BOT_CATALOG.items():
        if category and v["category"] != category:
            continue
        if featured is not None and v.get("featured") != featured:
            continue
        bots.append({
            "id": k, "name": v["name"], "description": v["description"],
            "icon": v.get("icon", "brain"), "category": v["category"],
            "subcategory": v.get("subcategory", ""),
            "featured": v.get("featured", False),
            "commands": v.get("commands", []),
            "install_count": v.get("install_count", 0),
            "rating": v.get("rating", 0),
        })
    categories = CATEGORY_ORDER
    return {"bots": bots, "categories": categories, "total": len(bots)}


@router.get("/featured")
async def get_featured_bots():
    """Get featured bots for marketplace hero"""
    featured = [
        {"id": k, "name": v["name"], "description": v["description"],
         "icon": v.get("icon", "brain"), "category": v["category"],
         "install_count": v.get("install_count", 0), "rating": v.get("rating", 0)}
        for k, v in BOT_CATALOG.items() if v.get("featured")
    ]
    return {"bots": featured}


@router.get("/popular")
async def get_popular_bots():
    """Get top 6 most installed bots"""
    sorted_bots = sorted(BOT_CATALOG.items(), key=lambda x: x[1].get("install_count", 0), reverse=True)
    popular = [
        {"id": k, "name": v["name"], "description": v["description"],
         "icon": v.get("icon", "brain"), "category": v["category"],
         "install_count": v.get("install_count", 0), "rating": v.get("rating", 0)}
        for k, v in sorted_bots[:6]
    ]
    return {"bots": popular}


class InstallBotRequest(BaseModel):
    bot_id: str
    channel_id: str
    config: Optional[dict] = None


@router.post("/install")
async def install_bot(req: InstallBotRequest, request: Request):
    """Install a bot in a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    bot = BOT_CATALOG.get(req.bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    existing = await db.enzi_installed_bots.find_one(
        {"bot_id": req.bot_id, "channel_id": req.channel_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Bot already installed in this channel")

    install_id = str(uuid.uuid4())
    config = {**bot["default_config"], **(req.config or {})}

    await db.enzi_installed_bots.insert_one({
        "id": install_id,
        "bot_id": req.bot_id,
        "bot_name": bot["name"],
        "channel_id": req.channel_id,
        "config": config,
        "installed_by": user.get("user_id"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    await db.lumi_messages.insert_one({
        "id": str(uuid.uuid4()),
        "channel_id": req.channel_id,
        "content": f"**{bot['name']}** has been installed. {bot['description']}",
        "sender_id": f"bot_{req.bot_id}",
        "sender_name": f"[Bot] {bot['name']}",
        "type": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"id": install_id, "bot_id": req.bot_id, "bot_name": bot["name"], "config": config, "status": "installed"}


@router.get("/installed")
async def get_installed_bots(request: Request, channel_id: Optional[str] = None):
    """Get installed bots"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = {"installed_by": user.get("user_id")}
    if channel_id:
        query["channel_id"] = channel_id

    bots = await db.enzi_installed_bots.find(query, {"_id": 0}).to_list(50)
    return {"bots": bots, "count": len(bots)}


@router.delete("/uninstall/{install_id}")
async def uninstall_bot(install_id: str, request: Request):
    """Uninstall a bot"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.delete_one({"id": install_id, "installed_by": user.get("user_id")})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "uninstalled"}


class ToggleBotRequest(BaseModel):
    is_active: bool


@router.put("/toggle/{install_id}")
async def toggle_bot(install_id: str, req: ToggleBotRequest, request: Request):
    """Toggle a bot active/paused"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.update_one(
        {"id": install_id, "installed_by": user.get("user_id")},
        {"$set": {"is_active": req.is_active}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "active" if req.is_active else "paused"}


class ConfigureBotRequest(BaseModel):
    config: dict


@router.put("/configure/{install_id}")
async def configure_bot(install_id: str, req: ConfigureBotRequest, request: Request):
    """Update bot configuration"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_installed_bots.update_one(
        {"id": install_id, "installed_by": user.get("user_id")},
        {"$set": {"config": req.config}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Installation not found")

    return {"status": "configured", "config": req.config}


class ReviewBotRequest(BaseModel):
    bot_id: str
    rating: int  # 1-5
    review: Optional[str] = None


@router.post("/review")
async def review_bot(req: ReviewBotRequest, request: Request):
    """Rate and review a bot"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    if req.bot_id not in BOT_CATALOG:
        raise HTTPException(status_code=404, detail="Bot not found")

    review_id = str(uuid.uuid4())
    await db.bot_reviews.update_one(
        {"bot_id": req.bot_id, "user_id": user.get("user_id")},
        {"$set": {
            "id": review_id,
            "bot_id": req.bot_id,
            "user_id": user.get("user_id"),
            "user_name": user.get("full_name", "User"),
            "rating": req.rating,
            "review": req.review or "",
            "created_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {"status": "reviewed", "review_id": review_id}


@router.get("/reviews/{bot_id}")
async def get_bot_reviews(bot_id: str):
    """Get reviews for a bot"""
    if bot_id not in BOT_CATALOG:
        raise HTTPException(status_code=404, detail="Bot not found")

    reviews = await db.bot_reviews.find({"bot_id": bot_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else BOT_CATALOG[bot_id].get("rating", 0)

    return {"reviews": reviews, "count": len(reviews), "avg_rating": round(avg_rating, 1)}


class BotActionRequest(BaseModel):
    bot_id: str
    channel_id: str
    action: str
    params: Optional[dict] = None


@router.post("/action")
async def execute_bot_action(req: BotActionRequest, request: Request):
    """Execute a bot action in a channel — AI-powered response"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    installed = await db.enzi_installed_bots.find_one(
        {"bot_id": req.bot_id, "channel_id": req.channel_id, "is_active": True}
    )
    if not installed:
        raise HTTPException(status_code=404, detail="Bot not installed in this channel")

    # Build query from action + params
    query = ""
    if req.params:
        query = " ".join(str(v) for v in req.params.values() if v)

    content = await generate_bot_response(req.bot_id, query, req.channel_id, installed.get("config"))
    msg_id = str(uuid.uuid4())
    bot_info = BOT_CATALOG.get(req.bot_id, {})

    await db.lumi_messages.insert_one({
        "id": msg_id,
        "channel_id": req.channel_id,
        "content": content,
        "sender_id": f"bot_{req.bot_id}",
        "sender_name": f"[Bot] {bot_info.get('name', req.bot_id)}",
        "type": "bot_action",
        "bot_id": req.bot_id,
        "action": req.action,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"message_id": msg_id, "content": content, "bot_name": bot_info.get("name", req.bot_id)}


@router.get("/channel/{channel_id}")
async def get_channel_bots(channel_id: str, request: Request):
    """Get installed bots for a channel with actions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    bots = await db.enzi_installed_bots.find(
        {"channel_id": channel_id, "is_active": True}, {"_id": 0}
    ).to_list(20)

    result = []
    for b in bots:
        bot_actions = BOT_ACTIONS.get(b["bot_id"], {})
        cat_info = BOT_CATALOG.get(b["bot_id"], {})
        result.append({
            "id": b["id"],
            "bot_id": b["bot_id"],
            "bot_name": b["bot_name"],
            "icon": cat_info.get("icon", "brain"),
            "actions": bot_actions.get("actions", []),
            "config": b.get("config", {})
        })

    return {"bots": result, "count": len(result)}


@router.get("/slash-commands/{channel_id}")
async def get_available_slash_commands(channel_id: str, request: Request):
    """Get available slash commands for a channel based on installed bots"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    installed = await db.enzi_installed_bots.find(
        {"channel_id": channel_id, "is_active": True}, {"_id": 0}
    ).to_list(20)

    commands = []
    for inst in installed:
        bot = BOT_CATALOG.get(inst["bot_id"])
        if bot:
            for cmd in bot.get("commands", []):
                commands.append({
                    "command": cmd,
                    "bot_id": inst["bot_id"],
                    "bot_name": bot["name"],
                    "category": bot["category"],
                })

    return {"commands": commands, "count": len(commands)}


# ═══════════════════════════════════════════════════════════════
# BOT CHAIN WORKFLOWS
# ═══════════════════════════════════════════════════════════════

class ChainStep(BaseModel):
    bot_id: str
    action: str
    order: int

class CreateChainRequest(BaseModel):
    name: str
    channel_id: str
    steps: List[ChainStep]
    trigger: str = "manual"

@router.post("/chains")
async def create_bot_chain(req: CreateChainRequest, request: Request):
    """Create a bot-to-bot workflow chain"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if len(req.steps) < 2:
        raise HTTPException(status_code=400, detail="A chain needs at least 2 steps")

    for step in req.steps:
        if step.bot_id not in BOT_CATALOG:
            raise HTTPException(status_code=400, detail=f"Unknown bot: {step.bot_id}")

    chain = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "channel_id": req.channel_id,
        "created_by": user["user_id"],
        "steps": [s.dict() for s in sorted(req.steps, key=lambda x: x.order)],
        "trigger": req.trigger,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_run": None,
        "run_count": 0,
    }
    await db.enzi_bot_chains.insert_one(chain)
    chain.pop("_id", None)
    return chain


@router.get("/chains/{channel_id}")
async def list_bot_chains(channel_id: str, request: Request):
    """List all workflow chains for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    chains = await db.enzi_bot_chains.find(
        {"channel_id": channel_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    for chain in chains:
        for step in chain.get("steps", []):
            bot = BOT_CATALOG.get(step["bot_id"], {})
            step["bot_name"] = bot.get("name", step["bot_id"])
            step["bot_icon"] = bot.get("icon", "bot")

    return {"chains": chains, "count": len(chains)}


@router.post("/chains/{chain_id}/run")
async def run_bot_chain(chain_id: str, request: Request):
    """Execute a bot chain — runs each bot in sequence, feeding output as context"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    chain = await db.enzi_bot_chains.find_one({"id": chain_id}, {"_id": 0})
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    channel_id = chain["channel_id"]
    results = []
    accumulated_context = ""

    # Post a chain-start system message
    start_msg_id = str(uuid.uuid4())
    step_names = " → ".join(BOT_CATALOG.get(s["bot_id"], {}).get("name", s["bot_id"]) for s in chain["steps"])
    await db.lumi_messages.insert_one({
        "id": start_msg_id,
        "channel_id": channel_id,
        "content": f"**Workflow: {chain['name']}**\nRunning chain: {step_names}",
        "sender_id": "system",
        "sender_name": "[System] Workflow",
        "type": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    for step in chain["steps"]:
        bot_id = step["bot_id"]
        query = accumulated_context if accumulated_context else ""

        try:
            response = await generate_bot_response(bot_id, query, channel_id)
            bot_info = BOT_CATALOG.get(bot_id, {})

            msg_id = str(uuid.uuid4())
            await db.lumi_messages.insert_one({
                "id": msg_id,
                "channel_id": channel_id,
                "content": response,
                "sender_id": f"bot_{bot_id}",
                "sender_name": f"[Bot] {bot_info.get('name', bot_id)}",
                "type": "bot_action",
                "bot_id": bot_id,
                "action": step.get("action", "chain"),
                "chain_id": chain_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

            accumulated_context += f"\n\n---\n{bot_info.get('name', bot_id)} output:\n{response}"
            results.append({"bot_id": bot_id, "message_id": msg_id, "status": "success"})
        except Exception as e:
            logger.error(f"Chain step error {bot_id}: {e}")
            results.append({"bot_id": bot_id, "status": "error", "error": str(e)})
            break

    await db.enzi_bot_chains.update_one(
        {"id": chain_id},
        {"$set": {"last_run": datetime.now(timezone.utc).isoformat()}, "$inc": {"run_count": 1}}
    )

    return {"chain_id": chain_id, "results": results, "steps_completed": len(results)}


@router.delete("/chains/{chain_id}")
async def delete_bot_chain(chain_id: str, request: Request):
    """Delete a workflow chain"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.enzi_bot_chains.delete_one({"id": chain_id, "created_by": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chain not found")
    return {"status": "deleted"}
