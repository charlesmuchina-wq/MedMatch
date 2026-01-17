"""
Dragon AI Routes
Handles: KARAU DRAGON AI voice assistant commands, intent processing, web search
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json
import httpx

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from routes.auth import get_current_user

router = APIRouter(prefix="/dragon", tags=["KARAU Dragon AI"])

# ============== Models ==============

class DragonCommand(BaseModel):
    command: str
    user_context: Dict[str, Any] = {}

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5

# ============== Dragon AI Intent Processing ==============

INTENT_ACTIONS = {
    "cover_letter": {
        "path": "/cover-letter",
        "label": "Cover Letter Generator",
        "color": "#10B981"
    },
    "job_search": {
        "path": "/search",
        "label": "Job Search",
        "color": "#3B82F6"
    },
    "interview_prep": {
        "path": "/interview",
        "label": "Interview Prep",
        "color": "#8B5CF6"
    },
    "resume": {
        "path": "/resume",
        "label": "My Resume",
        "color": "#F59E0B"
    },
    "prediction": {
        "path": "/predictor",
        "label": "Success Predictor",
        "color": "#EF4444"
    },
    "companies": {
        "path": "/companies",
        "label": "Companies",
        "color": "#06B6D4"
    },
    "interviews": {
        "path": "/interviews",
        "label": "Interview Scheduling",
        "color": "#EC4899"
    },
    "skills": {
        "path": "/skill-assessments",
        "label": "Skill Tests",
        "color": "#F97316"
    },
    "analytics": {
        "path": "/analytics",
        "label": "Analytics Dashboard",
        "color": "#14B8A6"
    },
    "salary": {
        "path": "/salary-insights",
        "label": "Salary Insights",
        "color": "#84CC16"
    },
    "messages": {
        "path": "/messages",
        "label": "Messages",
        "color": "#6366F1"
    },
    "web_search": {
        "path": None,
        "label": "Web Search",
        "color": "#6366F1"
    }
}

@router.post("/process")
async def process_dragon_command(data: DragonCommand, request: Request):
    """Process a KARAU Dragon AI voice/text command"""
    user = await get_current_user(request)
    command = data.command.lower().strip()
    user_context = data.user_context

    # Try AI-powered intent detection first
    if EMERGENT_LLM_KEY:
        try:
            result = await ai_intent_detection(command, user_context)
            
            # Log the command
            await log_dragon_command(user, command, result)
            
            return result
        except Exception as e:
            logging.error(f"AI intent detection failed: {e}")
    
    # Fallback to rule-based detection
    result = rule_based_intent_detection(command, user_context)
    
    # Log the command
    await log_dragon_command(user, command, result)
    
    return result

async def ai_intent_detection(command: str, user_context: Dict) -> Dict:
    """Use AI to detect intent and generate response"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are KARAU DRAGON AI, an intelligent job search assistant. 
Analyze the user's command and determine the intent.

Available intents:
- cover_letter: Generate or help with cover letters
- job_search: Find jobs, search positions
- interview_prep: Prepare for interviews, practice questions
- resume: View, edit, or manage resume
- prediction: Predict job application success
- companies: Research companies, browse company profiles
- interviews: View or schedule interviews
- skills: Take skill assessments
- analytics: View job search analytics
- salary: Get salary insights
- messages: Check messages
- web_search: Search the internet for information

Return ONLY valid JSON:
{
    "intent": "<intent_name>",
    "speech": "<friendly response to speak to user>",
    "params": {
        "company": "<company name if mentioned>",
        "role": "<job role if mentioned>",
        "query": "<search query if needed>"
    },
    "requires_web": <true if web search needed, false otherwise>,
    "confidence": <0.0-1.0>
}"""
    ).with_model("openai", "gpt-5.2")

    user_name = user_context.get("user_name", "there")
    
    response = await chat.send_message(UserMessage(
        text=f"User '{user_name}' says: {command}"
    ))
    
    # Parse AI response
    clean_response = response.strip()
    if clean_response.startswith("```"):
        clean_response = clean_response.split("```")[1]
        if clean_response.startswith("json"):
            clean_response = clean_response[4:]
    
    result = json.loads(clean_response)
    
    # Add action details
    intent = result.get("intent", "unknown")
    if intent in INTENT_ACTIONS:
        result["action"] = INTENT_ACTIONS[intent]
    
    return result

def rule_based_intent_detection(command: str, user_context: Dict) -> Dict:
    """Fallback rule-based intent detection"""
    cmd = command.lower()
    user_name = user_context.get("user_name", "there")
    
    # Cover letter intents
    if any(phrase in cmd for phrase in ["cover letter", "write letter", "application letter"]):
        company = extract_company(cmd)
        role = extract_role(cmd)
        
        speech = f"I'll help you create a cover letter"
        if role:
            speech += f" for a {role} position"
        if company:
            speech += f" at {company}"
        speech += ". Taking you to the cover letter generator."
        
        return {
            "intent": "cover_letter",
            "speech": speech,
            "action": INTENT_ACTIONS["cover_letter"],
            "params": {"company": company, "role": role},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Job search intents
    if any(phrase in cmd for phrase in ["find job", "search job", "look for job", "job search", "find position"]):
        role = extract_role(cmd)
        location = extract_location(cmd)
        
        speech = f"Searching for {role or 'jobs'}"
        if location:
            speech += f" in {location}"
        speech += ". Let me find the best opportunities for you."
        
        return {
            "intent": "job_search",
            "speech": speech,
            "action": INTENT_ACTIONS["job_search"],
            "params": {"query": role or "", "location": location or ""},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Interview prep
    if any(phrase in cmd for phrase in ["interview prep", "prepare interview", "practice interview", "interview question"]):
        company = extract_company(cmd)
        role = extract_role(cmd)
        
        speech = "Let's prepare you for your interview"
        if company:
            speech += f" at {company}"
        speech += ". I'll generate relevant questions."
        
        return {
            "intent": "interview_prep",
            "speech": speech,
            "action": INTENT_ACTIONS["interview_prep"],
            "params": {"company": company, "role": role},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Success prediction
    if any(phrase in cmd for phrase in ["predict", "chance", "probability", "likelihood", "success rate"]):
        return {
            "intent": "prediction",
            "speech": "I'll analyze your profile and predict your success rate for job applications.",
            "action": INTENT_ACTIONS["prediction"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Resume
    if any(phrase in cmd for phrase in ["resume", "cv", "my profile"]):
        return {
            "intent": "resume",
            "speech": "Taking you to your resume. You can view, upload, or edit your professional profile.",
            "action": INTENT_ACTIONS["resume"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Companies
    if any(phrase in cmd for phrase in ["company", "companies", "research company", "about company"]):
        company = extract_company(cmd)
        
        speech = "Opening the companies directory"
        if company:
            speech = f"Let me find information about {company}"
        
        return {
            "intent": "companies",
            "speech": speech,
            "action": INTENT_ACTIONS["companies"],
            "params": {"company": company},
            "requires_web": bool(company),
            "confidence": 0.85
        }
    
    # Interviews/Schedule
    if any(phrase in cmd for phrase in ["my interview", "scheduled interview", "interview schedule", "upcoming interview"]):
        return {
            "intent": "interviews",
            "speech": "Opening your interview schedule.",
            "action": INTENT_ACTIONS["interviews"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Skills
    if any(phrase in cmd for phrase in ["skill", "assessment", "test", "certification"]):
        return {
            "intent": "skills",
            "speech": "Taking you to the skill assessments. You can test your knowledge and earn badges.",
            "action": INTENT_ACTIONS["skills"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Analytics
    if any(phrase in cmd for phrase in ["analytics", "statistics", "dashboard", "progress"]):
        return {
            "intent": "analytics",
            "speech": "Opening your analytics dashboard to show your job search progress.",
            "action": INTENT_ACTIONS["analytics"],
            "params": {},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Salary
    if any(phrase in cmd for phrase in ["salary", "pay", "compensation", "how much"]):
        role = extract_role(cmd)
        
        return {
            "intent": "salary",
            "speech": f"Let me get salary insights{' for ' + role if role else ''}.",
            "action": INTENT_ACTIONS["salary"],
            "params": {"role": role},
            "requires_web": False,
            "confidence": 0.85
        }
    
    # Messages
    if any(phrase in cmd for phrase in ["message", "inbox", "chat"]):
        return {
            "intent": "messages",
            "speech": "Opening your messages.",
            "action": INTENT_ACTIONS["messages"],
            "params": {},
            "requires_web": False,
            "confidence": 0.9
        }
    
    # Web search (fallback for queries)
    if any(phrase in cmd for phrase in ["search", "find", "what is", "who is", "tell me about", "look up"]):
        return {
            "intent": "web_search",
            "speech": "Let me search the web for that information.",
            "action": INTENT_ACTIONS["web_search"],
            "params": {"query": command},
            "requires_web": True,
            "confidence": 0.7
        }
    
    # Unknown intent
    return {
        "intent": "unknown",
        "speech": f"Hi {user_name}! I can help you with cover letters, job searches, interview prep, resume management, skill tests, and company research. What would you like to do?",
        "suggestions": [
            "Generate a cover letter for Medtronic",
            "Find quality engineer jobs",
            "Prepare for my interview",
            "Show my resume",
            "Take a skill assessment"
        ],
        "confidence": 0.3
    }

def extract_company(text: str) -> Optional[str]:
    """Extract company name from text"""
    import re
    
    # Common patterns
    patterns = [
        r'(?:for|at|with)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
        r'(?:company|organization)\s+([A-Z][a-zA-Z]+)',
    ]
    
    # Known companies (extend this list)
    known_companies = [
        "medtronic", "johnson", "abbott", "stryker", "boston scientific",
        "google", "amazon", "microsoft", "apple", "meta", "netflix",
        "tesla", "spacex", "boeing", "lockheed", "raytheon",
        "pfizer", "merck", "novartis", "roche", "astrazeneca"
    ]
    
    text_lower = text.lower()
    for company in known_companies:
        if company in text_lower:
            return company.title()
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_role(text: str) -> Optional[str]:
    """Extract job role from text"""
    roles = [
        "supplier quality engineer", "supplier quality manager", "supplier quality",
        "quality engineer", "quality manager", "quality director",
        "manufacturing engineer", "process engineer", "production manager",
        "software engineer", "developer", "data scientist", "machine learning",
        "project manager", "program manager", "product manager",
        "sales manager", "marketing manager", "account manager",
        "analyst", "consultant", "designer", "architect"
    ]
    
    text_lower = text.lower()
    for role in roles:
        if role in text_lower:
            return role.title()
    
    return None

def extract_location(text: str) -> Optional[str]:
    """Extract location from text"""
    import re
    
    # Pattern for "in [Location]"
    match = re.search(r'in\s+([A-Za-z\s,]+?)(?:\s+at|\s+for|$)', text, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        if location.lower() not in ["a", "the", "my"]:
            return location
    
    # Check for common locations
    locations = ["remote", "new york", "san francisco", "chicago", "los angeles", "austin", "seattle", "boston"]
    text_lower = text.lower()
    for loc in locations:
        if loc in text_lower:
            return loc.title()
    
    return None

async def log_dragon_command(user: Optional[Dict], command: str, result: Dict):
    """Log Dragon AI commands for analytics"""
    try:
        log_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"] if user else None,
            "command": command,
            "intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.dragon_logs.insert_one(log_doc)
    except Exception as e:
        logging.error(f"Failed to log dragon command: {e}")

# ============== Web Search ==============

@router.post("/web-search")
async def dragon_web_search(data: WebSearchRequest, request: Request):
    """Perform web search for Dragon AI"""
    user = await get_current_user(request)
    
    results = []
    
    # Try Google Custom Search if configured
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": GOOGLE_API_KEY,
                        "cx": GOOGLE_CSE_ID,
                        "q": data.query,
                        "num": data.num_results
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    for item in search_data.get("items", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", "")
                        })
        except Exception as e:
            logging.error(f"Google search error: {e}")
    
    # Fallback: Use AI to generate relevant information
    if not results and EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=str(uuid.uuid4()),
                system_message="You are a helpful assistant. Provide brief, factual information."
            ).with_model("openai", "gpt-5.2")
            
            response = await chat.send_message(UserMessage(
                text=f"Provide a brief, helpful response about: {data.query}"
            ))
            
            results.append({
                "title": "AI Generated Response",
                "url": "",
                "snippet": response[:500]
            })
        except Exception as e:
            logging.error(f"AI fallback error: {e}")
    
    return {"results": results, "query": data.query}

# ============== Dragon Analytics ==============

@router.get("/analytics")
async def get_dragon_analytics(request: Request):
    """Get Dragon AI usage analytics (admin only)"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get intent distribution
    pipeline = [
        {"$group": {"_id": "$intent", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    intent_stats = await db.dragon_logs.aggregate(pipeline).to_list(20)
    
    # Get total commands
    total_commands = await db.dragon_logs.count_documents({})
    
    # Get unique users
    unique_users = len(await db.dragon_logs.distinct("user_id"))
    
    return {
        "total_commands": total_commands,
        "unique_users": unique_users,
        "intent_distribution": {item["_id"]: item["count"] for item in intent_stats if item["_id"]}
    }
