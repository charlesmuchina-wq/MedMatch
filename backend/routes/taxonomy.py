"""
Taxonomy API Routes
Endpoints for sector, role, certification, and skill management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from services.taxonomy import (
    SECTORS, SENIORITY_TIERS, CERTIFICATIONS, SKILLS, CAREER_PIVOTS, JOB_BOARDS,
    get_all_roles, get_all_certifications, get_all_skills,
    get_certifications_for_sector, get_skills_for_sector,
    get_career_pivots_from_sector, get_career_pivots_to_sector,
    match_role_to_sector, estimate_seniority_tier
)

router = APIRouter(prefix="/taxonomy", tags=["Taxonomy"])

# ============== Response Models ==============

class SectorResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    subsectors: dict

class CertificationResponse(BaseModel):
    code: str
    name: str
    org: str
    sector: List[str]
    category_id: str
    category_name: str

class SkillResponse(BaseModel):
    name: str
    sector: List[str]
    category_id: str
    category_name: str

class CareerPivotResponse(BaseModel):
    from_sector: str
    from_role: str
    to_sector: str
    to_role: str
    transferable_skills: List[str]
    bridge_certifications: List[str]
    difficulty: str
    salary_change: str

# ============== Sector Endpoints ==============

@router.get("/sectors")
async def get_sectors():
    """Get all sectors with their subsectors and roles"""
    return {
        "sectors": list(SECTORS.values()),
        "total_sectors": len(SECTORS)
    }

@router.get("/sectors/{sector_id}")
async def get_sector(sector_id: str):
    """Get a specific sector by ID"""
    if sector_id not in SECTORS:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    sector = SECTORS[sector_id]
    return {
        "sector": sector,
        "certifications": get_certifications_for_sector(sector_id),
        "skills": get_skills_for_sector(sector_id),
        "career_pivots_from": get_career_pivots_from_sector(sector_id),
        "career_pivots_to": get_career_pivots_to_sector(sector_id)
    }

@router.get("/sectors/{sector_id}/roles")
async def get_sector_roles(sector_id: str):
    """Get all roles in a specific sector"""
    if sector_id not in SECTORS:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    roles = []
    sector = SECTORS[sector_id]
    for subsector_id, subsector in sector["subsectors"].items():
        for role in subsector["roles"]:
            roles.append({
                "role": role,
                "subsector_id": subsector_id,
                "subsector_name": subsector["name"]
            })
    
    return {"sector_id": sector_id, "roles": roles, "total": len(roles)}

# ============== Seniority Endpoints ==============

@router.get("/seniority-tiers")
async def get_seniority_tiers():
    """Get all seniority tiers"""
    return {
        "tiers": list(SENIORITY_TIERS.values()),
        "total_tiers": len(SENIORITY_TIERS)
    }

@router.get("/seniority/estimate")
async def estimate_seniority(title: str = Query(..., description="Job title to analyze")):
    """Estimate seniority tier from a job title"""
    tier_id = estimate_seniority_tier(title)
    tier = SENIORITY_TIERS.get(tier_id)
    
    return {
        "title": title,
        "estimated_tier_id": tier_id,
        "tier": tier
    }

# ============== Role Endpoints ==============

@router.get("/roles")
async def get_roles(
    sector: Optional[str] = Query(None, description="Filter by sector ID"),
    search: Optional[str] = Query(None, description="Search roles by name")
):
    """Get all roles, optionally filtered by sector or search term"""
    all_roles = get_all_roles()
    
    if sector:
        all_roles = [r for r in all_roles if r["sector_id"] == sector]
    
    if search:
        search_lower = search.lower()
        all_roles = [r for r in all_roles if search_lower in r["role"].lower()]
    
    return {"roles": all_roles, "total": len(all_roles)}

@router.get("/roles/match")
async def match_role(title: str = Query(..., description="Job title to match")):
    """Try to match a job title to a sector and seniority"""
    sector_id = match_role_to_sector(title)
    tier_id = estimate_seniority_tier(title)
    
    result = {
        "title": title,
        "matched_sector_id": sector_id,
        "matched_sector": SECTORS.get(sector_id) if sector_id else None,
        "estimated_tier_id": tier_id,
        "estimated_tier": SENIORITY_TIERS.get(tier_id)
    }
    
    # Add relevant certifications and skills if sector matched
    if sector_id:
        result["recommended_certifications"] = get_certifications_for_sector(sector_id)[:5]
        result["recommended_skills"] = get_skills_for_sector(sector_id)[:5]
    
    return result

# ============== Certification Endpoints ==============

@router.get("/certifications")
async def get_certifications(
    sector: Optional[str] = Query(None, description="Filter by sector ID"),
    category: Optional[str] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name or code")
):
    """Get all certifications with optional filters"""
    certs = get_all_certifications()
    
    if sector:
        certs = [c for c in certs if sector in c["sector"]]
    
    if category:
        certs = [c for c in certs if c["category_id"] == category]
    
    if search:
        search_lower = search.lower()
        certs = [c for c in certs if search_lower in c["name"].lower() or search_lower in c["code"].lower()]
    
    return {"certifications": certs, "total": len(certs)}

@router.get("/certifications/categories")
async def get_certification_categories():
    """Get all certification categories"""
    categories = [
        {"id": cat_id, "name": cat["category"], "count": len(cat["certs"])}
        for cat_id, cat in CERTIFICATIONS.items()
    ]
    return {"categories": categories}

@router.get("/certifications/{code}")
async def get_certification(code: str):
    """Get a specific certification by code"""
    for category in CERTIFICATIONS.values():
        for cert in category["certs"]:
            if cert["code"].lower() == code.lower():
                return {"certification": cert}
    
    raise HTTPException(status_code=404, detail="Certification not found")

# ============== Skills Endpoints ==============

@router.get("/skills")
async def get_skills(
    sector: Optional[str] = Query(None, description="Filter by sector ID"),
    category: Optional[str] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name")
):
    """Get all skills with optional filters"""
    all_skills = get_all_skills()
    
    if sector:
        all_skills = [s for s in all_skills if sector in s["sector"]]
    
    if category:
        all_skills = [s for s in all_skills if s["category_id"] == category]
    
    if search:
        search_lower = search.lower()
        all_skills = [s for s in all_skills if search_lower in s["name"].lower()]
    
    return {"skills": all_skills, "total": len(all_skills)}

@router.get("/skills/categories")
async def get_skill_categories():
    """Get all skill categories"""
    categories = [
        {"id": cat_id, "name": cat["category"], "count": len(cat["skills"])}
        for cat_id, cat in SKILLS.items()
    ]
    return {"categories": categories}

# ============== Career Pivot Endpoints ==============

@router.get("/career-pivots")
async def get_career_pivots(
    from_sector: Optional[str] = Query(None, description="Filter by source sector"),
    to_sector: Optional[str] = Query(None, description="Filter by target sector"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: low, medium, high")
):
    """Get career pivot pathways with optional filters"""
    pivots = CAREER_PIVOTS.copy()
    
    if from_sector:
        pivots = [p for p in pivots if p["from_sector"] == from_sector]
    
    if to_sector:
        pivots = [p for p in pivots if p["to_sector"] == to_sector]
    
    if difficulty:
        pivots = [p for p in pivots if p["difficulty"] == difficulty]
    
    return {"career_pivots": pivots, "total": len(pivots)}

@router.get("/career-pivots/suggest")
async def suggest_career_pivots(
    current_sector: str = Query(..., description="Current sector ID"),
    current_role: Optional[str] = Query(None, description="Current role title")
):
    """Get suggested career pivots based on current position"""
    # Get pivots from current sector
    pivots = get_career_pivots_from_sector(current_sector)
    
    # If role provided, try to find more specific matches
    if current_role:
        role_lower = current_role.lower()
        exact_matches = [p for p in pivots if p["from_role"].lower() in role_lower or role_lower in p["from_role"].lower()]
        if exact_matches:
            pivots = exact_matches
    
    # Group by target sector
    by_sector = {}
    for pivot in pivots:
        to_sector = pivot["to_sector"]
        if to_sector not in by_sector:
            by_sector[to_sector] = {
                "sector": SECTORS.get(to_sector),
                "pivots": []
            }
        by_sector[to_sector]["pivots"].append(pivot)
    
    return {
        "current_sector": SECTORS.get(current_sector),
        "current_role": current_role,
        "suggestions": list(by_sector.values()),
        "total_opportunities": len(pivots)
    }

# ============== Job Board Endpoints ==============

@router.get("/job-boards")
async def get_job_boards(
    sector: Optional[str] = Query(None, description="Filter by sector ID")
):
    """Get specialized job boards by sector"""
    if sector:
        if sector not in JOB_BOARDS:
            raise HTTPException(status_code=404, detail="Sector not found")
        return {"sector": sector, "job_boards": JOB_BOARDS[sector]}
    
    return {"job_boards": JOB_BOARDS}

# ============== Summary Endpoints ==============

@router.get("/summary")
async def get_taxonomy_summary():
    """Get a summary of the entire taxonomy"""
    total_roles = sum(
        sum(len(sub["roles"]) for sub in sector["subsectors"].values())
        for sector in SECTORS.values()
    )
    
    total_certs = sum(len(cat["certs"]) for cat in CERTIFICATIONS.values())
    total_skills = sum(len(cat["skills"]) for cat in SKILLS.values())
    
    return {
        "summary": {
            "total_sectors": len(SECTORS),
            "total_subsectors": sum(len(s["subsectors"]) for s in SECTORS.values()),
            "total_roles": total_roles,
            "total_certifications": total_certs,
            "total_skills": total_skills,
            "total_career_pivots": len(CAREER_PIVOTS),
            "seniority_tiers": len(SENIORITY_TIERS),
            "job_boards": sum(len(boards) for boards in JOB_BOARDS.values())
        },
        "sectors": [
            {
                "id": s_id,
                "name": s["name"],
                "icon": s["icon"],
                "color": s["color"],
                "subsector_count": len(s["subsectors"]),
                "role_count": sum(len(sub["roles"]) for sub in s["subsectors"].values())
            }
            for s_id, s in SECTORS.items()
        ]
    }

# ============== Profile Enhancement ==============

@router.post("/profile/enhance")
async def enhance_profile(
    skills: List[str] = [],
    certifications: List[str] = [],
    current_role: Optional[str] = None,
    years_experience: Optional[int] = None
):
    """Analyze a profile and suggest sector matches, missing certifications, career pivots"""
    
    # Match skills to sectors
    sector_scores = {s_id: 0 for s_id in SECTORS}
    all_skills_list = get_all_skills()
    
    for skill in skills:
        skill_lower = skill.lower()
        for s in all_skills_list:
            if skill_lower in s["name"].lower():
                for sector_id in s["sector"]:
                    sector_scores[sector_id] += 1
    
    # Determine primary sector
    primary_sector = max(sector_scores.keys(), key=lambda k: sector_scores[k])
    
    # Get recommendations
    recommended_certs = get_certifications_for_sector(primary_sector)
    existing_cert_codes = [c.upper() for c in certifications]
    missing_certs = [c for c in recommended_certs if c["code"] not in existing_cert_codes]
    
    # Estimate seniority
    estimated_tier = "tier_1"
    if years_experience:
        if years_experience >= 15:
            estimated_tier = "tier_5"
        elif years_experience >= 10:
            estimated_tier = "tier_4"
        elif years_experience >= 5:
            estimated_tier = "tier_3"
        elif years_experience >= 2:
            estimated_tier = "tier_2"
    elif current_role:
        estimated_tier = estimate_seniority_tier(current_role)
    
    # Career pivots
    career_options = get_career_pivots_from_sector(primary_sector)
    
    return {
        "analysis": {
            "primary_sector": SECTORS.get(primary_sector),
            "sector_scores": {s_id: score for s_id, score in sector_scores.items() if score > 0},
            "estimated_tier": SENIORITY_TIERS.get(estimated_tier),
            "matched_skills": len(skills),
            "matched_certifications": len([c for c in certifications if c.upper() in existing_cert_codes])
        },
        "recommendations": {
            "missing_certifications": missing_certs[:5],
            "recommended_skills": get_skills_for_sector(primary_sector)[:5],
            "career_pivot_options": career_options[:3]
        }
    }
