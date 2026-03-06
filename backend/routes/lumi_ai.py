"""
LUMI AI Features - Writing Assistant, Smart Buckets, Translation, Voice-to-Text
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid
import tempfile

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/lumi/ai", tags=["LUMI AI"])

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")

# ============== Models ==============

class RefineRequest(BaseModel):
    text: str
    instruction: str  # "professional", "friendly", "assertive", "concise", "summarize", "custom"
    custom_prompt: Optional[str] = None

class SmartReplyRequest(BaseModel):
    messages: List[dict]  # Recent messages for context
    channel_name: Optional[str] = None

class TranslateRequest(BaseModel):
    text: str
    target_language: str  # "es", "fr", "de", "ja", "zh", "ko", etc.
    source_language: Optional[str] = None

class CategorizeRequest(BaseModel):
    messages: List[dict]  # Messages to categorize

# ============== AI Writing Assistant ==============

@router.post("/refine")
async def refine_text(req: RefineRequest):
    """Refine text tone: professional, friendly, assertive, concise, summarize"""
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    prompts = {
        "professional": "Rewrite the following text to sound more professional and polished for a business context. Keep the core meaning intact. Return ONLY the refined text, nothing else.",
        "friendly": "Rewrite the following text to sound warm, friendly, and approachable while keeping the meaning. Return ONLY the refined text.",
        "assertive": "Rewrite the following text to sound confident, direct, and assertive without being aggressive. Return ONLY the refined text.",
        "concise": "Make the following text shorter and more concise while keeping the key information. Return ONLY the refined text.",
        "summarize": "Summarize the following text in 1-2 sentences capturing the key points. Return ONLY the summary.",
    }

    system = prompts.get(req.instruction, req.custom_prompt or prompts["professional"])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"refine-{uuid.uuid4().hex[:8]}",
        system_message=system
    ).with_model("openai", "gpt-4.1-mini")

    try:
        response = await chat.send_message(UserMessage(text=req.text))
        return {"refined_text": response, "instruction": req.instruction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI refinement failed: {str(e)}")


@router.post("/smart-reply")
async def smart_reply(req: SmartReplyRequest):
    """Generate smart reply suggestions based on conversation context"""
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    context = "\n".join([f"{m.get('sender', 'User')}: {m.get('content', '')}" for m in req.messages[-10:]])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"reply-{uuid.uuid4().hex[:8]}",
        system_message="Based on the conversation context, suggest 3 brief, natural reply options. Return them as a JSON array of strings, e.g. [\"reply1\", \"reply2\", \"reply3\"]. Keep each under 50 words. Match the conversation's tone."
    ).with_model("openai", "gpt-4.1-mini")

    try:
        response = await chat.send_message(UserMessage(text=f"Conversation in #{req.channel_name or 'channel'}:\n{context}\n\nSuggest 3 replies:"))
        import json as json_mod
        try:
            suggestions = json_mod.loads(response)
            if not isinstance(suggestions, list):
                suggestions = [response]
        except:
            suggestions = [s.strip().strip('"').strip("'") for s in response.split("\n") if s.strip()][:3]
        return {"suggestions": suggestions[:3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart reply failed: {str(e)}")


# ============== Smart Buckets ==============

@router.post("/categorize")
async def categorize_messages(req: CategorizeRequest):
    """AI-powered message categorization into Smart Buckets"""
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    messages_text = "\n".join([
        f"[{m.get('id', 'msg')}] {m.get('sender', 'User')}: {m.get('content', '')}"
        for m in req.messages[:20]
    ])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"cat-{uuid.uuid4().hex[:8]}",
        system_message="""Categorize each message into one of these buckets:
- "urgent": Contains ASAP, deadline, critical, emergency, or time-sensitive content
- "action_required": Questions directed at the user, pending tasks, requests needing response
- "meeting": Calendar invites, scheduling requests, "let's meet", "can we sync"
- "missed": Mentions of missed calls, "tried to reach you", follow-up reminders
- "normal": Regular conversation, updates, FYI messages

Return a JSON object mapping message IDs to categories, e.g. {"msg1": "urgent", "msg2": "normal"}"""
    ).with_model("openai", "gpt-4.1-mini")

    try:
        response = await chat.send_message(UserMessage(text=messages_text))
        import json as json_mod
        try:
            categories = json_mod.loads(response)
        except:
            categories = {}
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")


# ============== Real-time Translation ==============

@router.post("/translate")
async def translate_text(req: TranslateRequest):
    """Translate message text to target language"""
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    lang_names = {
        "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
        "zh": "Chinese", "ko": "Korean", "pt": "Portuguese", "ar": "Arabic",
        "hi": "Hindi", "ru": "Russian", "it": "Italian", "nl": "Dutch",
        "tr": "Turkish", "pl": "Polish", "sv": "Swedish", "th": "Thai",
    }
    target = lang_names.get(req.target_language, req.target_language)

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"trans-{uuid.uuid4().hex[:8]}",
        system_message=f"Translate the following text to {target}. Return ONLY the translated text, nothing else. Preserve formatting and tone."
    ).with_model("openai", "gpt-4.1-mini")

    try:
        response = await chat.send_message(UserMessage(text=req.text))
        return {"translated_text": response, "target_language": req.target_language, "target_name": target}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


# ============== Voice-to-Text ==============

@router.post("/voice-to-text")
async def voice_to_text(file: UploadFile = File(...)):
    """Transcribe voice audio to polished text using Whisper"""
    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="AI key not configured")

    allowed = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "ogg"}
    ext = file.filename.split(".")[-1].lower() if file.filename else "webm"
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    from emergentintegrations.llm.openai import OpenAISpeechToText

    try:
        # Save to temp file
        suffix = f".{ext}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        stt = OpenAISpeechToText(api_key=EMERGENT_KEY)
        with open(tmp_path, "rb") as audio:
            response = await stt.transcribe(
                file=audio,
                model="whisper-1",
                response_format="json",
                language="en"
            )

        raw_text = response.text

        # Polish the text using LLM
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        polish_chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"polish-{uuid.uuid4().hex[:8]}",
            system_message="Clean up this transcribed speech. Remove filler words (um, uh, like, you know), fix grammar, and structure it into clear professional text. Keep the meaning and tone. Return ONLY the polished text."
        ).with_model("openai", "gpt-4.1-mini")

        polished = await polish_chat.send_message(UserMessage(text=raw_text))

        # Cleanup
        os.unlink(tmp_path)

        return {"raw_text": raw_text, "polished_text": polished}
    except Exception as e:
        if 'tmp_path' in locals():
            try: os.unlink(tmp_path)
            except: pass
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
