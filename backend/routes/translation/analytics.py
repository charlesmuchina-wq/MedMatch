# Auto-split route group: analytics

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



@router.get("/analytics")
async def get_translation_analytics(request: Request):
    """Get translation usage analytics (admin only)"""
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Most used target languages
    pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    lang_stats = await db.translation_logs.aggregate(pipeline).to_list(10)
    
    # Total translations
    total = await db.translation_logs.count_documents({})
    
    # Total characters
    char_pipeline = [
        {"$group": {"_id": None, "total_chars": {"$sum": "$character_count"}}}
    ]
    char_result = await db.translation_logs.aggregate(char_pipeline).to_list(1)
    total_chars = char_result[0]["total_chars"] if char_result else 0
    
    return {
        "total_translations": total,
        "total_characters": total_chars,
        "top_languages": [
            {"language": item["_id"], "count": item["count"], "info": SUPPORTED_LANGUAGES.get(item["_id"], {})}
            for item in lang_stats if item["_id"]
        ]
    }

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(request: Request):
    """
    Comprehensive translation analytics dashboard
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Translation logs stats
    total_translations = await db.translation_logs.count_documents({})
    
    # Character count
    char_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$character_count"}}}
    ]
    char_result = await db.translation_logs.aggregate(char_pipeline).to_list(1)
    total_characters = char_result[0]["total"] if char_result else 0
    
    # Top languages
    lang_pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}, "chars": {"$sum": "$character_count"}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    top_languages = await db.translation_logs.aggregate(lang_pipeline).to_list(15)
    
    # Pre-render cache stats
    cache_count = await db.translation_cache.count_documents({})
    
    # Translation Memory stats
    tm_count = await db.translation_memory.count_documents({})
    
    # Daily usage (last 7 days)
    from datetime import timedelta
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    daily_pipeline = [
        {"$match": {"timestamp": {"$gte": seven_days_ago}}},
        {"$group": {
            "_id": {"$substr": ["$timestamp", 0, 10]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_usage = await db.translation_logs.aggregate(daily_pipeline).to_list(7)
    
    return {
        "summary": {
            "total_translations": total_translations,
            "total_characters": total_characters,
            "cache_entries": cache_count,
            "memory_entries": tm_count
        },
        "top_languages": [
            {
                "language": item["_id"],
                "translations": item["count"],
                "characters": item.get("chars", 0),
                "info": SUPPORTED_LANGUAGES.get(item["_id"], {})
            }
            for item in top_languages if item["_id"]
        ],
        "daily_usage": [
            {"date": item["_id"], "count": item["count"]}
            for item in daily_usage
        ],
        "cldr_compliance": {
            "tmx_enabled": True,
            "locale_support": len(SUPPORTED_LANGUAGES),
            "rtl_languages": ["ar", "he", "fa", "ur"],
            "bundled_languages": [
                # Core languages
                "en", "es", "fr", "de", "zh",
                # High demand languages
                "ja", "ar", "hi", "pt-BR",
                # All 16 African languages
                "sw", "ha", "yo", "ig", "zu", "xh", "af", "am", "om", "so", "rw", "sn", "ny", "tw", "wo", "lg"
            ]
        }
    }
