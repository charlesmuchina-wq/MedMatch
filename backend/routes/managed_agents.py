"""
Managed Agents — Claude-powered agentic worklists & automation.

Capabilities:
  1. First-class trackable worklist tasks (CRUD + stats).
  2. Auto-extract a worklist (action items with owners/priority/due) from a
     meeting transcript or a stored recording/meeting using Claude.
  3. A conversational agent with real tool-use: Claude decides to call our
     server-side tools (list/create/update tasks, send follow-up email),
     we execute them in a loop and feed results back until it answers.
  4. Agent definitions — admin templates + client-built custom agents.

Powered by Claude (claude-sonnet-4-6) via the Emergent universal key using the
emergentintegrations LlmChat. Tool-use is implemented with a strict JSON
action protocol (the library does not expose native function-calling).
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os
import json
import logging
import re

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from routes.auth import require_auth
from services.email_service import send_email

logger = logging.getLogger(__name__)
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
AGENT_MODEL = ("anthropic", "claude-sonnet-4-6")

router = APIRouter(prefix="/agents", tags=["Managed Agents"])

VALID_STATUS = {"open", "in_progress", "done"}
VALID_PRIORITY = {"low", "medium", "high"}

# ── Admin-curated agent templates (client can also build custom ones) ────────
AGENT_TEMPLATES = [
    {
        "id": "tpl_meeting_followup",
        "name": "Meeting Follow-up Agent",
        "description": "Turns meeting outcomes into tracked tasks and drafts follow-up emails to attendees.",
        "icon": "list-checks",
        "system_prompt": (
            "You are a meeting follow-up assistant. Help the user capture action items as "
            "tracked tasks, review what is open, and draft/send concise follow-up emails. "
            "Be proactive: when the user describes outcomes, create tasks for each owner."
        ),
        "is_template": True,
    },
    {
        "id": "tpl_worklist_manager",
        "name": "Worklist Manager",
        "description": "Conversational task manager — create, prioritize, and close worklist items by chatting.",
        "icon": "kanban",
        "system_prompt": (
            "You are a worklist manager. Help the user create, update, prioritize and "
            "complete tasks. Always confirm what you changed and surface what's still open."
        ),
        "is_template": True,
    },
    {
        "id": "tpl_recruiting_ops",
        "name": "Recruiting Ops Agent",
        "description": "Coordinates candidate follow-ups, interview action items, and reminder emails.",
        "icon": "users",
        "system_prompt": (
            "You are a recruiting operations agent for a talent platform. Convert interview "
            "and hiring discussions into owner-assigned tasks and send candidate/recruiter "
            "follow-up emails when asked."
        ),
        "is_template": True,
    },
]


# ═══════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    assignee: Optional[str] = ""
    priority: str = "medium"
    due_date: Optional[str] = None
    source: Optional[str] = "manual"
    source_label: Optional[str] = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class ExtractRequest(BaseModel):
    transcript: Optional[str] = None
    meeting_id: Optional[str] = None
    source_label: Optional[str] = ""


class AgentDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    system_prompt: str
    icon: Optional[str] = "bot"


class AgentChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════
def _task_public(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


def _extract_json(text: str):
    """Best-effort parse of a JSON object/array from an LLM response."""
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    # Fall back to first balanced {...} or [...]
    for opener, closer in (("{", "}"), ("[", "]")):
        start = t.find(opener)
        end = t.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(t[start:end + 1])
            except Exception:
                continue
    return None


async def _llm(system_message: str, prompt: str) -> str:
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="LLM key not configured")
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"agent_{uuid.uuid4().hex[:12]}",
        system_message=system_message,
    ).with_model(*AGENT_MODEL)
    return await chat.send_message(UserMessage(text=prompt))


async def _get_transcript(meeting_id: str, user_id: str) -> Optional[str]:
    """Resolve a transcript from meeting_notes or karau_recordings."""
    mn = await db.meeting_notes.find_one({"id": meeting_id, "user_id": user_id}, {"_id": 0})
    if mn and mn.get("transcript"):
        return mn["transcript"]
    rec = await db.karau_recordings.find_one({"recording_id": meeting_id}, {"_id": 0})
    if rec and (rec.get("transcription") or {}).get("text"):
        return rec["transcription"]["text"]
    return None


# ═══════════════════════════════════════════════════════════════
# Agent tools (server-side) — operate on the authenticated user's worklist
# ═══════════════════════════════════════════════════════════════
async def _tool_list_tasks(user_id: str, args: dict) -> dict:
    query = {"user_id": user_id}
    status = args.get("status")
    if status in VALID_STATUS:
        query["status"] = status
    tasks = await db.agent_tasks.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"count": len(tasks), "tasks": [
        {"id": t["id"], "title": t["title"], "status": t["status"],
         "priority": t["priority"], "assignee": t.get("assignee", ""),
         "due_date": t.get("due_date")} for t in tasks
    ]}


async def _tool_create_task(user_id: str, args: dict) -> dict:
    title = (args.get("title") or "").strip()
    if not title:
        return {"error": "title is required"}
    doc = {
        "id": f"task_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "title": title,
        "description": args.get("description", ""),
        "assignee": args.get("assignee", ""),
        "priority": args.get("priority") if args.get("priority") in VALID_PRIORITY else "medium",
        "status": "open",
        "due_date": args.get("due_date"),
        "source": args.get("source", "agent"),
        "source_label": args.get("source_label", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_tasks.insert_one(doc)
    return {"created": True, "id": doc["id"], "title": doc["title"]}


async def _resolve_task(user_id: str, args: dict):
    if args.get("task_id"):
        return await db.agent_tasks.find_one({"id": args["task_id"], "user_id": user_id})
    if args.get("title"):
        return await db.agent_tasks.find_one(
            {"user_id": user_id, "title": {"$regex": re.escape(args["title"]), "$options": "i"}}
        )
    return None


async def _tool_update_task(user_id: str, args: dict) -> dict:
    task = await _resolve_task(user_id, args)
    if not task:
        return {"error": "task not found"}
    update = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if args.get("status") in VALID_STATUS:
        update["status"] = args["status"]
    if args.get("priority") in VALID_PRIORITY:
        update["priority"] = args["priority"]
    if args.get("assignee") is not None:
        update["assignee"] = args["assignee"]
    if args.get("due_date") is not None:
        update["due_date"] = args["due_date"]
    await db.agent_tasks.update_one({"id": task["id"]}, {"$set": update})
    return {"updated": True, "id": task["id"], "changes": {k: v for k, v in update.items() if k != "updated_at"}}


async def _tool_send_followup_email(user_id: str, args: dict) -> dict:
    to = (args.get("to") or "").strip()
    subject = (args.get("subject") or "Follow-up").strip()
    body = (args.get("body") or "").strip()
    if not to or "@" not in to:
        return {"error": "a valid 'to' email is required"}
    html = f"<div style='font-family:sans-serif;font-size:15px;line-height:1.6'>{body.replace(chr(10), '<br>')}</div>"
    result = await send_email(to_email=to, subject=subject, html_content=html, text_content=body)
    return {"sent": bool(result.get("success")), "to": to, "subject": subject, "provider": result.get("provider")}


TOOLS = {
    "list_tasks": _tool_list_tasks,
    "create_task": _tool_create_task,
    "update_task": _tool_update_task,
    "send_followup_email": _tool_send_followup_email,
}

TOOL_SPEC = """Available tools (call ONE per step):
- list_tasks(status?: "open"|"in_progress"|"done") — list the user's worklist tasks.
- create_task(title: string, description?, assignee?, priority?: "low"|"medium"|"high", due_date?) — add a task.
- update_task(task_id? | title?, status?, priority?, assignee?, due_date?) — modify an existing task (identify by task_id or title).
- send_followup_email(to: email, subject: string, body: string) — send a follow-up email."""


async def _run_agent_loop(user_id: str, user_message: str, system_prompt: str, max_steps: int = 6) -> dict:
    """ReAct-style JSON tool loop on top of Claude text generation."""
    system_message = (
        f"{system_prompt}\n\n{TOOL_SPEC}\n\n"
        "Respond with ONLY a single JSON object, no prose, no markdown fences.\n"
        'To use a tool: {\"action\":\"tool\",\"tool\":\"<name>\",\"args\":{...},\"thought\":\"<short>\"}\n'
        'When finished: {\"action\":\"final\",\"reply\":\"<message to the user>\"}\n'
        "Use at most a few tool calls. After each tool you receive its JSON result."
    )
    transcript = [f"User request: {user_message}"]
    actions: List[dict] = []

    for _ in range(max_steps):
        prompt = "\n".join(transcript) + "\n\nReturn the next JSON action now."
        raw = await _llm(system_message, prompt)
        parsed = _extract_json(raw)
        if not isinstance(parsed, dict):
            return {"reply": raw.strip(), "actions": actions}
        if parsed.get("action") == "final":
            return {"reply": parsed.get("reply", ""), "actions": actions}
        if parsed.get("action") == "tool":
            tool_name = parsed.get("tool")
            tool_fn = TOOLS.get(tool_name)
            args = parsed.get("args") or {}
            if not tool_fn:
                obs = {"error": f"unknown tool '{tool_name}'"}
            else:
                try:
                    obs = await tool_fn(user_id, args)
                except Exception as e:
                    logger.error(f"agent tool {tool_name} error: {e}")
                    obs = {"error": str(e)}
            actions.append({"tool": tool_name, "args": args, "result": obs})
            transcript.append(f"You called {tool_name}({json.dumps(args)}) -> {json.dumps(obs)}")
            continue
        # Unrecognized shape
        return {"reply": parsed.get("reply") or raw.strip(), "actions": actions}

    return {"reply": "I've completed the available steps. Let me know if you'd like more.", "actions": actions}


# ═══════════════════════════════════════════════════════════════
# Worklist task endpoints
# ═══════════════════════════════════════════════════════════════
@router.post("/tasks")
async def create_task(body: TaskCreate, request: Request):
    user = await require_auth(request)
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    doc = {
        "id": f"task_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "title": body.title.strip(),
        "description": body.description or "",
        "assignee": body.assignee or "",
        "priority": body.priority if body.priority in VALID_PRIORITY else "medium",
        "status": "open",
        "due_date": body.due_date,
        "source": body.source or "manual",
        "source_label": body.source_label or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_tasks.insert_one(doc)
    return _task_public(dict(doc))


@router.get("/tasks")
async def list_tasks(request: Request, status: Optional[str] = None, assignee: Optional[str] = None):
    user = await require_auth(request)
    query = {"user_id": user["user_id"]}
    if status in VALID_STATUS:
        query["status"] = status
    if assignee:
        query["assignee"] = assignee
    tasks = await db.agent_tasks.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"tasks": tasks, "count": len(tasks)}


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate, request: Request):
    user = await require_auth(request)
    update: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.title is not None:
        update["title"] = body.title
    if body.description is not None:
        update["description"] = body.description
    if body.assignee is not None:
        update["assignee"] = body.assignee
    if body.priority is not None:
        if body.priority not in VALID_PRIORITY:
            raise HTTPException(status_code=400, detail="Invalid priority")
        update["priority"] = body.priority
    if body.status is not None:
        if body.status not in VALID_STATUS:
            raise HTTPException(status_code=400, detail="Invalid status")
        update["status"] = body.status
    if body.due_date is not None:
        update["due_date"] = body.due_date
    result = await db.agent_tasks.update_one(
        {"id": task_id, "user_id": user["user_id"]}, {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    doc = await db.agent_tasks.find_one({"id": task_id}, {"_id": 0})
    return doc


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, request: Request):
    user = await require_auth(request)
    result = await db.agent_tasks.delete_one({"id": task_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.post("/tasks/run-reminders")
async def run_reminders_now(request: Request):
    """Manually trigger the overdue meeting-task reminder cycle."""
    await require_auth(request)
    from services.task_reminder_service import run_task_reminders
    return await run_task_reminders()


@router.post("/digest/run")
async def run_digest_now(request: Request):
    """Send the daily digest to the requesting user immediately."""
    user = await require_auth(request)
    from services.task_reminder_service import run_daily_digest
    return await run_daily_digest(only_user_id=user["user_id"], force=True)


class DigestPrefs(BaseModel):
    hour: Optional[int] = None
    timezone: Optional[str] = None


@router.get("/digest/preferences")
async def get_digest_preferences(request: Request):
    user = await require_auth(request)
    prefs = await db.enzi_digest_prefs.find_one({"user_id": user["user_id"]}, {"_id": 0}) or {}
    return {"hour": prefs.get("hour", 7), "timezone": prefs.get("timezone", "UTC")}


@router.put("/digest/preferences")
async def update_digest_preferences(body: DigestPrefs, request: Request):
    user = await require_auth(request)
    update = {}
    if body.hour is not None:
        if not 0 <= body.hour <= 23:
            raise HTTPException(status_code=400, detail="hour must be 0-23")
        update["hour"] = body.hour
    if body.timezone is not None:
        from zoneinfo import ZoneInfo
        try:
            ZoneInfo(body.timezone)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid IANA timezone")
        update["timezone"] = body.timezone
    if not update:
        raise HTTPException(status_code=400, detail="Provide hour and/or timezone")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.enzi_digest_prefs.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"user_id": user["user_id"], **update}}, upsert=True)
    prefs = await db.enzi_digest_prefs.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {"hour": prefs.get("hour", 7), "timezone": prefs.get("timezone", "UTC")}


@router.get("/tasks-stats")
async def task_stats(request: Request):
    user = await require_auth(request)
    uid = user["user_id"]
    total = await db.agent_tasks.count_documents({"user_id": uid})
    open_c = await db.agent_tasks.count_documents({"user_id": uid, "status": "open"})
    prog_c = await db.agent_tasks.count_documents({"user_id": uid, "status": "in_progress"})
    done_c = await db.agent_tasks.count_documents({"user_id": uid, "status": "done"})
    return {
        "total": total, "open": open_c, "in_progress": prog_c, "done": done_c,
        "completion_rate": round(done_c / max(1, total) * 100),
    }


# ═══════════════════════════════════════════════════════════════
# Worklist extraction from transcript
# ═══════════════════════════════════════════════════════════════
@router.post("/extract-worklist")
async def extract_worklist(body: ExtractRequest, request: Request):
    user = await require_auth(request)
    transcript = (body.transcript or "").strip()
    label = body.source_label or "Meeting"
    source = "transcript"
    if not transcript and body.meeting_id:
        transcript = (await _get_transcript(body.meeting_id, user["user_id"]) or "").strip()
        source = f"meeting:{body.meeting_id}"
    if not transcript:
        raise HTTPException(status_code=400, detail="Provide a transcript or a meeting_id with a transcript")

    system_message = (
        "You are an expert meeting analyst. Extract concrete, actionable follow-up tasks "
        "from a meeting transcript. Respond ONLY with a JSON array."
    )
    prompt = f"""From the transcript below, extract a worklist of action items.

TRANSCRIPT:
{transcript[:12000]}

Return ONLY a JSON array. Each item:
{{"title": "short imperative task", "assignee": "owner name or empty", "priority": "low|medium|high", "due_date": "natural-language deadline or empty", "description": "1-line context"}}
Return [] if there are no action items."""

    raw = await _llm(system_message, prompt)
    parsed = _extract_json(raw)
    items = parsed if isinstance(parsed, list) else []

    created = []
    now = datetime.now(timezone.utc).isoformat()
    for it in items[:25]:
        if not isinstance(it, dict) or not (it.get("title") or "").strip():
            continue
        doc = {
            "id": f"task_{uuid.uuid4().hex[:12]}",
            "user_id": user["user_id"],
            "title": it["title"].strip()[:200],
            "description": (it.get("description") or "")[:500],
            "assignee": (it.get("assignee") or "")[:120],
            "priority": it.get("priority") if it.get("priority") in VALID_PRIORITY else "medium",
            "status": "open",
            "due_date": (it.get("due_date") or None),
            "source": source,
            "source_label": label,
            "created_at": now,
            "updated_at": now,
        }
        await db.agent_tasks.insert_one(doc)
        created.append(_task_public(dict(doc)))

    return {"extracted": len(created), "tasks": created}


# ═══════════════════════════════════════════════════════════════
# Agent definitions (templates + custom)
# ═══════════════════════════════════════════════════════════════
@router.get("/definitions")
async def list_definitions(request: Request):
    user = await require_auth(request)
    custom = await db.agent_definitions.find(
        {"owner_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {"templates": AGENT_TEMPLATES, "custom": custom}


@router.post("/definitions")
async def create_definition(body: AgentDefinitionCreate, request: Request):
    user = await require_auth(request)
    if not body.name.strip() or not body.system_prompt.strip():
        raise HTTPException(status_code=400, detail="name and system_prompt are required")
    doc = {
        "id": f"agent_{uuid.uuid4().hex[:12]}",
        "owner_id": user["user_id"],
        "name": body.name.strip(),
        "description": body.description or "",
        "system_prompt": body.system_prompt.strip(),
        "icon": body.icon or "bot",
        "is_template": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_definitions.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.delete("/definitions/{agent_id}")
async def delete_definition(agent_id: str, request: Request):
    user = await require_auth(request)
    result = await db.agent_definitions.delete_one({"id": agent_id, "owner_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"deleted": True}


async def _resolve_agent_prompt(agent_id: Optional[str], user_id: str) -> str:
    default = AGENT_TEMPLATES[1]["system_prompt"]
    if not agent_id:
        return default
    for tpl in AGENT_TEMPLATES:
        if tpl["id"] == agent_id:
            return tpl["system_prompt"]
    doc = await db.agent_definitions.find_one({"id": agent_id, "owner_id": user_id}, {"_id": 0})
    return doc["system_prompt"] if doc else default


# ═══════════════════════════════════════════════════════════════
# Conversational agent with tool-use
# ═══════════════════════════════════════════════════════════════
@router.post("/chat")
async def agent_chat(body: AgentChatRequest, request: Request):
    user = await require_auth(request)
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    system_prompt = await _resolve_agent_prompt(body.agent_id, user["user_id"])
    session_id = body.session_id or f"sess_{uuid.uuid4().hex[:12]}"

    result = await _run_agent_loop(user["user_id"], body.message.strip(), system_prompt)

    run = {
        "id": f"run_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "agent_id": body.agent_id,
        "session_id": session_id,
        "input": body.message.strip(),
        "reply": result["reply"],
        "actions": result["actions"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_runs.insert_one(dict(run))
    run.pop("_id", None)
    return {"session_id": session_id, "reply": result["reply"], "actions": result["actions"]}


@router.get("/status")
async def agent_status(request: Request):
    await require_auth(request)
    return {"available": bool(EMERGENT_LLM_KEY), "model": "claude-sonnet-4-6", "tools": list(TOOLS.keys())}
