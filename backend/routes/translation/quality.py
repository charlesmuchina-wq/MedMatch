# Auto-split route group: quality

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



@router.post("/quality/score")
async def score_translation_quality(data: Dict[str, Any], request: Request):
    """
    Score the quality of a translation
    """
    source_text = data.get("source_text", "")
    target_text = data.get("target_text", "")
    target_language = data.get("target_language", "")
    
    if not source_text or not target_text or not target_language:
        raise HTTPException(status_code=400, detail="source_text, target_text, and target_language are required")
    
    score = TranslationQualityScorer.calculate_score(source_text, target_text, target_language)
    
    # Store quality score in DB for analytics
    await db.translation_quality.insert_one({
        "source_text": source_text[:100],
        "target_text": target_text[:100],
        "target_language": target_language,
        "scores": score,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "source_text": source_text,
        "target_text": target_text,
        "target_language": target_language,
        "quality": score
    }

@router.post("/quality/batch-score")
async def batch_score_translations(data: Dict[str, Any], request: Request):
    """
    Score quality of multiple translations at once
    """
    translations = data.get("translations", [])
    target_language = data.get("target_language", "")
    
    if not translations or not target_language:
        raise HTTPException(status_code=400, detail="translations array and target_language are required")
    
    results = []
    total_score = 0
    
    for item in translations:
        source = item.get("source", "")
        target = item.get("target", "")
        
        if source and target:
            score = TranslationQualityScorer.calculate_score(source, target, target_language)
            total_score += score["overall_score"]
            results.append({
                "source": source[:50],
                "target": target[:50],
                "quality": score
            })
    
    avg_score = total_score / len(results) if results else 0
    
    return {
        "target_language": target_language,
        "translations_scored": len(results),
        "average_score": round(avg_score),
        "quality_level": "excellent" if avg_score >= 90 else "good" if avg_score >= 70 else "fair" if avg_score >= 50 else "poor",
        "results": results[:20]  # Limit response size
    }

@router.get("/quality/stats")
async def get_quality_stats(request: Request):
    """
    Get translation quality statistics
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Overall quality by language
    quality_pipeline = [
        {"$group": {
            "_id": "$target_language",
            "avg_score": {"$avg": "$scores.overall_score"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_quality.aggregate(quality_pipeline).to_list(20)
    
    # Quality distribution
    distribution_pipeline = [
        {"$bucket": {
            "groupBy": "$scores.overall_score",
            "boundaries": [0, 50, 70, 90, 101],
            "default": "unknown",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    distribution = await db.translation_quality.aggregate(distribution_pipeline).to_list(10)
    
    # Total scored
    total_scored = await db.translation_quality.count_documents({})
    
    return {
        "total_scored": total_scored,
        "by_language": [
            {
                "language": item["_id"],
                "average_score": round(item["avg_score"]) if item["avg_score"] else 0,
                "count": item["count"],
                "quality_level": "excellent" if item["avg_score"] and item["avg_score"] >= 90 else "good" if item["avg_score"] and item["avg_score"] >= 70 else "fair"
            }
            for item in by_language if item["_id"]
        ],
        "quality_distribution": [
            {
                "range": f"{dist['_id']}-{dist['_id']+20 if dist['_id'] < 90 else 100}" if isinstance(dist['_id'], int) else "unknown",
                "count": dist["count"],
                "level": "poor" if dist['_id'] == 0 else "fair" if dist['_id'] == 50 else "good" if dist['_id'] == 70 else "excellent"
            }
            for dist in distribution if isinstance(dist.get('_id'), int)
        ]
    }
