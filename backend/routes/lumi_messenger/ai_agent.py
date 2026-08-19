"""ENZI AI channel assistant — @AI agentic commands posted in-channel."""
import os
import re
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from utils.database import db
from routes.auth import get_current_user
from ._common import manager

router = APIRouter()

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
AI_HOURLY_LIMIT = 10


class AICommand(BaseModel):
    query: str


def _parse_intent(q: str):
    ql = q.lower().strip()
    if ql.startswith(("summarize", "summary", "recap")):
        return "summarize", None
    if "action item" in ql or ql.startswith(("actions", "extract action", "tasks", "todo")):
        return "actions", None
    if ql.startswith("translate"):
        m = re.search(r"(?:to|into)\s+([a-zA-Z\- ]+?)\s*$", q.strip())
        return "translate", (m.group(1).strip().title() if m else "English")
    return "ask", None


_SYSTEM_PROMPTS = {
    "summarize": "You are ENZI AI, the in-channel assistant. Summarize the conversation concisely in markdown: **Key topics**, **Decisions**, **Open questions** (omit empty sections). Max 150 words.",
    "actions": "You are ENZI AI, the in-channel assistant. Extract action items from the conversation as a markdown checklist. Format each as '- [ ] task — @owner' when an owner is identifiable. If there are none, say 'No action items found in the recent conversation.'",
    "ask": "You are ENZI AI, the in-channel assistant. Answer the user's question using the conversation context. Be concise and helpful. If the answer isn't in the conversation, answer from general knowledge and say so briefly.",
}


@router.post("/channels/{channel_id}/ai")
async def channel_ai_assistant(channel_id: str, data: AICommand, request: Request):
    """@AI assistant: summarize / action items / translate / Q&A, posted as a channel message."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    channel = await db.lumi_channels.find_one(
        {"id": channel_id, "members.user_id": user["user_id"]}, {"_id": 0, "id": 1, "name": 1}
    )
    if not channel:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    query = (data.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    intent, target_lang = _parse_intent(query)

    hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    used = await db.enzi_ai_usage.count_documents({"user_id": user["user_id"], "ts": {"$gte": hour_ago}})
    if used >= AI_HOURLY_LIMIT:
        raise HTTPException(status_code=429, detail=f"AI request limit reached ({AI_HOURLY_LIMIT}/hour). Please try again later.")

    cursor = db.lumi_messages.find(
        {"channel_id": channel_id, "sender_id": {"$ne": "enzi_ai"}},
        {"_id": 0, "sender_name": 1, "content": 1},
    ).sort("created_at", -1).limit(30)
    recent = await cursor.to_list(length=30)
    recent.reverse()
    context = "\n".join(f"{m.get('sender_name', 'User')}: {m.get('content', '')}" for m in recent)

    if intent == "translate":
        system = f"You are ENZI AI. Translate the conversation messages into {target_lang}. Keep the 'Sender: message' format, one per line. Return ONLY the translated lines."
    else:
        system = _SYSTEM_PROMPTS[intent]

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"enzi-ai-{uuid.uuid4().hex[:8]}",
        system_message=system,
    ).with_model("openai", "gpt-4.1-mini")

    prompt = f"Conversation in #{channel.get('name', 'channel')}:\n{context or '(no recent messages)'}\n\nRequest from {user.get('name', 'a member')}: {query}"
    try:
        response = await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ENZI AI failed: {str(e)}")

    await db.enzi_ai_usage.insert_one({"user_id": user["user_id"], "ts": datetime.now(timezone.utc).isoformat()})

    ai_msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "channel_id": channel_id,
        "sender_id": "enzi_ai",
        "sender_name": "ENZI AI",
        "content": str(response),
        "type": "ai_assistant",
        "ai_intent": intent,
        "requested_by": user.get("name", user.get("email", "")),
        "reply_to": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reactions": {},
    }
    await db.lumi_messages.insert_one(ai_msg)
    ai_msg.pop("_id", None)

    await db.lumi_channels.update_one(
        {"id": channel_id},
        {"$set": {"last_message": {"content": ai_msg["content"][:120], "sender_name": "ENZI AI"},
                  "last_message_at": ai_msg["created_at"]},
         "$inc": {"message_count": 1}},
    )
    await manager.send_to_channel(channel_id, {"type": "message", "data": ai_msg})
    return ai_msg
