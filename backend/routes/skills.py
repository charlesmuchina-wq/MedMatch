"""
Skill Assessment Routes
Handles: Skill verification tests, certifications, badges
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import json
import random

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["Skill Assessments"])

# ============== Models ==============

class StartAssessmentRequest(BaseModel):
    skill_name: str
    difficulty: str = "intermediate"  # beginner, intermediate, advanced

class SubmitAnswerRequest(BaseModel):
    assessment_id: str
    question_index: int
    answer: str

class SubmitAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[dict]  # [{question_index: 0, answer: "A"}, ...]

# ============== Available Assessments ==============

SKILL_ASSESSMENTS = {
    "Python": {
        "category": "Programming",
        "questions": 15,
        "time_limit": 25,  # minutes
        "passing_score": 70,
        "badge_icon": "🐍",
        "badge_color": "#3776AB"
    },
    "JavaScript": {
        "category": "Programming",
        "questions": 15,
        "time_limit": 25,
        "passing_score": 70,
        "badge_icon": "⚡",
        "badge_color": "#F7DF1E"
    },
    "React": {
        "category": "Frontend",
        "questions": 15,
        "time_limit": 25,
        "passing_score": 70,
        "badge_icon": "⚛️",
        "badge_color": "#61DAFB"
    },
    "SQL": {
        "category": "Database",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "🗄️",
        "badge_color": "#336791"
    },
    "AWS": {
        "category": "Cloud",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "☁️",
        "badge_color": "#FF9900"
    },
    "Machine Learning": {
        "category": "AI/ML",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "🤖",
        "badge_color": "#FF6F00"
    },
    "Data Science": {
        "category": "AI/ML",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "📊",
        "badge_color": "#4B8BBE"
    },
    "Project Management": {
        "category": "Business",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "📋",
        "badge_color": "#00A36C"
    },
    "Agile/Scrum": {
        "category": "Business",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "🔄",
        "badge_color": "#6495ED"
    },
    "Communication": {
        "category": "Soft Skills",
        "questions": 10,
        "time_limit": 15,
        "passing_score": 70,
        "badge_icon": "💬",
        "badge_color": "#9B59B6"
    }
}

# ============== Routes ==============

@router.get("/available")
async def get_available_assessments():
    """Get list of available skill assessments"""
    assessments = []
    for skill, config in SKILL_ASSESSMENTS.items():
        assessments.append({
            "skill_name": skill,
            "category": config["category"],
            "questions": config["questions"],
            "time_limit": config["time_limit"],
            "passing_score": config["passing_score"],
            "badge_icon": config["badge_icon"],
            "badge_color": config["badge_color"]
        })
    
    # Group by category
    categories = {}
    for a in assessments:
        cat = a["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)
    
    return {"assessments": assessments, "by_category": categories}

@router.get("/my-badges")
async def get_my_badges(request: Request):
    """Get all badges earned by current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    badges = await db.skill_badges.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("earned_at", -1).to_list(100)
    
    return {"badges": badges, "total": len(badges)}

@router.post("/start")
async def start_assessment(req: StartAssessmentRequest, request: Request):
    """Start a skill assessment"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if req.skill_name not in SKILL_ASSESSMENTS:
        raise HTTPException(status_code=400, detail=f"Assessment not available for {req.skill_name}")
    
    config = SKILL_ASSESSMENTS[req.skill_name]
    
    # Check for cooldown (can't retake for 24 hours if failed)
    recent_attempt = await db.skill_assessments.find_one({
        "user_id": user["user_id"],
        "skill_name": req.skill_name,
        "status": "failed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}
    })
    
    if recent_attempt:
        raise HTTPException(status_code=400, detail="Please wait 24 hours before retaking this assessment")
    
    # Generate questions using AI
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    from datetime import timedelta
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message=f"""You are an expert assessment creator for {req.skill_name}. 
Generate {config['questions']} multiple choice questions to test {req.difficulty} level knowledge.

Return ONLY valid JSON array with this structure:
[
    {{
        "question": "What is...",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "correct_answer": "A",
        "explanation": "Brief explanation of why A is correct",
        "difficulty": "{req.difficulty}"
    }}
]

Questions should cover practical, real-world scenarios and test genuine understanding.
Include a mix of conceptual and practical questions."""
    ).with_model("openai", "gpt-5.2")
    
    try:
        response = await chat.send_message(UserMessage(
            text=f"Generate {config['questions']} {req.difficulty} level assessment questions for {req.skill_name}."
        ))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        questions = json.loads(clean_response)
        
        # Store questions but remove answers from response
        assessment = {
            "id": f"assess_{uuid.uuid4().hex[:12]}",
            "user_id": user["user_id"],
            "skill_name": req.skill_name,
            "difficulty": req.difficulty,
            "questions": questions,  # Full questions with answers (server-side only)
            "status": "in_progress",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "time_limit": config["time_limit"],
            "passing_score": config["passing_score"],
            "answers_submitted": [],
            "score": None
        }
        
        await db.skill_assessments.insert_one(assessment)
        
        # Return questions without correct answers
        client_questions = []
        for i, q in enumerate(questions):
            client_questions.append({
                "index": i,
                "question": q["question"],
                "options": q["options"]
            })
        
        return {
            "assessment_id": assessment["id"],
            "skill_name": req.skill_name,
            "questions": client_questions,
            "time_limit": config["time_limit"],
            "total_questions": len(questions)
        }
        
    except Exception as e:
        logging.error(f"Assessment generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate assessment")

@router.post("/submit")
async def submit_assessment(submission: SubmitAssessmentRequest, request: Request):
    """Submit completed assessment and get results"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    assessment = await db.skill_assessments.find_one({
        "id": submission.assessment_id,
        "user_id": user["user_id"],
        "status": "in_progress"
    })
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found or already completed")
    
    # Calculate score
    questions = assessment["questions"]
    correct_count = 0
    results = []
    
    for answer in submission.answers:
        q_idx = answer.get("question_index", 0)
        user_answer = answer.get("answer", "")
        
        if q_idx < len(questions):
            correct = questions[q_idx]["correct_answer"]
            is_correct = user_answer.upper().startswith(correct.upper())
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_index": q_idx,
                "question": questions[q_idx]["question"],
                "your_answer": user_answer,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": questions[q_idx].get("explanation", "")
            })
    
    score = round(correct_count / len(questions) * 100, 1) if questions else 0
    passed = score >= assessment["passing_score"]
    
    # Update assessment
    await db.skill_assessments.update_one(
        {"id": submission.assessment_id},
        {"$set": {
            "status": "passed" if passed else "failed",
            "score": score,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "answers_submitted": submission.answers,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Award badge if passed
    badge = None
    if passed:
        config = SKILL_ASSESSMENTS.get(assessment["skill_name"], {})
        badge = {
            "id": f"badge_{uuid.uuid4().hex[:12]}",
            "user_id": user["user_id"],
            "skill_name": assessment["skill_name"],
            "difficulty": assessment["difficulty"],
            "score": score,
            "badge_icon": config.get("badge_icon", "🏆"),
            "badge_color": config.get("badge_color", "#4CAF50"),
            "earned_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,  # Badges don't expire
            "verified": True
        }
        
        await db.skill_badges.insert_one(badge)
        
        # Add skill to user's verified skills
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"verified_skills": {
                "skill": assessment["skill_name"],
                "level": assessment["difficulty"],
                "score": score,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }}}
        )
        
        # Update resume with verified badge
        await db.resumes.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"verified_skills": assessment["skill_name"]}}
        )
    
    return {
        "passed": passed,
        "score": score,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "passing_score": assessment["passing_score"],
        "results": results,
        "badge": badge,
        "message": f"Congratulations! You earned the {assessment['skill_name']} badge!" if passed else f"You need {assessment['passing_score']}% to pass. Try again in 24 hours."
    }

@router.get("/history")
async def get_assessment_history(request: Request):
    """Get user's assessment history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    assessments = await db.skill_assessments.find(
        {"user_id": user["user_id"], "status": {"$ne": "in_progress"}},
        {"_id": 0, "questions": 0, "answers_submitted": 0}  # Don't return questions/answers
    ).sort("completed_at", -1).to_list(50)
    
    return {"history": assessments}

@router.get("/leaderboard/{skill_name}")
async def get_skill_leaderboard(skill_name: str):
    """Get top scorers for a skill"""
    if skill_name not in SKILL_ASSESSMENTS:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Get top 10 scorers
    top_scores = await db.skill_assessments.aggregate([
        {"$match": {"skill_name": skill_name, "status": "passed"}},
        {"$sort": {"score": -1, "completed_at": 1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user"
        }},
        {"$project": {
            "_id": 0,
            "score": 1,
            "difficulty": 1,
            "completed_at": 1,
            "user_name": {"$arrayElemAt": ["$user.name", 0]}
        }}
    ]).to_list(10)
    
    # Add rank
    for i, score in enumerate(top_scores):
        score["rank"] = i + 1
        if not score.get("user_name"):
            score["user_name"] = "Anonymous"
    
    return {"skill_name": skill_name, "leaderboard": top_scores}

@router.get("/verify/{user_id}/{skill_name}")
async def verify_skill_badge(user_id: str, skill_name: str):
    """Public endpoint to verify a user's skill badge"""
    badge = await db.skill_badges.find_one(
        {"user_id": user_id, "skill_name": skill_name},
        {"_id": 0}
    )
    
    if not badge:
        return {"verified": False, "message": "Badge not found"}
    
    return {
        "verified": True,
        "skill_name": badge["skill_name"],
        "difficulty": badge["difficulty"],
        "score": badge["score"],
        "earned_at": badge["earned_at"],
        "badge_icon": badge["badge_icon"]
    }
