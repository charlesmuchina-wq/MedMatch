"""
AI Candidate Scoring & Job Intelligence Routes
Semantic skill matching, candidate scoring, job description generation
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-talent", tags=["AI Talent Intelligence"])


class CandidateScoringRequest(BaseModel):
    job_title: str
    job_description: str
    required_skills: List[str] = []
    candidate_name: str
    candidate_resume: str
    candidate_skills: List[str] = []

class CandidateScoreResponse(BaseModel):
    overall_score: int
    skill_match_score: int
    experience_match_score: int
    culture_fit_score: int
    strengths: List[str]
    gaps: List[str]
    recommendation: str
    detailed_analysis: str

class JobDescriptionRequest(BaseModel):
    title: str
    department: Optional[str] = ""
    seniority: Optional[str] = "mid"
    key_responsibilities: List[str] = []
    required_skills: List[str] = []
    company_name: Optional[str] = ""
    industry: Optional[str] = "life sciences"

class InterviewScorecardRequest(BaseModel):
    job_id: str
    candidate_id: str
    interviewer_name: str
    scores: Dict[str, int]
    notes: str = ""
    recommendation: str = "neutral"


@router.post("/score-candidate", response_model=CandidateScoreResponse)
async def score_candidate(req: CandidateScoringRequest):
    """AI-powered candidate scoring against job requirements"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")

        chat = LlmChat(
            api_key=api_key,
            session_id=f"scoring-{datetime.now(timezone.utc).timestamp()}",
            system_message="""You are an expert talent acquisition analyst specializing in life sciences and engineering.
Score candidates against job requirements on a 0-100 scale. Be objective and data-driven.
Always respond in this exact JSON format:
{
  "overall_score": 75,
  "skill_match_score": 80,
  "experience_match_score": 70,
  "culture_fit_score": 75,
  "strengths": ["Strength 1", "Strength 2"],
  "gaps": ["Gap 1", "Gap 2"],
  "recommendation": "Strong Match / Moderate Match / Weak Match",
  "detailed_analysis": "2-3 paragraph analysis"
}"""
        )

        prompt = f"""Score this candidate for the role:

JOB: {req.job_title}
DESCRIPTION: {req.job_description}
REQUIRED SKILLS: {', '.join(req.required_skills)}

CANDIDATE: {req.candidate_name}
RESUME: {req.candidate_resume}
SKILLS: {', '.join(req.candidate_skills)}

Provide a detailed scoring analysis."""

        response = await chat.send_message(UserMessage(text=prompt))

        import json
        try:
            text = response.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            parsed = json.loads(text.strip())
        except json.JSONDecodeError:
            parsed = {
                "overall_score": 50,
                "skill_match_score": 50,
                "experience_match_score": 50,
                "culture_fit_score": 50,
                "strengths": ["Unable to parse detailed analysis"],
                "gaps": ["Review manually"],
                "recommendation": "Review Required",
                "detailed_analysis": response
            }

        return CandidateScoreResponse(**parsed)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Candidate scoring error: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/generate-job-description")
async def generate_job_description(req: JobDescriptionRequest):
    """AI-powered job description generator"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")

        chat = LlmChat(
            api_key=api_key,
            session_id=f"jd-gen-{datetime.now(timezone.utc).timestamp()}",
            system_message="""You are an expert technical recruiter for life sciences and engineering companies.
Generate professional, inclusive, and compelling job descriptions. Include sections for:
- About the Role
- Key Responsibilities
- Required Qualifications
- Preferred Qualifications
- What We Offer
Use inclusive language and avoid biased terms. Return plain text, well-formatted with markdown."""
        )

        prompt = f"""Generate a job description:
Title: {req.title}
Department: {req.department}
Seniority: {req.seniority}
Company: {req.company_name}
Industry: {req.industry}
Key Responsibilities: {', '.join(req.key_responsibilities) if req.key_responsibilities else 'Generate appropriate ones'}
Required Skills: {', '.join(req.required_skills) if req.required_skills else 'Generate appropriate ones'}"""

        response = await chat.send_message(UserMessage(text=prompt))
        return {"job_description": response, "title": req.title}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JD generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# --- Interview Scorecards ---

@router.post("/scorecards")
async def create_scorecard(req: InterviewScorecardRequest, request: Request):
    """Create an interview scorecard"""
    try:
        from server import db
        scorecard = {
            "job_id": req.job_id,
            "candidate_id": req.candidate_id,
            "interviewer_name": req.interviewer_name,
            "scores": req.scores,
            "notes": req.notes,
            "recommendation": req.recommendation,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.interview_scorecards.insert_one(scorecard)
        scorecard["scorecard_id"] = str(result.inserted_id)
        scorecard.pop("_id", None)
        return scorecard
    except Exception as e:
        logger.error(f"Scorecard creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create scorecard")


@router.get("/scorecards/{job_id}/{candidate_id}")
async def get_scorecards(job_id: str, candidate_id: str, request: Request):
    """Get all scorecards for a candidate's job application"""
    try:
        from server import db
        scorecards = await db.interview_scorecards.find(
            {"job_id": job_id, "candidate_id": candidate_id}, {"_id": 0}
        ).to_list(50)
        
        # Calculate averages
        if scorecards:
            all_scores = {}
            for sc in scorecards:
                for key, val in sc.get("scores", {}).items():
                    if key not in all_scores:
                        all_scores[key] = []
                    all_scores[key].append(val)
            
            avg_scores = {k: round(sum(v) / len(v), 1) for k, v in all_scores.items()}
        else:
            avg_scores = {}

        return {
            "scorecards": scorecards,
            "average_scores": avg_scores,
            "total_reviews": len(scorecards)
        }
    except Exception as e:
        logger.error(f"Error fetching scorecards: {e}")
        return {"scorecards": [], "average_scores": {}, "total_reviews": 0}


# --- Hiring Analytics ---

@router.get("/hiring-metrics")
async def get_hiring_metrics(request: Request):
    """Get time-to-hire and other recruitment metrics, computed from data.

    Status handling is case-insensitive and tolerant of the several status
    vocabularies the ``applications`` collection is written with (candidate
    self-apply writes "Applied", ATS intake writes "received", recruiters write
    "hired"/"rejected"/...). ``avg_cost_per_hire`` is never fabricated — it is
    surfaced only if an operator has configured it in ``recruiting_settings``.
    """
    try:
        from server import db
        from analytics_utils import tally_statuses, average_time_to_hire, source_effectiveness

        total_apps = await db.applications.count_documents({})

        # Status breakdown (case-insensitive; merges "Applied"/"applied" etc.)
        status_rows = await db.applications.aggregate([
            {"$group": {"_id": {"$toLower": "$status"}, "count": {"$sum": 1}}}
        ]).to_list(100)
        counts_by_status = {(r["_id"] or "unknown"): r["count"] for r in status_rows}
        tallied = tally_statuses(counts_by_status)
        hired = tallied["hired"]
        rejected = tallied["rejected"]
        in_progress = tallied["in_progress"]
        pipeline_dict = tallied["pipeline"]

        # Job statistics
        total_jobs = await db.jobs.count_documents({})
        active_jobs = await db.jobs.count_documents({"status": "active"})

        hire_rate = round((hired / total_apps * 100), 1) if total_apps > 0 else 0

        # Real time-to-hire from hired applications' timestamps (bounded fetch).
        hired_apps = await db.applications.find(
            {"status": {"$regex": "^hired$", "$options": "i"}},
            {"_id": 0, "applied_at": 1, "created_at": 1, "submitted_at": 1,
             "updated_at": 1, "status_updated_at": 1, "hired_at": 1,
             "source": 1, "job.source": 1},
        ).to_list(5000)
        avg_time_to_hire_days = average_time_to_hire(hired_apps)

        # Source effectiveness: share of hires by source, falling back to share
        # of all applications by source when there are no hires yet.
        if hired_apps:
            source_eff = source_effectiveness(hired_apps)
        else:
            all_apps = await db.applications.find(
                {}, {"_id": 0, "source": 1, "job.source": 1}
            ).to_list(5000)
            source_eff = source_effectiveness(all_apps)

        # Cost-per-hire has no source data in the app; expose it only when an
        # operator has configured it. Never fabricated.
        cost_setting = await db.recruiting_settings.find_one({"key": "cost_per_hire"})
        avg_cost_per_hire = cost_setting.get("value") if cost_setting else None

        return {
            "total_applications": total_apps,
            "hired": hired,
            "rejected": rejected,
            "in_progress": in_progress,
            "hire_rate": hire_rate,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "pipeline": pipeline_dict,
            "avg_time_to_hire_days": avg_time_to_hire_days,
            "avg_cost_per_hire": avg_cost_per_hire,
            "source_effectiveness": source_eff,
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return {
            "total_applications": 0, "hired": 0, "rejected": 0,
            "in_progress": 0, "hire_rate": 0, "total_jobs": 0,
            "active_jobs": 0, "pipeline": {},
            "avg_time_to_hire_days": 0, "avg_cost_per_hire": None,
            "source_effectiveness": {}
        }
