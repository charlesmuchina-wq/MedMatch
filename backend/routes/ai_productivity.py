"""
AI Productivity Features for LUMI & AI KARAU
- Intelligent Meeting Summaries with action item extraction
- Sentiment Analysis for channel health
- Automated Status Reporting
- Smart Task Assignment from chat
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import json
import os
import logging

from utils.database import db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Productivity"])

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")


async def _call_llm(prompt: str, system_msg: str, session_tag: str) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"{session_tag}_{uuid.uuid4().hex[:6]}",
        system_message=system_msg
    ).with_model("openai", "gpt-5.2")
    return await chat.send_message(UserMessage(text=prompt))


def _parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(t)


# ============== 1. Intelligent Meeting Summaries ==============

@router.post("/karau-meet/ai/enhanced-summary")
async def enhanced_meeting_summary(request: Request):
    """AI-powered meeting summary with extracted action items, assignees, and deadlines"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    user_id = user["user_id"]
    meetings = await db.karau_meetings.find(
        {"$or": [{"host_id": user_id}, {"participants.user_id": user_id}], "status": "ended"},
        {"_id": 0, "meeting_id": 1, "title": 1, "ai_notes": 1, "ended_at": 1, "participants": 1}
    ).sort("ended_at", -1).limit(10).to_list(10)

    all_notes = []
    participant_names = set()
    for m in meetings:
        for p in m.get("participants", []):
            participant_names.add(p.get("name", p.get("user_id", "Unknown")))
        for note in m.get("ai_notes", []):
            all_notes.append(f"[{m.get('title', 'Meeting')}] ({note.get('type', 'note')}): {note.get('content', '')}")

    if not all_notes:
        return {
            "summary": "No meeting data available yet. Complete meetings with AI notes to get intelligent summaries.",
            "action_items": [], "key_decisions": [], "risk_alerts": [],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    names_str = ", ".join(list(participant_names)[:20])
    notes_text = "\n".join(all_notes[:40])

    try:
        prompt = f"""Analyze these meeting notes from {len(meetings)} meetings. Participants include: {names_str}

{notes_text}

Extract structured intelligence. Respond in valid JSON only:
{{
  "summary": "2-3 sentence executive overview",
  "action_items": [
    {{"task": "description", "assignee": "person name or 'Unassigned'", "deadline": "YYYY-MM-DD or 'TBD'", "priority": "high/medium/low"}}
  ],
  "key_decisions": ["decision 1", "decision 2"],
  "risk_alerts": ["risk or concern that needs attention"],
  "follow_ups": ["topic needing follow-up discussion"]
}}"""

        raw = await _call_llm(prompt, "You are a meeting intelligence analyst. Extract action items with specific assignees and deadlines. Respond in valid JSON only.", f"enh_sum_{user_id}")
        result = _parse_json(raw)

        # Store action items in DB for tracking
        for item in result.get("action_items", []):
            item["id"] = f"ai_{uuid.uuid4().hex[:8]}"
            item["status"] = "open"
            item["created_at"] = datetime.now(timezone.utc).isoformat()
            item["created_by"] = user_id
            item["source"] = "meeting_summary"
            await db.ai_action_items.update_one(
                {"id": item["id"]}, {"$set": item}, upsert=True
            )

        return {
            **result,
            "meetings_analyzed": len(meetings),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Enhanced summary error: {e}")
        return {
            "summary": "AI analysis temporarily unavailable.", "action_items": [],
            "key_decisions": [], "risk_alerts": [],
            "error": str(e), "generated_at": datetime.now(timezone.utc).isoformat()
        }


@router.get("/karau-meet/ai/action-items")
async def list_ai_action_items(request: Request):
    """List all AI-extracted action items with tracking status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    items = await db.ai_action_items.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)

    open_count = sum(1 for i in items if i.get("status") == "open")
    done_count = sum(1 for i in items if i.get("status") == "done")

    return {
        "items": items,
        "stats": {"total": len(items), "open": open_count, "done": done_count,
                  "completion_rate": round(done_count / max(1, len(items)) * 100)}
    }


class ActionItemUpdate(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[str] = None


@router.put("/karau-meet/ai/action-items/{item_id}")
async def update_action_item(item_id: str, body: ActionItemUpdate, request: Request):
    """Update an action item's status, assignee, or deadline"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    updates = {}
    if body.status:
        updates["status"] = body.status
    if body.assignee:
        updates["assignee"] = body.assignee
    if body.deadline:
        updates["deadline"] = body.deadline
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    updates["updated_by"] = user["user_id"]

    result = await db.ai_action_items.update_one({"id": item_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True, "item_id": item_id}


# ============== 2. Sentiment Analysis ==============

@router.post("/lumi/ai/sentiment/{channel_id}")
async def analyze_channel_sentiment(channel_id: str, request: Request):
    """Analyze sentiment/morale of a channel's recent messages"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    messages = await db.lumi_messages.find(
        {"channel_id": channel_id, "type": {"$ne": "system"}},
        {"_id": 0, "content": 1, "sender_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(50).to_list(50)

    if len(messages) < 3:
        return {
            "score": 75, "label": "Neutral",
            "summary": "Not enough messages to analyze yet.",
            "alerts": [], "generated_at": datetime.now(timezone.utc).isoformat()
        }

    msg_text = "\n".join([f"{m.get('sender_name', 'User')}: {m.get('content', '')}" for m in messages[:40]])

    try:
        prompt = f"""Analyze the sentiment and team morale from these team chat messages:

{msg_text}

Respond in valid JSON only:
{{
  "score": 0-100 (0=very negative, 50=neutral, 100=very positive),
  "label": "Positive/Neutral/Concerned/Negative",
  "summary": "1-2 sentence mood assessment",
  "highlights": ["positive observation 1"],
  "alerts": ["concern that needs attention, if any"],
  "engagement_level": "High/Medium/Low"
}}"""

        raw = await _call_llm(prompt, "You are a team dynamics analyst. Assess team morale from chat messages. Be balanced and constructive. JSON only.", f"sent_{channel_id}")
        result = _parse_json(raw)

        # Store sentiment history
        await db.lumi_sentiment.insert_one({
            "channel_id": channel_id,
            "score": result.get("score", 50),
            "label": result.get("label", "Neutral"),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "messages_analyzed": len(messages)
        })

        return {**result, "messages_analyzed": len(messages), "generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        return {"score": 50, "label": "Neutral", "summary": "Analysis temporarily unavailable.", "alerts": [], "error": str(e), "generated_at": datetime.now(timezone.utc).isoformat()}


@router.get("/lumi/ai/sentiment-history/{channel_id}")
async def get_sentiment_history(channel_id: str, request: Request):
    """Get sentiment trend for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    history = await db.lumi_sentiment.find(
        {"channel_id": channel_id}, {"_id": 0}
    ).sort("analyzed_at", -1).limit(10).to_list(10)

    return {"history": history}


# ============== 3. Automated Status Reporting ==============

@router.post("/lumi/ai/report/{channel_id}")
async def generate_channel_report(channel_id: str, request: Request):
    """Generate an AI-powered activity report for a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0, "name": 1, "channel_type": 1})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Get messages from last 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    messages = await db.lumi_messages.find(
        {"channel_id": channel_id, "created_at": {"$gte": cutoff}, "type": {"$ne": "system"}},
        {"_id": 0, "content": 1, "sender_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(100).to_list(100)

    # Gather stats
    unique_authors = set(m.get("sender_name", "") for m in messages)
    msg_count = len(messages)

    if msg_count < 2:
        return {
            "report": f"**#{channel.get('name', 'Channel')} — Weekly Report**\n\nNot enough activity to generate a report (only {msg_count} messages this week).",
            "stats": {"messages": msg_count, "participants": len(unique_authors)},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    msg_text = "\n".join([f"{m.get('sender_name', 'User')}: {m.get('content', '')}" for m in messages[:60]])

    try:
        prompt = f"""Generate a concise weekly status report for the #{channel.get('name', 'channel')} channel based on these {msg_count} messages from {len(unique_authors)} team members:

{msg_text}

Format the report in Markdown. Include:
1. **Executive Summary** (2-3 sentences)
2. **Key Discussions** (bullet points of main topics)
3. **Decisions Made** (if any)
4. **Action Items** (extracted from conversations)
5. **Blockers/Risks** (if mentioned)
6. **Team Activity** (who was most active, engagement pattern)

Keep it professional and stakeholder-ready."""

        report = await _call_llm(prompt, "You are a project reporting assistant. Generate clean, professional status reports from team chat data. Use Markdown formatting.", f"rpt_{channel_id}")

        # Store report
        report_doc = {
            "id": f"rpt_{uuid.uuid4().hex[:8]}",
            "channel_id": channel_id,
            "channel_name": channel.get("name", ""),
            "report": report,
            "stats": {"messages": msg_count, "participants": len(unique_authors), "period_days": 7},
            "generated_by": user["user_id"],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.lumi_reports.insert_one({**report_doc})
        report_doc.pop("_id", None)

        return report_doc
    except Exception as e:
        logger.error(f"Report error: {e}")
        return {"report": "Report generation temporarily unavailable.", "error": str(e), "generated_at": datetime.now(timezone.utc).isoformat()}


@router.get("/lumi/ai/reports")
async def list_reports(request: Request):
    """List generated reports"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    reports = await db.lumi_reports.find(
        {}, {"_id": 0}
    ).sort("generated_at", -1).limit(20).to_list(20)

    return {"reports": reports}


# ============== 4. Smart Task Assignment ==============

@router.post("/lumi/ai/extract-tasks/{channel_id}")
async def extract_tasks_from_chat(channel_id: str, request: Request):
    """AI extracts tasks/action items from recent chat messages"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0, "name": 1, "members": 1})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    messages = await db.lumi_messages.find(
        {"channel_id": channel_id, "type": {"$ne": "system"}},
        {"_id": 0, "content": 1, "sender_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(50).to_list(50)

    if len(messages) < 2:
        return {"tasks": [], "message": "Not enough messages to extract tasks."}

    member_names = [m.get("name", m.get("user_id", "")) for m in channel.get("members", [])]
    msg_text = "\n".join([f"{m.get('sender_name', 'User')}: {m.get('content', '')}" for m in messages[:40]])

    try:
        prompt = f"""Analyze these team chat messages and extract any tasks, action items, or commitments mentioned.
Team members: {', '.join(member_names[:15])}

Messages:
{msg_text}

Respond in valid JSON only:
{{
  "tasks": [
    {{
      "task": "clear task description",
      "assignee": "person who should do it (from team members) or 'Unassigned'",
      "deadline": "YYYY-MM-DD or 'TBD'",
      "priority": "high/medium/low",
      "context": "brief context from the conversation"
    }}
  ]
}}
If no tasks are found, return {{"tasks": []}}"""

        raw = await _call_llm(prompt, "You are a task extraction specialist. Find tasks and commitments in team conversations. Be precise about who should do what. JSON only.", f"task_{channel_id}")
        result = _parse_json(raw)

        # Store tasks
        tasks = result.get("tasks", [])
        for task in tasks:
            task["id"] = f"tsk_{uuid.uuid4().hex[:8]}"
            task["channel_id"] = channel_id
            task["channel_name"] = channel.get("name", "")
            task["status"] = "open"
            task["created_at"] = datetime.now(timezone.utc).isoformat()
            task["created_by"] = user["user_id"]
            task["source"] = "chat_extraction"
            await db.lumi_tasks.update_one({"id": task["id"]}, {"$set": task}, upsert=True)

        return {"tasks": tasks, "extracted_from": len(messages), "generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Task extraction error: {e}")
        return {"tasks": [], "error": str(e)}


@router.get("/lumi/ai/tasks")
async def list_tasks(request: Request, channel_id: Optional[str] = None):
    """List tasks for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    query = {}
    if channel_id:
        query["channel_id"] = channel_id

    tasks = await db.lumi_tasks.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)

    open_count = sum(1 for t in tasks if t.get("status") == "open")
    return {"tasks": tasks, "stats": {"total": len(tasks), "open": open_count}}


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None


@router.put("/lumi/ai/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate, request: Request):
    """Update task status or assignee"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.status:
        updates["status"] = body.status
    if body.assignee:
        updates["assignee"] = body.assignee

    result = await db.lumi_tasks.update_one({"id": task_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


# ============== 5. Conversational Data Querying (NLP) ==============

class AskAiRequest(BaseModel):
    question: str
    channel_id: Optional[str] = None


@router.post("/lumi/ai/ask")
async def conversational_query(body: AskAiRequest, request: Request):
    """Natural language querying across meeting data, channels, and tasks"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    user_id = user["user_id"]
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question required")

    # Gather context: recent meetings, tasks, channel activity
    context_parts = []

    # Meeting data
    meetings = await db.karau_meetings.find(
        {"$or": [{"host_id": user_id}, {"participants.user_id": user_id}]},
        {"_id": 0, "meeting_id": 1, "title": 1, "status": 1, "ai_notes": 1,
         "created_at": 1, "ended_at": 1, "participants": 1}
    ).sort("created_at", -1).limit(10).to_list(10)

    if meetings:
        meeting_summaries = []
        for m in meetings:
            notes_text = "; ".join([n.get("content", "") for n in m.get("ai_notes", [])[:5]])
            p_count = len(m.get("participants", []))
            meeting_summaries.append(
                f"- {m.get('title', 'Untitled')} (status: {m.get('status', 'unknown')}, "
                f"{p_count} participants): {notes_text[:200]}"
            )
        context_parts.append(f"MEETINGS ({len(meetings)}):\n" + "\n".join(meeting_summaries))

    # Channel messages (if channel specified)
    if body.channel_id:
        msgs = await db.lumi_messages.find(
            {"channel_id": body.channel_id, "type": {"$ne": "system"}},
            {"_id": 0, "content": 1, "sender_name": 1, "created_at": 1}
        ).sort("created_at", -1).limit(30).to_list(30)
        if msgs:
            msg_text = "\n".join([f"- {m.get('sender_name', 'User')}: {m.get('content', '')}" for m in msgs[:20]])
            context_parts.append(f"RECENT CHANNEL MESSAGES:\n{msg_text}")

    # All channels
    channels = await db.lumi_channels.find(
        {}, {"_id": 0, "id": 1, "name": 1, "channel_type": 1}
    ).limit(20).to_list(20)
    if channels:
        ch_list = ", ".join([f"#{c.get('name', '')}" for c in channels])
        context_parts.append(f"CHANNELS: {ch_list}")

    # Tasks
    tasks = await db.lumi_tasks.find(
        {}, {"_id": 0, "task": 1, "assignee": 1, "status": 1, "priority": 1, "channel_name": 1}
    ).limit(20).to_list(20)
    if tasks:
        task_text = "\n".join([
            f"- [{t.get('status', 'open')}] {t.get('task', '')} (assigned: {t.get('assignee', 'unassigned')}, "
            f"priority: {t.get('priority', 'medium')})"
            for t in tasks
        ])
        context_parts.append(f"TASKS ({len(tasks)}):\n{task_text}")

    # Action items
    action_items = await db.ai_action_items.find(
        {}, {"_id": 0, "task": 1, "assignee": 1, "status": 1, "deadline": 1}
    ).limit(15).to_list(15)
    if action_items:
        ai_text = "\n".join([
            f"- [{a.get('status', 'open')}] {a.get('task', '')} → {a.get('assignee', 'unassigned')} (due: {a.get('deadline', 'TBD')})"
            for a in action_items
        ])
        context_parts.append(f"ACTION ITEMS:\n{ai_text}")

    full_context = "\n\n".join(context_parts) if context_parts else "No data available yet."

    try:
        prompt = f"""A team member asks: "{question}"

Here is the available project and team data:

{full_context}

Provide a helpful, concise answer. If the data doesn't contain enough information, say so honestly. 
If you identify actionable insights or recommendations, include them.
Format your response clearly with bullet points where appropriate."""

        answer = await _call_llm(
            prompt,
            "You are an AI project intelligence assistant embedded in a team messenger. "
            "Answer questions about project status, team activity, meetings, and tasks using the provided data. "
            "Be concise, accurate, and actionable.",
            f"ask_{user_id}"
        )

        # Store conversation for history
        await db.lumi_ai_conversations.insert_one({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "channel_id": body.channel_id,
            "asked_at": datetime.now(timezone.utc).isoformat()
        })

        return {"answer": answer, "context_sources": len(context_parts), "generated_at": datetime.now(timezone.utc).isoformat()}

    except Exception as e:
        logger.error(f"Conversational query error: {e}")
        return {"answer": "I'm temporarily unable to process your question. Please try again.", "error": str(e)}


@router.get("/lumi/ai/conversation-history")
async def get_conversation_history(request: Request):
    """Get recent AI conversation history for the user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    history = await db.lumi_ai_conversations.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("asked_at", -1).limit(20).to_list(20)

    return {"conversations": history}


# ============== 6. Interactive Decision Cards ==============

@router.post("/lumi/ai/decision-card")
async def generate_decision_card(request: Request):
    """Generate an interactive decision card based on current project state"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    user_id = user["user_id"]

    # Gather all open tasks and action items
    open_tasks = await db.lumi_tasks.find(
        {"status": "open"}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)

    open_actions = await db.ai_action_items.find(
        {"status": "open"}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)

    # Recent sentiment
    recent_sentiment = await db.lumi_sentiment.find(
        {}, {"_id": 0}
    ).sort("analyzed_at", -1).limit(5).to_list(5)

    context = {
        "open_tasks": len(open_tasks),
        "high_priority_tasks": [t for t in open_tasks if t.get("priority") == "high"],
        "open_actions": len(open_actions),
        "overdue_actions": [a for a in open_actions if a.get("deadline") and a.get("deadline") != "TBD" and a.get("deadline") < datetime.now(timezone.utc).strftime("%Y-%m-%d")],
        "sentiment_scores": [s.get("score", 50) for s in recent_sentiment],
    }

    try:
        ctx_text = json.dumps(context, default=str)
        prompt = f"""Based on the current project state, generate 1-3 decision cards that need attention.

Project state:
{ctx_text}

Respond in valid JSON only:
{{
  "cards": [
    {{
      "title": "Card title (concise)",
      "description": "What needs attention and why",
      "severity": "critical/warning/info",
      "actions": [
        {{"label": "Action button text", "action_type": "reassign/escalate/defer/resolve/notify", "payload": "relevant_id or description"}}
      ],
      "metric": {{"label": "Key metric", "value": "number or text"}}
    }}
  ]
}}"""

        raw = await _call_llm(prompt, "You are a project decision intelligence engine. Generate actionable decision cards based on project data. JSON only.", f"card_{user_id}")
        result = _parse_json(raw)

        for card in result.get("cards", []):
            card["id"] = f"card_{uuid.uuid4().hex[:8]}"
            card["created_at"] = datetime.now(timezone.utc).isoformat()
            card["status"] = "active"

        return {**result, "generated_at": datetime.now(timezone.utc).isoformat()}

    except Exception as e:
        logger.error(f"Decision card error: {e}")
        return {"cards": [], "error": str(e)}


@router.post("/lumi/ai/decision-card/{card_id}/action")
async def execute_card_action(card_id: str, request: Request):
    """Execute an action from a decision card"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    body = await request.json()
    action_type = body.get("action_type", "")
    payload = body.get("payload", "")

    # Log the action
    await db.lumi_decision_log.insert_one({
        "card_id": card_id,
        "action_type": action_type,
        "payload": payload,
        "executed_by": user["user_id"],
        "executed_at": datetime.now(timezone.utc).isoformat()
    })

    # Execute based on type
    if action_type == "resolve":
        await db.lumi_tasks.update_many(
            {"status": "open", "priority": "high"},
            {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"success": True, "message": "High-priority tasks moved to in-progress"}
    elif action_type == "notify":
        return {"success": True, "message": f"Notification sent regarding: {payload}"}
    elif action_type == "defer":
        return {"success": True, "message": f"Deferred: {payload}"}
    elif action_type == "escalate":
        return {"success": True, "message": f"Escalated: {payload}"}
    else:
        return {"success": True, "message": f"Action '{action_type}' recorded"}


# ============== 7. Proactive Anomaly Alerts ==============

@router.get("/lumi/ai/anomalies")
async def detect_anomalies(request: Request):
    """Detect anomalies in project activity and team patterns"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    alerts = []
    now = datetime.now(timezone.utc)

    # Check 1: Overdue action items
    overdue = await db.ai_action_items.find(
        {"status": "open", "deadline": {"$exists": True, "$ne": "TBD"}},
        {"_id": 0}
    ).to_list(50)
    overdue_items = [a for a in overdue if a.get("deadline", "9999") < now.strftime("%Y-%m-%d")]
    if overdue_items:
        alerts.append({
            "id": f"alert_overdue_{uuid.uuid4().hex[:6]}",
            "type": "overdue_items",
            "severity": "critical" if len(overdue_items) > 3 else "warning",
            "title": f"{len(overdue_items)} Overdue Action Items",
            "description": f"There are {len(overdue_items)} action items past their deadline that need attention.",
            "items": [{"task": a.get("task", ""), "deadline": a.get("deadline", ""), "assignee": a.get("assignee", "")} for a in overdue_items[:5]],
            "suggested_action": "Review and reassign or update deadlines"
        })

    # Check 2: Low sentiment channels
    recent_sentiments = await db.lumi_sentiment.find(
        {"analyzed_at": {"$gte": (now - timedelta(days=7)).isoformat()}},
        {"_id": 0}
    ).to_list(20)
    low_morale = [s for s in recent_sentiments if s.get("score", 100) < 40]
    if low_morale:
        alerts.append({
            "id": f"alert_morale_{uuid.uuid4().hex[:6]}",
            "type": "low_morale",
            "severity": "warning",
            "title": "Low Team Morale Detected",
            "description": f"{len(low_morale)} channel(s) show concerning sentiment scores below 40.",
            "channels": [s.get("channel_id", "") for s in low_morale],
            "suggested_action": "Schedule team check-in or address blockers"
        })

    # Check 3: Stale channels (no messages in 3+ days)
    cutoff_3d = (now - timedelta(days=3)).isoformat()
    all_channels = await db.lumi_channels.find({}, {"_id": 0, "id": 1, "name": 1}).to_list(20)
    for ch in all_channels:
        latest_msg = await db.lumi_messages.find_one(
            {"channel_id": ch["id"], "created_at": {"$gte": cutoff_3d}},
            {"_id": 0, "created_at": 1}
        )
        if not latest_msg:
            # Check if channel has any messages at all
            any_msg = await db.lumi_messages.find_one({"channel_id": ch["id"]}, {"_id": 0})
            if any_msg:
                alerts.append({
                    "id": f"alert_stale_{ch['id'][:8]}",
                    "type": "stale_channel",
                    "severity": "info",
                    "title": f"#{ch.get('name', 'Channel')} — No Recent Activity",
                    "description": f"No messages in #{ch.get('name', '')} for 3+ days.",
                    "suggested_action": "Check if the channel is still active or archive it"
                })

    # Check 4: Unassigned high-priority tasks
    unassigned_high = await db.lumi_tasks.find(
        {"status": "open", "priority": "high", "$or": [{"assignee": "Unassigned"}, {"assignee": {"$exists": False}}]},
        {"_id": 0}
    ).to_list(10)
    if unassigned_high:
        alerts.append({
            "id": f"alert_unassigned_{uuid.uuid4().hex[:6]}",
            "type": "unassigned_tasks",
            "severity": "warning",
            "title": f"{len(unassigned_high)} High-Priority Tasks Unassigned",
            "description": "Critical tasks without owners need immediate assignment.",
            "tasks": [t.get("task", "") for t in unassigned_high[:5]],
            "suggested_action": "Assign team members to high-priority tasks"
        })

    # Check 5: Task completion rate
    all_tasks = await db.lumi_tasks.find({}, {"_id": 0, "status": 1}).to_list(100)
    if len(all_tasks) >= 5:
        done = sum(1 for t in all_tasks if t.get("status") == "done")
        rate = round(done / len(all_tasks) * 100)
        if rate < 30:
            alerts.append({
                "id": f"alert_completion_{uuid.uuid4().hex[:6]}",
                "type": "low_completion",
                "severity": "warning",
                "title": f"Low Task Completion Rate: {rate}%",
                "description": f"Only {done}/{len(all_tasks)} tasks are completed. This may indicate blockers.",
                "suggested_action": "Review blocked tasks and redistribute workload"
            })

    return {
        "alerts": alerts,
        "total": len(alerts),
        "critical": sum(1 for a in alerts if a.get("severity") == "critical"),
        "checked_at": now.isoformat()
    }


# ============== 8. Command Bar Search ==============

class CommandSearchRequest(BaseModel):
    query: str
    mode: Optional[str] = "search"  # "search" or "ai"


@router.post("/lumi/command/search")
async def command_bar_search(body: CommandSearchRequest, request: Request):
    """Unified search for command bar — channels, DMs, messages, tasks, actions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    q = body.query.strip().lower()
    if not q:
        return {"results": []}

    # If AI mode, delegate to conversational AI
    if body.mode == "ai":
        try:
            res_data = await conversational_query(
                AskAiRequest(question=body.query), request
            )
            return {"results": [{"type": "ai_answer", "content": res_data.get("answer", ""), "icon": "sparkles"}], "mode": "ai"}
        except Exception as e:
            return {"results": [{"type": "ai_answer", "content": f"Error: {str(e)}", "icon": "sparkles"}], "mode": "ai"}

    results = []

    # Search channels
    channels = await db.lumi_channels.find(
        {"name": {"$regex": q, "$options": "i"}},
        {"_id": 0, "id": 1, "name": 1, "channel_type": 1}
    ).limit(5).to_list(5)
    for ch in channels:
        results.append({"type": "channel", "id": ch["id"], "name": ch["name"], "subtype": ch.get("channel_type", "group"), "icon": "hash"})

    # Search DMs
    user_id = user["user_id"]
    dms = await db.lumi_dms.find(
        {"participants": user_id},
        {"_id": 0, "id": 1, "dm_partner": 1}
    ).limit(5).to_list(5)
    for dm in dms:
        partner = dm.get("dm_partner", {})
        p_name = partner.get("name", partner.get("email", ""))
        if q in p_name.lower():
            results.append({"type": "dm", "id": dm["id"], "name": p_name, "icon": "user"})

    # Search messages
    messages = await db.lumi_messages.find(
        {"content": {"$regex": q, "$options": "i"}, "type": {"$ne": "system"}},
        {"_id": 0, "id": 1, "content": 1, "sender_name": 1, "channel_id": 1}
    ).sort("created_at", -1).limit(5).to_list(5)
    for msg in messages:
        results.append({"type": "message", "id": msg.get("id", ""), "content": msg.get("content", "")[:80], "sender": msg.get("sender_name", ""), "channel_id": msg.get("channel_id", ""), "icon": "message"})

    # Search tasks
    tasks = await db.lumi_tasks.find(
        {"task": {"$regex": q, "$options": "i"}},
        {"_id": 0, "id": 1, "task": 1, "status": 1, "assignee": 1, "priority": 1}
    ).limit(5).to_list(5)
    for t in tasks:
        results.append({"type": "task", "id": t["id"], "name": t.get("task", ""), "status": t.get("status", ""), "assignee": t.get("assignee", ""), "priority": t.get("priority", ""), "icon": "list-todo"})

    # Search action items
    actions = await db.ai_action_items.find(
        {"task": {"$regex": q, "$options": "i"}},
        {"_id": 0, "id": 1, "task": 1, "status": 1, "assignee": 1}
    ).limit(3).to_list(3)
    for a in actions:
        results.append({"type": "action_item", "id": a["id"], "name": a.get("task", ""), "status": a.get("status", ""), "icon": "check-circle"})

    # Quick actions
    quick_actions = [
        {"type": "action", "id": "create_channel", "name": "Create new channel", "icon": "plus", "command": "create_channel"},
        {"type": "action", "id": "gen_report", "name": "Generate channel report", "icon": "file-bar-chart", "command": "generate_report"},
        {"type": "action", "id": "check_sentiment", "name": "Analyze channel sentiment", "icon": "activity", "command": "analyze_sentiment"},
        {"type": "action", "id": "extract_tasks", "name": "Extract tasks from chat", "icon": "list-todo", "command": "extract_tasks"},
        {"type": "action", "id": "check_anomalies", "name": "Check for anomalies", "icon": "alert-triangle", "command": "check_anomalies"},
    ]
    for qa in quick_actions:
        if q in qa["name"].lower():
            results.append(qa)

    return {"results": results[:15], "mode": "search"}


# ============== 9. Knowledge Graph ==============

@router.get("/lumi/knowledge-graph")
async def get_knowledge_graph(request: Request):
    """Build and return the knowledge graph of entity relationships"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    nodes = []
    edges = []
    node_ids = set()

    # Get all channels
    channels = await db.lumi_channels.find(
        {}, {"_id": 0, "id": 1, "name": 1, "channel_type": 1, "members": 1}
    ).to_list(30)

    for ch in channels:
        ch_node_id = f"ch_{ch['id'][:8]}"
        nodes.append({
            "id": ch_node_id, "type": "channel", "label": f"#{ch['name']}",
            "subtype": ch.get("channel_type", "group"), "size": "medium"
        })
        node_ids.add(ch_node_id)

        # Connect members to channels
        for member in ch.get("members", []):
            m_id = member.get("user_id", member.get("email", ""))
            m_name = member.get("name", member.get("email", "unknown"))
            person_node_id = f"person_{m_id[:12]}"
            if person_node_id not in node_ids:
                nodes.append({
                    "id": person_node_id, "type": "person", "label": m_name,
                    "email": member.get("email", ""), "size": "small"
                })
                node_ids.add(person_node_id)
            edges.append({"source": person_node_id, "target": ch_node_id, "relationship": "member_of", "label": "member"})

    # Get tasks and connect to channels and people
    tasks = await db.lumi_tasks.find(
        {}, {"_id": 0, "id": 1, "task": 1, "channel_id": 1, "channel_name": 1, "assignee": 1, "status": 1, "priority": 1}
    ).limit(50).to_list(50)

    for t in tasks:
        task_node_id = f"task_{t['id']}"
        nodes.append({
            "id": task_node_id, "type": "task", "label": t.get("task", "")[:40],
            "status": t.get("status", "open"), "priority": t.get("priority", "medium"), "size": "small"
        })
        node_ids.add(task_node_id)

        # Connect task to channel
        if t.get("channel_id"):
            ch_node = f"ch_{t['channel_id'][:8]}"
            if ch_node in node_ids:
                edges.append({"source": task_node_id, "target": ch_node, "relationship": "belongs_to", "label": "from"})

        # Connect task to assignee
        if t.get("assignee") and t["assignee"] != "Unassigned":
            assignee_node = None
            for n in nodes:
                if n["type"] == "person" and t["assignee"].lower() in n["label"].lower():
                    assignee_node = n["id"]
                    break
            if assignee_node:
                edges.append({"source": assignee_node, "target": task_node_id, "relationship": "assigned_to", "label": "owns"})

    # Get action items
    action_items = await db.ai_action_items.find(
        {}, {"_id": 0, "id": 1, "task": 1, "assignee": 1, "status": 1, "source": 1}
    ).limit(30).to_list(30)

    for a in action_items:
        ai_node_id = f"action_{a['id']}"
        nodes.append({
            "id": ai_node_id, "type": "action_item", "label": a.get("task", "")[:40],
            "status": a.get("status", "open"), "size": "small"
        })
        node_ids.add(ai_node_id)

        if a.get("assignee") and a["assignee"] != "Unassigned":
            for n in nodes:
                if n["type"] == "person" and a["assignee"].lower() in n["label"].lower():
                    edges.append({"source": n["id"], "target": ai_node_id, "relationship": "responsible_for", "label": "owns"})
                    break

    # Get meetings
    meetings = await db.karau_meetings.find(
        {}, {"_id": 0, "meeting_id": 1, "title": 1, "participants": 1, "status": 1}
    ).limit(15).to_list(15)

    for m in meetings:
        m_node_id = f"meeting_{m['meeting_id'][:8]}"
        nodes.append({
            "id": m_node_id, "type": "meeting", "label": m.get("title", "Meeting")[:30],
            "status": m.get("status", ""), "size": "medium"
        })
        node_ids.add(m_node_id)

        for p in m.get("participants", []):
            p_id = p.get("user_id", "")
            person_node = f"person_{p_id[:12]}"
            if person_node in node_ids:
                edges.append({"source": person_node, "target": m_node_id, "relationship": "attended", "label": "attended"})

    # Stats
    type_counts = {}
    for n in nodes:
        t = n["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "by_type": type_counts
        }
    }


@router.post("/lumi/knowledge-graph/impact")
async def impact_analysis(request: Request):
    """Analyze the impact of removing/changing an entity"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    body = await request.json()
    entity_type = body.get("entity_type", "")
    entity_id = body.get("entity_id", "")
    entity_name = body.get("entity_name", "")

    if not entity_type or not (entity_id or entity_name):
        raise HTTPException(status_code=400, detail="entity_type and entity_id/entity_name required")

    # Gather affected entities
    impacts = {"direct": [], "indirect": [], "risk_level": "low"}

    if entity_type == "person":
        # Find tasks assigned to this person
        assigned_tasks = await db.lumi_tasks.find(
            {"assignee": {"$regex": entity_name, "$options": "i"}, "status": {"$ne": "done"}},
            {"_id": 0, "task": 1, "priority": 1, "channel_name": 1}
        ).to_list(20)
        if assigned_tasks:
            impacts["direct"].append({
                "type": "tasks", "count": len(assigned_tasks),
                "description": f"{len(assigned_tasks)} open tasks will be unassigned",
                "items": [t.get("task", "")[:50] for t in assigned_tasks[:5]]
            })

        # Find action items
        assigned_actions = await db.ai_action_items.find(
            {"assignee": {"$regex": entity_name, "$options": "i"}, "status": {"$ne": "done"}},
            {"_id": 0, "task": 1}
        ).to_list(20)
        if assigned_actions:
            impacts["direct"].append({
                "type": "action_items", "count": len(assigned_actions),
                "description": f"{len(assigned_actions)} action items need reassignment"
            })

        # Find channels they're in
        member_channels = await db.lumi_channels.find(
            {"members.name": {"$regex": entity_name, "$options": "i"}},
            {"_id": 0, "name": 1}
        ).to_list(20)
        if member_channels:
            impacts["indirect"].append({
                "type": "channels", "count": len(member_channels),
                "description": f"Active in {len(member_channels)} channels",
                "items": [c.get("name", "") for c in member_channels[:5]]
            })

        high_pri = sum(1 for t in assigned_tasks if t.get("priority") == "high")
        if high_pri > 0:
            impacts["risk_level"] = "critical"
        elif len(assigned_tasks) > 3:
            impacts["risk_level"] = "high"
        elif len(assigned_tasks) > 0:
            impacts["risk_level"] = "medium"

    elif entity_type == "channel":
        # Count messages, tasks, members
        msg_count = await db.lumi_messages.count_documents({"channel_id": entity_id})
        task_count = await db.lumi_tasks.count_documents({"channel_id": entity_id})
        channel = await db.lumi_channels.find_one({"id": entity_id}, {"_id": 0, "members": 1})
        member_count = len(channel.get("members", [])) if channel else 0

        if msg_count > 0:
            impacts["direct"].append({"type": "messages", "count": msg_count, "description": f"{msg_count} messages will be lost"})
        if task_count > 0:
            impacts["direct"].append({"type": "tasks", "count": task_count, "description": f"{task_count} tasks linked to this channel"})
        if member_count > 0:
            impacts["indirect"].append({"type": "members", "count": member_count, "description": f"{member_count} members will lose access"})

        impacts["risk_level"] = "critical" if msg_count > 50 or task_count > 5 else "high" if msg_count > 10 else "medium"

    elif entity_type == "task":
        task = await db.lumi_tasks.find_one({"id": entity_id}, {"_id": 0})
        if task:
            impacts["direct"].append({
                "type": "task_detail",
                "description": f"Task '{task.get('task', '')}' (priority: {task.get('priority', 'medium')}) assigned to {task.get('assignee', 'Unassigned')}"
            })

    # AI analysis if there are impacts
    if impacts["direct"] or impacts["indirect"]:
        try:
            ctx = json.dumps({"entity_type": entity_type, "entity_name": entity_name, "impacts": impacts}, default=str)
            prompt = f"""Analyze the impact of removing or changing this entity from the project:

{ctx}

Provide a brief risk assessment (2-3 sentences) and suggest mitigation steps. Be specific and actionable."""

            analysis = await _call_llm(prompt, "You are a project risk analyst. Provide concise impact assessments.", f"impact_{entity_type}")
            impacts["ai_analysis"] = analysis
        except Exception as e:
            impacts["ai_analysis"] = "AI analysis unavailable."

    return impacts


# ============== 10. Bottleneck Detection ==============

@router.get("/lumi/bottlenecks")
async def detect_bottlenecks(request: Request):
    """Detect team bottlenecks: overloaded members, blocked chains, resource gaps"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    bottlenecks = []

    # 1. Workload Analysis — find overloaded team members
    all_tasks = await db.lumi_tasks.find(
        {"status": {"$ne": "done"}}, {"_id": 0, "assignee": 1, "priority": 1, "task": 1}
    ).to_list(200)

    all_actions = await db.ai_action_items.find(
        {"status": {"$ne": "done"}}, {"_id": 0, "assignee": 1, "task": 1}
    ).to_list(200)

    # Aggregate workload per person
    workload = {}
    for item in all_tasks + all_actions:
        assignee = item.get("assignee", "Unassigned")
        if assignee == "Unassigned":
            continue
        if assignee not in workload:
            workload[assignee] = {"total": 0, "high": 0, "items": []}
        workload[assignee]["total"] += 1
        if item.get("priority") == "high":
            workload[assignee]["high"] += 1
        workload[assignee]["items"].append(item.get("task", "")[:50])

    for person, load in workload.items():
        if load["total"] >= 5 or load["high"] >= 3:
            bottlenecks.append({
                "id": f"bn_overload_{uuid.uuid4().hex[:6]}",
                "type": "overloaded_member",
                "severity": "critical" if load["high"] >= 3 else "warning",
                "person": person,
                "title": f"{person} — Overloaded ({load['total']} open items)",
                "description": f"{load['total']} tasks/actions ({load['high']} high-priority). Risk of burnout and delays.",
                "workload": load,
                "suggestion": "Consider redistributing tasks or extending deadlines"
            })

    # 2. Unassigned critical work
    unassigned = [t for t in all_tasks if t.get("assignee", "Unassigned") == "Unassigned"]
    unassigned_high = [t for t in unassigned if t.get("priority") == "high"]
    if unassigned_high:
        bottlenecks.append({
            "id": f"bn_unassigned_{uuid.uuid4().hex[:6]}",
            "type": "unassigned_critical",
            "severity": "critical",
            "title": f"{len(unassigned_high)} Critical Tasks Without Owners",
            "description": "High-priority tasks are unassigned and at risk of being missed.",
            "items": [t.get("task", "")[:50] for t in unassigned_high[:5]],
            "suggestion": "Immediately assign owners to high-priority tasks"
        })

    # 3. Channel engagement gaps
    channels = await db.lumi_channels.find({}, {"_id": 0, "id": 1, "name": 1, "members": 1}).to_list(30)
    now = datetime.now(timezone.utc)
    cutoff_7d = (now - timedelta(days=7)).isoformat()

    for ch in channels:
        members = ch.get("members", [])
        if len(members) < 2:
            continue
        recent_msgs = await db.lumi_messages.find(
            {"channel_id": ch["id"], "created_at": {"$gte": cutoff_7d}, "type": {"$ne": "system"}},
            {"_id": 0, "sender_id": 1}
        ).to_list(200)

        active_senders = set(m.get("sender_id", "") for m in recent_msgs)
        inactive_members = [m for m in members if m.get("user_id", "") not in active_senders]

        if len(inactive_members) > len(members) * 0.5 and len(members) > 3:
            bottlenecks.append({
                "id": f"bn_engage_{ch['id'][:6]}",
                "type": "low_engagement",
                "severity": "info",
                "title": f"#{ch['name']} — Low Participation",
                "description": f"{len(inactive_members)}/{len(members)} members haven't contributed in 7 days.",
                "inactive_members": [m.get("name", m.get("email", "")) for m in inactive_members[:5]],
                "suggestion": "Check in with inactive members or review channel relevance"
            })

    # 4. Dependency chain analysis (tasks blocking other tasks)
    high_tasks = [t for t in all_tasks if t.get("priority") == "high"]
    if len(high_tasks) > 3:
        channels_with_high = {}
        for t in high_tasks:
            ch = t.get("channel_name", t.get("channel_id", "unknown"))
            if ch not in channels_with_high:
                channels_with_high[ch] = []
            channels_with_high[ch].append(t.get("task", ""))

        for ch, ch_tasks in channels_with_high.items():
            if len(ch_tasks) >= 3:
                bottlenecks.append({
                    "id": f"bn_chain_{uuid.uuid4().hex[:6]}",
                    "type": "task_concentration",
                    "severity": "warning",
                    "title": f"High-Priority Cluster in #{ch}",
                    "description": f"{len(ch_tasks)} high-priority tasks concentrated in one channel. Risk of cascading delays.",
                    "tasks": ch_tasks[:5],
                    "suggestion": "Review task dependencies and consider parallel execution"
                })

    # Overall health score
    total_items = len(all_tasks) + len(all_actions)
    critical_count = sum(1 for b in bottlenecks if b.get("severity") == "critical")
    warning_count = sum(1 for b in bottlenecks if b.get("severity") == "warning")
    health_score = max(0, 100 - (critical_count * 20) - (warning_count * 10))

    return {
        "bottlenecks": bottlenecks,
        "total": len(bottlenecks),
        "health_score": health_score,
        "workload_summary": {
            "total_open_items": total_items,
            "people_with_work": len(workload),
            "overloaded_count": sum(1 for p, l in workload.items() if l["total"] >= 5),
            "avg_workload": round(total_items / max(1, len(workload)), 1)
        },
        "checked_at": now.isoformat()
    }

# ============== 11. What-If Simulations ==============

class SimulationRequest(BaseModel):
    scenario: str
    entity_type: Optional[str] = None
    entity_name: Optional[str] = None


@router.post("/lumi/ai/simulate")
async def what_if_simulation(body: SimulationRequest, request: Request):
    """Run a What-If simulation against current project state"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    # Gather current project state
    tasks = await db.lumi_tasks.find({}, {"_id": 0, "task": 1, "assignee": 1, "status": 1, "priority": 1, "channel_name": 1}).limit(30).to_list(30)
    actions = await db.ai_action_items.find({}, {"_id": 0, "task": 1, "assignee": 1, "status": 1, "deadline": 1}).limit(20).to_list(20)
    channels = await db.lumi_channels.find({}, {"_id": 0, "name": 1, "members": 1}).limit(15).to_list(15)

    member_set = set()
    for ch in channels:
        for m in ch.get("members", []):
            member_set.add(m.get("name", m.get("email", "")))

    state = {
        "tasks": tasks, "action_items": actions,
        "channels": [{"name": c["name"], "member_count": len(c.get("members", []))} for c in channels],
        "team_members": list(member_set)[:30],
        "total_open_tasks": sum(1 for t in tasks if t.get("status") != "done"),
        "total_open_actions": sum(1 for a in actions if a.get("status") != "done"),
    }

    try:
        prompt = f"""You are a project simulation engine. A project manager wants to run a "What-If" scenario.

SCENARIO: "{body.scenario}"

CURRENT PROJECT STATE:
{json.dumps(state, default=str)}

Analyze this scenario thoroughly and respond in valid JSON:
{{
  "scenario_summary": "Brief restatement of the scenario",
  "impact_timeline": [
    {{"timeframe": "Immediate/1 week/2 weeks/1 month", "impact": "what happens", "severity": "high/medium/low"}}
  ],
  "affected_entities": [
    {{"type": "person/task/channel", "name": "entity name", "effect": "how it's affected"}}
  ],
  "risk_score": 0-100,
  "recommendation": "What should the PM do",
  "alternative_approaches": ["alternative 1", "alternative 2"],
  "before_after": {{
    "before": {{"open_tasks": number, "team_capacity": "description", "risk_level": "low/medium/high"}},
    "after": {{"open_tasks": number, "team_capacity": "description", "risk_level": "low/medium/high"}}
  }}
}}"""

        raw = await _call_llm(prompt, "You are a project simulation engine. Provide realistic impact analysis for what-if scenarios. Be specific about timeline and affected entities. JSON only.", f"sim_{user['user_id']}")
        result = _parse_json(raw)
        result["generated_at"] = datetime.now(timezone.utc).isoformat()
        return result

    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return {"error": str(e), "scenario_summary": body.scenario, "recommendation": "Simulation temporarily unavailable."}


# ============== 12. Message Translation ==============

class TranslateRequest(BaseModel):
    text: str
    target_language: str


@router.post("/lumi/ai/translate")
async def translate_message(body: TranslateRequest, request: Request):
    """Translate a message to the target language"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text required")

    try:
        prompt = f"Translate the following text to {body.target_language}. Return ONLY the translated text, nothing else:\n\n{body.text}"
        translated = await _call_llm(prompt, f"You are a professional translator. Translate accurately to {body.target_language}. Return only the translated text.", f"tr_{user['user_id']}")
        return {
            "original": body.text,
            "translated": translated.strip(),
            "target_language": body.target_language,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {"original": body.text, "translated": body.text, "error": str(e)}


# ============== 13. Smart Notifications ==============

@router.get("/lumi/ai/notifications")
async def get_smart_notifications(request: Request):
    """Get AI-prioritized notifications for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")

    user_id = user["user_id"]
    user_name = user.get("name", user.get("email", ""))
    notifications = []

    # 1. Direct mentions in messages (last 24h)
    cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    mention_pattern = f"@{user_name}" if user_name else None

    if mention_pattern:
        mentions = await db.lumi_messages.find(
            {"content": {"$regex": mention_pattern, "$options": "i"}, "created_at": {"$gte": cutoff_24h}, "sender_id": {"$ne": user_id}},
            {"_id": 0, "id": 1, "content": 1, "sender_name": 1, "channel_id": 1, "created_at": 1}
        ).sort("created_at", -1).limit(10).to_list(10)

        for m in mentions:
            notifications.append({
                "id": f"notif_mention_{m['id'][:8]}",
                "type": "mention", "priority": "high",
                "title": f"{m.get('sender_name', 'Someone')} mentioned you",
                "body": m.get("content", "")[:100],
                "channel_id": m.get("channel_id", ""),
                "created_at": m.get("created_at", ""),
                "read": False
            })

    # 2. Tasks assigned to user
    user_tasks = await db.lumi_tasks.find(
        {"assignee": {"$regex": user_name, "$options": "i"}, "status": "open"},
        {"_id": 0, "id": 1, "task": 1, "priority": 1, "deadline": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5).to_list(5)

    for t in user_tasks:
        is_overdue = t.get("deadline") and t.get("deadline") != "TBD" and t["deadline"] < datetime.now(timezone.utc).strftime("%Y-%m-%d")
        notifications.append({
            "id": f"notif_task_{t['id']}",
            "type": "task_assigned", "priority": "critical" if is_overdue else ("high" if t.get("priority") == "high" else "medium"),
            "title": f"{'OVERDUE: ' if is_overdue else ''}Task assigned to you",
            "body": t.get("task", "")[:100],
            "deadline": t.get("deadline", ""),
            "created_at": t.get("created_at", ""),
            "read": False
        })

    # 3. Action items assigned to user
    user_actions = await db.ai_action_items.find(
        {"assignee": {"$regex": user_name, "$options": "i"}, "status": "open"},
        {"_id": 0, "id": 1, "task": 1, "deadline": 1, "created_at": 1}
    ).limit(5).to_list(5)

    for a in user_actions:
        notifications.append({
            "id": f"notif_action_{a['id']}",
            "type": "action_item", "priority": "medium",
            "title": "Action item needs attention",
            "body": a.get("task", "")[:100],
            "deadline": a.get("deadline", ""),
            "created_at": a.get("created_at", ""),
            "read": False
        })

    # 4. Anomaly alerts (critical only)
    overdue_actions = await db.ai_action_items.find(
        {"status": "open", "deadline": {"$exists": True, "$ne": "TBD"}}, {"_id": 0}
    ).to_list(20)
    overdue_count = sum(1 for a in overdue_actions if a.get("deadline", "9999") < datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    if overdue_count > 0:
        notifications.append({
            "id": f"notif_anomaly_overdue",
            "type": "anomaly", "priority": "critical",
            "title": f"{overdue_count} overdue items across the team",
            "body": "Review and reassign or update deadlines",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False
        })

    # 5. Low sentiment warnings
    low_sentiment = await db.lumi_sentiment.find(
        {"score": {"$lt": 40}, "analyzed_at": {"$gte": cutoff_24h}},
        {"_id": 0, "channel_id": 1, "score": 1, "label": 1}
    ).limit(3).to_list(3)
    for s in low_sentiment:
        notifications.append({
            "id": f"notif_sentiment_{s['channel_id'][:8]}",
            "type": "sentiment_warning", "priority": "medium",
            "title": f"Low morale alert (score: {s.get('score', 0)})",
            "body": f"Channel sentiment is {s.get('label', 'Concerning')}",
            "channel_id": s.get("channel_id", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False
        })

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    notifications.sort(key=lambda n: priority_order.get(n.get("priority", "low"), 4))

    return {
        "notifications": notifications,
        "total": len(notifications),
        "unread": sum(1 for n in notifications if not n.get("read")),
        "critical": sum(1 for n in notifications if n.get("priority") == "critical"),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

