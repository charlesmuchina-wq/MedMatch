"""
Smart Apply Routes
AiApply-like intelligent job application automation.
Features:
- Resume-based job matching with 24h freshness filter
- AI cover letter generation per matched job
- Batch auto-apply with application tracking
- Configurable preferences (roles, location, salary)
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import json
import logging
import asyncio

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/smart-apply", tags=["Smart Apply"])


class SmartApplyConfig(BaseModel):
    target_roles: List[str] = []
    locations: List[str] = ["Remote"]
    location_type: str = ""
    exclude_companies: List[str] = []
    min_salary: Optional[int] = None
    max_applications_per_run: int = 10
    auto_generate_cover_letter: bool = True


class SmartApplyRunRequest(BaseModel):
    job_title: str
    location: str = "Remote"
    max_jobs: int = 10


@router.get("/config")
async def get_smart_apply_config(request: Request):
    """Get user's Smart Apply preferences."""
    user = await require_auth(request)
    config = await db.smart_apply_configs.find_one(
        {"user_id": user["user_id"]}, {"_id": 0}
    )
    if not config:
        config = {
            "user_id": user["user_id"],
            "target_roles": [],
            "locations": ["Remote"],
            "location_type": "",
            "exclude_companies": [],
            "min_salary": None,
            "max_applications_per_run": 10,
            "auto_generate_cover_letter": True,
        }
    return config


@router.put("/config")
async def update_smart_apply_config(config: SmartApplyConfig, request: Request):
    """Save user's Smart Apply preferences."""
    user = await require_auth(request)
    doc = config.model_dump()
    doc["user_id"] = user["user_id"]
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.smart_apply_configs.update_one(
        {"user_id": user["user_id"]},
        {"$set": doc},
        upsert=True,
    )
    return {"message": "Config saved"}


@router.post("/run")
async def run_smart_apply(data: SmartApplyRunRequest, request: Request):
    """
    Run the Smart Apply bot:
    1. Fetch user resume
    2. Search for matching jobs (posted within 24h)
    3. Score & rank matches against resume
    4. Generate cover letters for top matches
    5. Record applications
    """
    user = await require_auth(request)
    user_id = user["user_id"]

    # 1. Get user resume
    resume = await db.resumes.find_one({"user_id": user_id}, {"_id": 0})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first")

    # Get config
    config = await db.smart_apply_configs.find_one({"user_id": user_id}, {"_id": 0})
    exclude_companies = [c.lower() for c in (config or {}).get("exclude_companies", [])]

    # 2. Search for jobs
    from routes.jobs import get_job_sources_service, GOOGLE_API_KEY, GOOGLE_CSE_ID

    job_service = get_job_sources_service(GOOGLE_API_KEY, GOOGLE_CSE_ID)
    all_jobs = await job_service.search_all_sources(
        query=data.job_title,
        location=data.location,
        limit_per_source=30,
    )

    # 3. Filter: 24h window + exclude companies + dedup
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    seen_urls = set()
    fresh_jobs = []

    for job in all_jobs:
        url = job.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Exclude companies
        company = (job.get("company", "") or "").lower()
        if any(exc in company for exc in exclude_companies):
            continue

        # Check freshness (if date available)
        posted_str = job.get("date") or job.get("posted_at") or ""
        is_fresh = True
        if posted_str:
            try:
                posted = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
                is_fresh = posted >= cutoff
            except Exception:
                is_fresh = True  # keep if unparseable

        if is_fresh:
            fresh_jobs.append(job)

    # 4. Score against resume
    resume_skills = set()
    for s in resume.get("skills", []):
        name = s.get("name", s) if isinstance(s, dict) else str(s)
        resume_skills.add(name.lower())

    resume_titles = [t.lower() for t in resume.get("job_titles", [])]
    resume_summary = (resume.get("summary", "") or "").lower()

    for job in fresh_jobs:
        title = (job.get("title", "") or "").lower()
        desc = (job.get("description", "") or "").lower()
        tags = " ".join([str(t).lower() for t in job.get("tags", [])])
        combined = f"{title} {desc} {tags}"

        # Skill match
        matched_skills = [s for s in resume_skills if s in combined]
        skill_score = min(len(matched_skills) * 8, 50)

        # Title match
        title_score = 0
        query_lower = data.job_title.lower()
        if query_lower in title:
            title_score = 35
        elif any(t in title for t in resume_titles):
            title_score = 25
        elif any(w in title for w in query_lower.split() if len(w) > 3):
            title_score = 15

        job["match_score"] = min(skill_score + title_score, 100)
        job["matched_skills"] = matched_skills[:10]

    # Sort by match score
    fresh_jobs.sort(key=lambda j: j.get("match_score", 0), reverse=True)
    top_jobs = fresh_jobs[: data.max_jobs]

    # 5. Check already-applied
    applied_urls = set()
    existing = await db.applications.find(
        {"user_id": user_id},
        {"_id": 0, "job.url": 1, "external_url": 1},
    ).to_list(500)
    for app in existing:
        applied_urls.add(app.get("external_url", ""))
        applied_urls.add(app.get("job", {}).get("url", ""))

    # 6. Generate cover letters + record applications
    results = []
    run_id = str(uuid.uuid4())[:8]

    for job in top_jobs:
        job_url = job.get("url", "")
        already = job_url in applied_urls
        cover_letter = None
        cover_letter_preview = None

        if not already and EMERGENT_LLM_KEY and (config or {}).get("auto_generate_cover_letter", True):
            try:
                chat = LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id=f"sa-{run_id}-{uuid.uuid4().hex[:6]}",
                    system_message="You are an expert career coach. Write a compelling, concise cover letter (200 words max). Return ONLY the letter text, no JSON, no extra formatting.",
                ).with_model("openai", "gpt-4o")

                prompt = f"""Write a cover letter for:
Job: {job.get('title', '')} at {job.get('company', '')}
Description: {(job.get('description', '') or '')[:1500]}

Candidate:
Name: {resume.get('full_name', user.get('name', 'Applicant'))}
Skills: {', '.join(list(resume_skills)[:15])}
Summary: {resume.get('summary', '')[:500]}
Experience: {json.dumps(resume.get('experience', [])[:2], default=str)[:500]}"""

                cover_letter = await chat.send_message(UserMessage(text=prompt))
                cover_letter = cover_letter.strip()
                if cover_letter.startswith("```"):
                    cover_letter = cover_letter.split("```")[1].strip()
                cover_letter_preview = cover_letter[:200] + "..." if len(cover_letter) > 200 else cover_letter
            except Exception as e:
                logging.warning(f"Smart Apply cover letter error: {e}")
                cover_letter = None

        # Record application
        if not already:
            application = {
                "id": f"sa-{run_id}-{uuid.uuid4().hex[:8]}",
                "user_id": user_id,
                "job": {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "url": job_url,
                    "location": job.get("location", ""),
                    "description": (job.get("description", "") or "")[:500],
                },
                "status": "Applied",
                "job_status": "Active",
                "applied_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "external_url": job_url,
                "source": "smart_apply",
                "smart_apply_run": run_id,
                "match_score": job.get("match_score", 0),
                "cover_letter": cover_letter,
            }
            await db.applications.insert_one(application)
            applied_urls.add(job_url)

        results.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job_url,
            "location": job.get("location", ""),
            "match_score": job.get("match_score", 0),
            "matched_skills": job.get("matched_skills", []),
            "already_applied": already,
            "cover_letter_generated": cover_letter is not None,
            "cover_letter_preview": cover_letter_preview,
        })

    # Save run history
    await db.smart_apply_runs.insert_one({
        "id": run_id,
        "user_id": user_id,
        "job_title": data.job_title,
        "location": data.location,
        "total_found": len(fresh_jobs),
        "total_applied": sum(1 for r in results if not r["already_applied"]),
        "total_skipped": sum(1 for r in results if r["already_applied"]),
        "results": results,
        "created_at": now.isoformat(),
    })

    return {
        "run_id": run_id,
        "job_title": data.job_title,
        "total_jobs_found": len(fresh_jobs),
        "total_matched": len(top_jobs),
        "total_applied": sum(1 for r in results if not r["already_applied"]),
        "total_skipped": sum(1 for r in results if r["already_applied"]),
        "results": results,
    }


@router.get("/history")
async def get_smart_apply_history(request: Request):
    """Get Smart Apply run history."""
    user = await require_auth(request)
    runs = (
        await db.smart_apply_runs.find(
            {"user_id": user["user_id"]}, {"_id": 0}
        )
        .sort("created_at", -1)
        .to_list(20)
    )
    return {"runs": runs}
