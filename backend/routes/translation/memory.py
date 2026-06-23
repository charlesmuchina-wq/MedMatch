# Auto-split route group: memory

from fastapi import APIRouter

from ._common import *  # noqa: F401,F403



router = APIRouter()



@router.post("/memory/store")
async def store_translation_memory(data: Dict[str, Any], request: Request):
    """
    CLDR TMX-compliant Translation Memory storage
    Stores verified translations for consistency and reuse
    """
    source_text = data.get("source_text", "").strip()
    target_text = data.get("target_text", "").strip()
    source_lang = data.get("source_language", "en")
    target_lang = data.get("target_language", "")
    context = data.get("context", "")  # UI context: nav, dashboard, common, etc.
    
    if not source_text or not target_text or not target_lang:
        raise HTTPException(status_code=400, detail="source_text, target_text, and target_language are required")
    
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {target_lang}")
    
    # Create TMX-compliant translation unit (TU)
    tu_id = f"{source_lang}:{target_lang}:{hash(source_text) % 10**8}"
    
    tm_entry = {
        "tu_id": tu_id,
        "source_language": source_lang,
        "target_language": target_lang,
        "source_text": source_text,
        "target_text": target_text,
        "context": context,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "usage_count": 1,
        "verified": False,
        "cldr_locale": target_lang
    }
    
    # Upsert to avoid duplicates
    existing = await db.translation_memory.find_one({"tu_id": tu_id})
    if existing:
        await db.translation_memory.update_one(
            {"tu_id": tu_id},
            {"$set": {"target_text": target_text, "updated_at": datetime.now(timezone.utc).isoformat()}, 
             "$inc": {"usage_count": 1}}
        )
    else:
        await db.translation_memory.insert_one(tm_entry)
    
    return {"message": "Translation stored in memory", "tu_id": tu_id}

@router.get("/memory/lookup")
async def lookup_translation_memory(
    source_text: str,
    target_language: str,
    source_language: str = "en",
    request: Request = None
):
    """
    CLDR TMX-compliant Translation Memory lookup
    Returns exact and fuzzy matches from translation memory
    """
    if not source_text or not target_language:
        raise HTTPException(status_code=400, detail="source_text and target_language are required")
    
    # Exact match
    exact_match = await db.translation_memory.find_one(
        {
            "source_language": source_language,
            "target_language": target_language,
            "source_text": source_text
        },
        {"_id": 0}
    )
    
    if exact_match:
        # Increment usage count
        await db.translation_memory.update_one(
            {"tu_id": exact_match["tu_id"]},
            {"$inc": {"usage_count": 1}}
        )
        return {
            "match_type": "exact",
            "confidence": 100,
            "translation": exact_match["target_text"],
            "tu_id": exact_match["tu_id"],
            "usage_count": exact_match.get("usage_count", 1)
        }
    
    # Fuzzy match (simplified - words overlap)
    words = set(source_text.lower().split())
    if len(words) >= 2:
        # Find similar entries
        similar = await db.translation_memory.find(
            {
                "source_language": source_language,
                "target_language": target_language,
            },
            {"_id": 0}
        ).to_list(100)
        
        best_match = None
        best_score = 0
        
        for entry in similar:
            entry_words = set(entry["source_text"].lower().split())
            overlap = len(words & entry_words)
            total = len(words | entry_words)
            score = (overlap / total * 100) if total > 0 else 0
            
            if score > best_score and score >= 50:  # 50% minimum threshold
                best_score = score
                best_match = entry
        
        if best_match:
            return {
                "match_type": "fuzzy",
                "confidence": round(best_score),
                "translation": best_match["target_text"],
                "tu_id": best_match["tu_id"],
                "source_matched": best_match["source_text"]
            }
    
    return {
        "match_type": "none",
        "confidence": 0,
        "translation": None
    }

@router.get("/memory/stats")
async def get_translation_memory_stats(request: Request):
    """Get Translation Memory statistics"""
    user = await require_auth(request)
    
    # Total entries
    total_entries = await db.translation_memory.count_documents({})
    
    # By language
    lang_pipeline = [
        {"$group": {"_id": "$target_language", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_memory.aggregate(lang_pipeline).to_list(20)
    
    # By context
    context_pipeline = [
        {"$group": {"_id": "$context", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_context = await db.translation_memory.aggregate(context_pipeline).to_list(10)
    
    # Most used translations
    most_used_pipeline = [
        {"$sort": {"usage_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "source_text": 1, "target_language": 1, "usage_count": 1}}
    ]
    most_used = await db.translation_memory.aggregate(most_used_pipeline).to_list(10)
    
    return {
        "total_entries": total_entries,
        "by_language": [
            {"language": item["_id"], "count": item["count"], "info": SUPPORTED_LANGUAGES.get(item["_id"], {})}
            for item in by_language if item["_id"]
        ],
        "by_context": [
            {"context": item["_id"] or "general", "count": item["count"]}
            for item in by_context
        ],
        "most_used": most_used
    }

@router.post("/memory/bulk-store")
async def bulk_store_translation_memory(data: Dict[str, Any], request: Request):
    """
    Bulk store translations in memory (for pre-population)
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    translations = data.get("translations", [])
    target_language = data.get("target_language", "")
    source_language = data.get("source_language", "en")
    context = data.get("context", "ui")
    
    if not translations or not target_language:
        raise HTTPException(status_code=400, detail="translations array and target_language are required")
    
    stored_count = 0
    for item in translations:
        source = item.get("source", "")
        target = item.get("target", "")
        
        if source and target:
            tu_id = f"{source_language}:{target_language}:{hash(source) % 10**8}"
            
            await db.translation_memory.update_one(
                {"tu_id": tu_id},
                {"$set": {
                    "tu_id": tu_id,
                    "source_language": source_language,
                    "target_language": target_language,
                    "source_text": source,
                    "target_text": target,
                    "context": context,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "verified": True,
                    "cldr_locale": target_language
                }},
                upsert=True
            )
            stored_count += 1
    
    return {
        "message": f"Stored {stored_count} translations in memory",
        "target_language": target_language
    }

@router.get("/memory/analytics")
async def get_memory_analytics(request: Request):
    """
    Comprehensive Translation Memory analytics with CLDR metrics
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total entries
    total_entries = await db.translation_memory.count_documents({})
    verified_entries = await db.translation_memory.count_documents({"verified": True})
    
    # Usage statistics
    usage_pipeline = [
        {"$group": {
            "_id": None,
            "total_usage": {"$sum": "$usage_count"},
            "avg_usage": {"$avg": "$usage_count"},
            "max_usage": {"$max": "$usage_count"}
        }}
    ]
    usage_stats = await db.translation_memory.aggregate(usage_pipeline).to_list(1)
    
    # Top used translations
    top_used_pipeline = [
        {"$sort": {"usage_count": -1}},
        {"$limit": 15},
        {"$project": {
            "_id": 0,
            "source_text": 1,
            "target_text": 1,
            "target_language": 1,
            "usage_count": 1,
            "context": 1
        }}
    ]
    top_used = await db.translation_memory.aggregate(top_used_pipeline).to_list(15)
    
    # Coverage by language
    coverage_pipeline = [
        {"$group": {
            "_id": "$target_language",
            "entries": {"$sum": 1},
            "verified": {"$sum": {"$cond": ["$verified", 1, 0]}},
            "total_usage": {"$sum": "$usage_count"}
        }},
        {"$sort": {"entries": -1}},
        {"$limit": 20}
    ]
    by_language = await db.translation_memory.aggregate(coverage_pipeline).to_list(20)
    
    # Context distribution
    context_pipeline = [
        {"$group": {
            "_id": "$context",
            "count": {"$sum": 1},
            "usage": {"$sum": "$usage_count"}
        }},
        {"$sort": {"count": -1}}
    ]
    by_context = await db.translation_memory.aggregate(context_pipeline).to_list(10)
    
    # Recent additions (last 7 days)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_count = await db.translation_memory.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    return {
        "summary": {
            "total_entries": total_entries,
            "verified_entries": verified_entries,
            "verification_rate": round((verified_entries / total_entries * 100) if total_entries > 0 else 0),
            "recent_additions": recent_count
        },
        "usage": {
            "total_lookups": usage_stats[0]["total_usage"] if usage_stats else 0,
            "average_per_entry": round(usage_stats[0]["avg_usage"], 1) if usage_stats else 0,
            "most_used_count": usage_stats[0]["max_usage"] if usage_stats else 0
        },
        "top_translations": top_used,
        "by_language": [
            {
                "language": item["_id"],
                "entries": item["entries"],
                "verified": item["verified"],
                "total_usage": item["total_usage"],
                "info": SUPPORTED_LANGUAGES.get(item["_id"], {})
            }
            for item in by_language if item["_id"]
        ],
        "by_context": [
            {
                "context": item["_id"] or "general",
                "entries": item["count"],
                "usage": item["usage"]
            }
            for item in by_context
        ],
        "cldr_metrics": {
            "tmx_version": "1.4",
            "supported_locales": len(SUPPORTED_LANGUAGES),
            "bundled_locales": 9,  # Updated count
            "rtl_support": True,
            "pluralization": False,  # Future enhancement
            "gender_forms": False   # Future enhancement
        }
    }

@router.get("/memory/export/tmx")
async def export_translation_memory_tmx(
    target_language: Optional[str] = None,
    context: Optional[str] = None,
    request: Request = None
):
    """
    Export Translation Memory in TMX 1.4 format
    Standard format for CAT tools and translation management systems
    Admin only
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query
    query = {}
    if target_language:
        query["target_language"] = target_language
    if context:
        query["context"] = context
    
    # Get translation memory entries
    entries = await db.translation_memory.find(query, {"_id": 0}).to_list(10000)
    
    if not entries:
        raise HTTPException(status_code=404, detail="No translation memory entries found")
    
    # Build TMX XML
    tmx_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header
    creationtool="MedMatch Translation Memory"
    creationtoolversion="1.0"
    datatype="plaintext"
    segtype="sentence"
    adminlang="en"
    srclang="en"
    o-tmf="MedMatch"
    creationdate="{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
  >
    <note>Exported from MedMatch Translation Memory System</note>
  </header>
  <body>
'''
    
    tmx_body = ""
    for entry in entries:
        source_lang = entry.get("source_language", "en")
        target_lang = entry.get("target_language", "")
        source_text = entry.get("source_text", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        target_text = entry.get("target_text", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tu_id = entry.get("tu_id", str(uuid.uuid4()))
        created_at = entry.get("created_at", datetime.now(timezone.utc).isoformat())
        
        # Convert ISO date to TMX format
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            creation_date = dt.strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            creation_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        tmx_body += f'''    <tu tuid="{tu_id}" creationdate="{creation_date}">
      <prop type="context">{entry.get("context", "general")}</prop>
      <prop type="usage_count">{entry.get("usage_count", 0)}</prop>
      <prop type="verified">{str(entry.get("verified", False)).lower()}</prop>
      <tuv xml:lang="{source_lang}">
        <seg>{source_text}</seg>
      </tuv>
      <tuv xml:lang="{target_lang}">
        <seg>{target_text}</seg>
      </tuv>
    </tu>
'''
    
    tmx_footer = '''  </body>
</tmx>
'''
    
    tmx_content = tmx_header + tmx_body + tmx_footer
    
    filename = f"medmatch_tm_{target_language or 'all'}_{datetime.now().strftime('%Y%m%d')}.tmx"
    
    from fastapi.responses import Response
    return Response(
        content=tmx_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/memory/export/json")
async def export_translation_memory_json(
    target_language: Optional[str] = None,
    context: Optional[str] = None,
    request: Request = None
):
    """
    Export Translation Memory in JSON format
    Useful for custom integrations and backups
    Admin only
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query
    query = {}
    if target_language:
        query["target_language"] = target_language
    if context:
        query["context"] = context
    
    # Get translation memory entries
    entries = await db.translation_memory.find(query, {"_id": 0}).to_list(10000)
    
    export_data = {
        "format": "MedMatch Translation Memory Export",
        "version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "filters": {
            "target_language": target_language,
            "context": context
        },
        "statistics": {
            "total_entries": len(entries),
            "languages": list(set(e.get("target_language") for e in entries if e.get("target_language"))),
            "contexts": list(set(e.get("context") for e in entries if e.get("context")))
        },
        "entries": entries
    }
    
    return export_data

@router.get("/memory/export/xliff")
async def export_translation_memory_xliff(
    target_language: str,
    context: Optional[str] = None,
    request: Request = None
):
    """
    Export Translation Memory in XLIFF 2.0 format
    Standard format for localization workflows
    Admin only
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not target_language:
        raise HTTPException(status_code=400, detail="target_language is required for XLIFF export")
    
    # Build query
    query = {"target_language": target_language}
    if context:
        query["context"] = context
    
    # Get translation memory entries
    entries = await db.translation_memory.find(query, {"_id": 0}).to_list(10000)
    
    if not entries:
        raise HTTPException(status_code=404, detail="No translation memory entries found")
    
    # Build XLIFF 2.0 XML
    xliff_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<xliff version="2.0" xmlns="urn:oasis:names:tc:xliff:document:2.0" srcLang="en" trgLang="{target_language}">
  <file id="medmatch-tm" original="MedMatch Translation Memory">
'''
    
    xliff_body = ""
    for idx, entry in enumerate(entries):
        source_text = entry.get("source_text", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        target_text = entry.get("target_text", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tu_id = entry.get("tu_id", f"tu-{idx}")
        
        xliff_body += f'''    <unit id="{tu_id}">
      <notes>
        <note category="context">{entry.get("context", "general")}</note>
        <note category="usage_count">{entry.get("usage_count", 0)}</note>
      </notes>
      <segment state="translated">
        <source>{source_text}</source>
        <target>{target_text}</target>
      </segment>
    </unit>
'''
    
    xliff_footer = '''  </file>
</xliff>
'''
    
    xliff_content = xliff_header + xliff_body + xliff_footer
    
    filename = f"medmatch_tm_{target_language}_{datetime.now().strftime('%Y%m%d')}.xliff"
    
    from fastapi.responses import Response
    return Response(
        content=xliff_content,
        media_type="application/xliff+xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.post("/memory/import/tmx")
async def import_translation_memory_tmx(data: TMXImportRequest, request: Request):
    """
    Import Translation Memory from TMX format
    Admin only
    """
    user = await require_auth(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    import re
    
    # Parse TMX content (simple regex parsing for reliability)
    tu_pattern = r'<tu[^>]*tuid="([^"]*)"[^>]*>(.*?)</tu>'
    tuv_pattern = r'<tuv[^>]*xml:lang="([^"]*)"[^>]*>\s*<seg>(.*?)</seg>\s*</tuv>'
    
    imported = 0
    errors = []
    
    tus = re.findall(tu_pattern, data.tmx_content, re.DOTALL)
    
    for tu_id, tu_content in tus:
        try:
            tuvs = re.findall(tuv_pattern, tu_content, re.DOTALL)
            
            if len(tuvs) >= 2:
                source_lang, source_text = tuvs[0]
                target_lang, target_text = tuvs[1]
                
                # Unescape XML entities
                source_text = source_text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                target_text = target_text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                
                # Check existing
                existing = await db.translation_memory.find_one({"tu_id": tu_id})
                
                if existing and not data.overwrite_existing:
                    continue
                
                tm_entry = {
                    "tu_id": tu_id,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "source_text": source_text.strip(),
                    "target_text": target_text.strip(),
                    "context": "imported",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "usage_count": 0,
                    "verified": False,
                    "cldr_locale": target_lang,
                    "imported_from": "tmx"
                }
                
                if existing:
                    await db.translation_memory.update_one(
                        {"tu_id": tu_id},
                        {"$set": tm_entry}
                    )
                else:
                    await db.translation_memory.insert_one(tm_entry)
                
                imported += 1
                
        except Exception as e:
            errors.append({"tu_id": tu_id, "error": str(e)})
    
    return {
        "message": f"TMX import completed: {imported} entries processed",
        "imported": imported,
        "errors": errors[:20],  # Limit error list
        "total_found": len(tus)
    }
