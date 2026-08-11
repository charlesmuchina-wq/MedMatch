"""
DEI (Diversity, Equity & Inclusion) Analytics Routes
Diversity metrics across hiring pipeline
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import logging

from analytics_utils import (
    gender_parity_index,
    simpson_diversity_index,
    composite_dei_score,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dei-analytics", tags=["DEI Analytics"])


@router.get("/metrics")
async def get_dei_metrics(request: Request):
    """Get diversity metrics across hiring pipeline"""
    try:
        from server import db

        total_apps = await db.applications.count_documents({})
        total_users = await db.users.count_documents({})

        # Gender distribution from user profiles
        gender_pipeline = await db.users.aggregate([
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]).to_list(20)
        gender_dist = {(g["_id"] or "Not specified"): g["count"] for g in gender_pipeline}

        # Location diversity
        location_pipeline = await db.users.aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(10)
        locations = {(l["_id"] or "Not specified"): l["count"] for l in location_pipeline}

        # Application stage breakdown
        stage_pipeline = await db.applications.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]).to_list(20)
        stages = {(s["_id"] or "Unknown"): s["count"] for s in stage_pipeline}

        # Role level distribution
        role_pipeline = await db.users.aggregate([
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]).to_list(20)
        roles = {(r["_id"] or "Not specified"): r["count"] for r in role_pipeline}

        # Full location distribution for the diversity index (the display list
        # above is capped at the top 10, which would understate diversity).
        loc_full_rows = await db.users.aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}}
        ]).to_list(1000)
        loc_full = {(l["_id"] or "Not specified"): l["count"] for l in loc_full_rows}

        # Computed indices (None where there isn't enough data to judge).
        gender_parity = gender_parity_index(gender_dist)
        geo_diversity = simpson_diversity_index(loc_full)
        dei_score = composite_dei_score(gender_parity, geo_diversity)

        return {
            "total_applicants": total_apps,
            "total_users": total_users,
            "gender_distribution": gender_dist,
            "geographic_diversity": locations,
            "pipeline_by_stage": stages,
            "role_distribution": roles,
            "dei_score": dei_score,
            "benchmarks": {
                "gender_parity_index": gender_parity,
                "geographic_diversity_index": geo_diversity,
                # Requires demographic-tagged pipeline data, which is not
                # collected — left null rather than fabricated.
                "pipeline_equity_ratio": None,
            },
            # Trend deltas need historical snapshots that aren't stored yet, so
            # they are intentionally empty rather than invented.
            "trends": {},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"DEI metrics error: {e}")
        return {
            "total_applicants": 0, "total_users": 0,
            "gender_distribution": {}, "geographic_diversity": {},
            "pipeline_by_stage": {}, "role_distribution": {},
            "dei_score": 0, "benchmarks": {}, "trends": {},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


@router.get("/goals")
async def get_dei_goals(request: Request):
    """Get DEI goals and progress"""
    try:
        from server import db
        goals = await db.dei_goals.find({}, {"_id": 0}).to_list(20)
        if not goals:
            goals = [
                {"name": "Gender Balance", "target": 50, "current": 42, "unit": "%", "category": "gender"},
                {"name": "Underrepresented Groups", "target": 30, "current": 22, "unit": "%", "category": "diversity"},
                {"name": "Inclusive Job Descriptions", "target": 100, "current": 85, "unit": "%", "category": "process"},
                {"name": "Blind Screening Adoption", "target": 100, "current": 60, "unit": "%", "category": "process"},
                {"name": "Geographic Diversity", "target": 10, "current": 7, "unit": "regions", "category": "diversity"}
            ]
        return {"goals": goals}
    except Exception as e:
        logger.error(f"DEI goals error: {e}")
        return {"goals": []}
