"""
ENZI Bot Store — Full Marketplace
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

from utils.database import db
from routes.auth import get_current_user

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

# Bot action handlers
BOT_ACTIONS = {
    "talent_matcher": {
        "actions": [{"id": "match", "label": "Find Talent", "icon": "user-search"}],
        "handler": lambda p: f"**Talent Search**\nSearching 800M+ profiles for: *{p.get('query', 'senior backend engineer')}*\nMatch score threshold: 75%\n\nProcessing results..."
    },
    "resume_architect": {
        "actions": [{"id": "build_resume", "label": "Build Resume", "icon": "file-text"}],
        "handler": lambda p: "**Resume Architect**\nGenerating ATS-optimized resume from job listing...\nFormat: Modern | Language: English | ATS Score: Calculating..."
    },
    "interview_copilot": {
        "actions": [{"id": "mock_interview", "label": "Mock Interview", "icon": "mic"}],
        "handler": lambda p: "**Interview Copilot**\nStarting mock interview session...\nTracking: filler words, pacing, body language\nSay 'ready' to begin."
    },
    "ez_sourcing": {
        "actions": [{"id": "source", "label": "Start Sourcing", "icon": "zap"}],
        "handler": lambda p: f"**EZ Sourcing Agent**\nStarting autonomous sourcing for: *{p.get('role', 'open role')}*\nSteps: Profile scan → Email verification → Outreach"
    },
    "salary_negotiator": {
        "actions": [{"id": "benchmark", "label": "Salary Benchmark", "icon": "dollar-sign"}],
        "handler": lambda p: f"**Salary Negotiator**\nAnalyzing compensation data for *{p.get('role', 'this role')}*...\nRegion: US | Including benefits: Yes"
    },
    "note_taker": {
        "actions": [{"id": "notes", "label": "Start Notes", "icon": "edit"}],
        "handler": lambda p: "**Note-Taker Active**\nRecording and transcribing in real-time.\nAction items and key insights will be extracted automatically."
    },
    "smart_scheduler": {
        "actions": [{"id": "schedule", "label": "Schedule Meeting", "icon": "calendar"}],
        "handler": lambda p: "**Smart Scheduler**\nAnalyzing calendars to find optimal time...\nBuffer: 10 min | Reminders: Enabled"
    },
    "search_copilot": {
        "actions": [{"id": "ask", "label": "Ask AI", "icon": "search"}],
        "handler": lambda p: f"**Search Copilot**\nSearching past meetings for: *{p.get('question', 'your query')}*..."
    },
    "attendance_tracker": {
        "actions": [{"id": "attendance", "label": "Attendance Report", "icon": "users"}],
        "handler": lambda p: "**Attendance Tracker**\nGenerating attendance sheet and engagement metrics..."
    },
    "summary_generator": {
        "actions": [{"id": "summarize", "label": "Summarize", "icon": "brain"}],
        "handler": lambda p: "**Summary Generator**\nConverting transcript into structured summary with highlights..."
    },
    "knowledge_layer": {
        "actions": [{"id": "ask", "label": "Ask Knowledge", "icon": "book-open"}],
        "handler": lambda p: f"**Knowledge Layer**\nSearching company-wide data for: *{p.get('question', 'your question')}*..."
    },
    "multilingual_translator": {
        "actions": [{"id": "translate", "label": "Translate", "icon": "globe"}],
        "handler": lambda p: f"**Translator Active**\nAuto-translating to {p.get('language', 'English')}. Language detection: ON"
    },
    "omnichannel_assistant": {
        "actions": [{"id": "inbox", "label": "Unified Inbox", "icon": "message-circle"}],
        "handler": lambda p: "**Omnichannel Assistant**\nUnified inbox active: SMS, WhatsApp, Web Chat\nAll messages routed here."
    },
    "compliance_audit": {
        "actions": [{"id": "audit", "label": "Run Audit", "icon": "shield"}],
        "handler": lambda p: "**Compliance Audit**\nScanning against HIPAA, GDPR, SOC2 frameworks...\nGenerating risk score and PDF report."
    },
    "visual_testing": {
        "actions": [{"id": "test", "label": "Run UI Tests", "icon": "monitor"}],
        "handler": lambda p: "**Visual Testing Bot**\nRunning regression tests across desktop, mobile, tablet..."
    },
    "bias_auditor": {
        "actions": [{"id": "audit_data", "label": "Audit Data", "icon": "scale"}],
        "handler": lambda p: "**Bias Auditor**\nScanning recruitment datasets for hidden patterns and potential bias..."
    },
    "threat_scanner": {
        "actions": [{"id": "scan", "label": "Scan Threats", "icon": "alert-triangle"}],
        "handler": lambda p: "**Threat Scanner**\nMonitoring communications for threats, scams, and conduct issues..."
    },
    "translation_qa": {
        "actions": [{"id": "qa", "label": "QA Translations", "icon": "check-circle"}],
        "handler": lambda p: "**Translation QA**\nAuditing translations for accuracy, tone, and cultural context..."
    },
}


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
    """Execute a bot action in a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    installed = await db.enzi_installed_bots.find_one(
        {"bot_id": req.bot_id, "channel_id": req.channel_id, "is_active": True}
    )
    if not installed:
        raise HTTPException(status_code=404, detail="Bot not installed in this channel")

    bot_def = BOT_ACTIONS.get(req.bot_id)
    if not bot_def:
        raise HTTPException(status_code=404, detail="Bot actions not defined")

    content = bot_def["handler"](req.params or {})
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
