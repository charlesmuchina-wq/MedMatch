"""
Translation QA API Routes
Part of Karau Automator
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import asyncio

from services.translation_qa import translation_qa_service, TranslationQAService


router = APIRouter(prefix="/translation-qa", tags=["Translation QA"])


# In-memory storage for QA results (in production, use database)
qa_history = []
scheduled_qa_enabled = False
last_scheduled_run = None


class QARunResponse(BaseModel):
    run_id: str
    status: str
    timestamp: str
    summary: Dict[str, Any]
    duration_ms: Optional[int] = None


class QADetailResponse(BaseModel):
    run_id: str
    timestamp: str
    status: str
    summary: Dict[str, Any]
    languages: Dict[str, Any]
    critical_issues: List[Dict]
    warnings: List[Dict]
    recommendations: List[Dict]
    duration_ms: Optional[int] = None


class ScheduleConfig(BaseModel):
    enabled: bool
    interval_hours: int = 24


@router.post("/run", response_model=QARunResponse)
async def run_translation_qa():
    """
    Run complete translation QA suite
    
    Performs:
    - JSON syntax validation
    - Missing key detection
    - Placeholder validation
    - Text expansion analysis
    - UI length checks
    - RTL language validation
    """
    try:
        # Run QA
        results = translation_qa_service.run_full_qa()
        
        # Store in history
        qa_history.insert(0, results)
        if len(qa_history) > 50:
            qa_history.pop()
        
        return QARunResponse(
            run_id=results["run_id"],
            status=results["status"],
            timestamp=results["timestamp"],
            summary=results["summary"],
            duration_ms=results.get("duration_ms")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=QADetailResponse)
async def get_latest_qa_results():
    """Get the most recent QA run results"""
    if not qa_history:
        # Run QA if no history exists
        results = translation_qa_service.run_full_qa()
        qa_history.insert(0, results)
    
    latest = qa_history[0]
    return QADetailResponse(**latest)


@router.get("/history")
async def get_qa_history(limit: int = 10):
    """Get QA run history"""
    return {
        "total": len(qa_history),
        "runs": qa_history[:limit]
    }


@router.get("/run/{run_id}", response_model=QADetailResponse)
async def get_qa_run(run_id: str):
    """Get specific QA run by ID"""
    for run in qa_history:
        if run["run_id"] == run_id:
            return QADetailResponse(**run)
    raise HTTPException(status_code=404, detail="QA run not found")


@router.get("/missing-keys")
async def get_missing_keys():
    """Get detailed report of missing translation keys per language"""
    report = translation_qa_service.get_missing_keys_report()
    
    # Calculate totals
    total_missing = sum(len(keys) for keys in report.values())
    languages_affected = len(report)
    
    return {
        "total_missing_keys": total_missing,
        "languages_affected": languages_affected,
        "by_language": report
    }


@router.get("/expansion-issues")
async def get_expansion_issues():
    """Get detailed report of text expansion issues"""
    report = translation_qa_service.get_expansion_report()
    
    total_issues = sum(len(issues) for issues in report.values())
    
    return {
        "total_issues": total_issues,
        "by_language": report
    }


@router.get("/language/{lang_code}")
async def get_language_qa(lang_code: str):
    """Get QA results for a specific language"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    if lang_code not in results.get("languages", {}):
        raise HTTPException(status_code=404, detail=f"Language '{lang_code}' not found")
    
    return {
        "language_code": lang_code,
        "results": results["languages"][lang_code],
        "master_key_count": results["summary"]["total_keys"]
    }


@router.post("/pseudo-localize")
async def generate_pseudo_localization():
    """
    Generate pseudo-localized strings for testing
    
    Converts English text to accented characters to help identify
    hard-coded strings that aren't being translated
    """
    pseudo_keys = translation_qa_service.generate_pseudo_localization()
    
    return {
        "total_keys": len(pseudo_keys),
        "sample": dict(list(pseudo_keys.items())[:10]),
        "description": "Use these pseudo-localized strings to test for hard-coded text"
    }


@router.get("/score")
async def get_translation_score():
    """Get overall translation quality score"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    
    # Calculate per-language scores
    language_scores = {}
    for lang_code, lang_data in results.get("languages", {}).items():
        language_scores[lang_code] = {
            "score": lang_data["score"],
            "missing_keys": lang_data["missing_keys_count"],
            "placeholder_errors": len(lang_data["placeholder_errors"]),
            "status": "healthy" if lang_data["score"] >= 90 else 
                     "warning" if lang_data["score"] >= 70 else "critical"
        }
    
    return {
        "overall_score": results["summary"]["overall_score"],
        "total_languages": results["summary"]["total_languages"],
        "total_keys": results["summary"]["total_keys"],
        "language_scores": language_scores,
        "last_run": results["timestamp"]
    }


@router.get("/recommendations")
async def get_recommendations():
    """Get prioritized recommendations for improving translations"""
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    
    return {
        "recommendations": results.get("recommendations", []),
        "critical_issues_count": len(results.get("critical_issues", [])),
        "overall_score": results["summary"]["overall_score"]
    }


@router.post("/schedule")
async def configure_scheduled_qa(config: ScheduleConfig):
    """Configure scheduled QA runs (for Karau Automator integration)"""
    global scheduled_qa_enabled
    scheduled_qa_enabled = config.enabled
    
    return {
        "scheduled_qa_enabled": scheduled_qa_enabled,
        "interval_hours": config.interval_hours,
        "message": f"Scheduled QA {'enabled' if config.enabled else 'disabled'}"
    }


@router.get("/schedule/status")
async def get_schedule_status():
    """Get current scheduled QA status"""
    return {
        "enabled": scheduled_qa_enabled,
        "last_run": last_scheduled_run,
        "next_run": None  # Would be calculated based on schedule
    }


# Karau Automator Integration
@router.post("/automator/trigger")
async def trigger_from_automator(background_tasks: BackgroundTasks):
    """
    Endpoint for Karau Automator to trigger QA runs
    
    Called by the automator on schedule to run translation QA
    and store results for the dashboard
    """
    global last_scheduled_run
    
    async def run_qa_background():
        global last_scheduled_run
        results = translation_qa_service.run_full_qa()
        qa_history.insert(0, results)
        if len(qa_history) > 50:
            qa_history.pop()
        last_scheduled_run = datetime.now(timezone.utc).isoformat()
    
    background_tasks.add_task(run_qa_background)
    
    return {
        "status": "triggered",
        "message": "Translation QA run started in background"
    }


@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """
    Get summary data for the QA dashboard widget
    
    Returns condensed data suitable for dashboard display
    """
    if not translation_qa_service.qa_results:
        translation_qa_service.run_full_qa()
    
    results = translation_qa_service.qa_results
    summary = results["summary"]
    
    # Determine health status
    score = summary["overall_score"]
    if score >= 90:
        health = "excellent"
        health_color = "green"
    elif score >= 75:
        health = "good"
        health_color = "blue"
    elif score >= 50:
        health = "needs_attention"
        health_color = "yellow"
    else:
        health = "critical"
        health_color = "red"
    
    # Count languages by status
    status_counts = {"healthy": 0, "warning": 0, "critical": 0}
    for lang_data in results.get("languages", {}).values():
        if lang_data["score"] >= 90:
            status_counts["healthy"] += 1
        elif lang_data["score"] >= 70:
            status_counts["warning"] += 1
        else:
            status_counts["critical"] += 1
    
    return {
        "overall_score": score,
        "health": health,
        "health_color": health_color,
        "total_languages": summary["total_languages"],
        "total_keys": summary["total_keys"],
        "issues": {
            "critical": len(results.get("critical_issues", [])),
            "missing_keys": summary["missing_keys"],
            "placeholder_errors": summary["placeholder_errors"],
            "expansion_warnings": summary["expansion_warnings"]
        },
        "language_status": status_counts,
        "last_run": results["timestamp"],
        "top_recommendations": results.get("recommendations", [])[:3]
    }


# =============================================================================
# BENCHMARKING & AUTO-TRANSLATION ENDPOINTS
# =============================================================================

# Language Tiers for KPI targeting
LANGUAGE_TIERS = {
    "tier1": {
        "name": "Tier 1 - Must Have",
        "target_kpi": 98,
        "languages": ["en", "es", "fr", "de", "ja", "zh", "ar", "pt-BR"],
        "description": "Critical languages with highest user base"
    },
    "tier2": {
        "name": "Tier 2 - High Value",
        "target_kpi": 95,
        "languages": ["ko", "hi", "it", "nl", "ru", "tr", "vi", "pl", "sv"],
        "description": "High-growth market languages"
    },
    "tier3": {
        "name": "Tier 3 - Growth Markets (African)",
        "target_kpi": 90,
        "languages": ["sw", "ha", "yo", "ig", "zu", "xh", "af", "am", "om", "so", "rw", "sn", "ny", "tw", "wo", "lg"],
        "description": "African languages for emerging markets"
    }
}

# In-memory storage for auto-translation jobs
auto_translation_jobs = {}


class AutoTranslateRequest(BaseModel):
    target_kpi: float = 95.0
    tiers: Optional[List[str]] = None  # None = all tiers
    dry_run: bool = False


class BenchmarkAlert(BaseModel):
    threshold: float = 90.0
    enabled: bool = True


# Alert configuration storage
alert_config = {
    "threshold": 90.0,
    "enabled": True,
    "last_alert": None,
    "alerts_triggered": []
}


@router.get("/benchmark")
async def get_translation_benchmark():
    """
    Get comprehensive translation benchmarking metrics
    
    Returns:
    - Overall KPI status
    - Per-tier coverage metrics
    - Per-language coverage with grades
    - Industry comparison
    """
    import json
    import os
    
    locales_dir = "/app/frontend/src/locales"
    
    # Load English as master
    with open(f"{locales_dir}/en.json", 'r', encoding='utf-8') as f:
        english = json.load(f)
    
    def flatten_keys(obj, prefix=""):
        keys = {}
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(flatten_keys(v, full_key))
            else:
                keys[full_key] = v
        return keys
    
    english_flat = flatten_keys(english)
    total_keys = len(english_flat)
    
    # Calculate per-language metrics
    language_metrics = {}
    tier_metrics = {}
    
    # Initialize tier metrics
    for tier_id, tier_data in LANGUAGE_TIERS.items():
        tier_metrics[tier_id] = {
            "name": tier_data["name"],
            "target_kpi": tier_data["target_kpi"],
            "languages": [],
            "total_coverage": 0,
            "languages_meeting_kpi": 0,
            "status": "unknown"
        }
    
    # Get all locale files
    locale_files = [f.replace('.json', '') for f in os.listdir(locales_dir) 
                    if f.endswith('.json') and f not in ['en.json', 'pseudo.json']]
    
    for lang_code in locale_files:
        try:
            with open(f"{locales_dir}/{lang_code}.json", 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_flat = flatten_keys(locale_data)
            
            # Count translated (non-identical to English)
            translated = 0
            for key, en_value in english_flat.items():
                locale_value = locale_flat.get(key)
                if locale_value and locale_value != en_value:
                    translated += 1
            
            coverage = (translated / total_keys) * 100 if total_keys > 0 else 0
            
            # Determine grade
            if coverage >= 98:
                grade = "A+"
            elif coverage >= 95:
                grade = "A"
            elif coverage >= 90:
                grade = "B+"
            elif coverage >= 85:
                grade = "B"
            elif coverage >= 80:
                grade = "C"
            elif coverage >= 70:
                grade = "D"
            else:
                grade = "F"
            
            # Find tier
            lang_tier = None
            for tier_id, tier_data in LANGUAGE_TIERS.items():
                if lang_code in tier_data["languages"]:
                    lang_tier = tier_id
                    break
            
            language_metrics[lang_code] = {
                "translated": translated,
                "total": total_keys,
                "coverage": round(coverage, 1),
                "grade": grade,
                "tier": lang_tier,
                "meets_kpi": coverage >= (LANGUAGE_TIERS.get(lang_tier, {}).get("target_kpi", 95) if lang_tier else 95)
            }
            
            # Update tier metrics
            if lang_tier:
                tier_metrics[lang_tier]["languages"].append({
                    "code": lang_code,
                    "coverage": round(coverage, 1),
                    "grade": grade
                })
                tier_metrics[lang_tier]["total_coverage"] += coverage
                if language_metrics[lang_code]["meets_kpi"]:
                    tier_metrics[lang_tier]["languages_meeting_kpi"] += 1
                    
        except Exception as e:
            language_metrics[lang_code] = {
                "error": str(e),
                "coverage": 0,
                "grade": "F"
            }
    
    # Calculate tier averages and status
    for tier_id, tier_data in tier_metrics.items():
        lang_count = len(tier_data["languages"])
        if lang_count > 0:
            avg_coverage = tier_data["total_coverage"] / lang_count
            tier_data["average_coverage"] = round(avg_coverage, 1)
            tier_data["kpi_achievement"] = round((tier_data["languages_meeting_kpi"] / lang_count) * 100, 1)
            
            if avg_coverage >= tier_data["target_kpi"]:
                tier_data["status"] = "excellent"
            elif avg_coverage >= tier_data["target_kpi"] - 5:
                tier_data["status"] = "good"
            elif avg_coverage >= tier_data["target_kpi"] - 10:
                tier_data["status"] = "needs_improvement"
            else:
                tier_data["status"] = "critical"
    
    # Overall metrics
    all_coverages = [m["coverage"] for m in language_metrics.values() if "coverage" in m]
    overall_avg = sum(all_coverages) / len(all_coverages) if all_coverages else 0
    languages_at_95 = sum(1 for c in all_coverages if c >= 95)
    languages_at_90 = sum(1 for c in all_coverages if c >= 90)
    
    # Industry benchmark comparison
    industry_benchmarks = {
        "duolingo": {"languages": 40, "avg_coverage": 98},
        "airbnb": {"languages": 62, "avg_coverage": 95},
        "uber": {"languages": 40, "avg_coverage": 92},
        "whatsapp": {"languages": 60, "avg_coverage": 96}
    }
    
    # Check alerts
    alerts = []
    if alert_config["enabled"]:
        for lang_code, metrics in language_metrics.items():
            if metrics.get("coverage", 0) < alert_config["threshold"]:
                alerts.append({
                    "language": lang_code,
                    "coverage": metrics.get("coverage", 0),
                    "threshold": alert_config["threshold"],
                    "severity": "critical" if metrics.get("coverage", 0) < 70 else "warning"
                })
    
    return {
        "summary": {
            "total_ui_keys": total_keys,
            "total_languages": len(locale_files),
            "overall_average_coverage": round(overall_avg, 1),
            "languages_at_95_percent": languages_at_95,
            "languages_at_90_percent": languages_at_90,
            "overall_grade": "A" if overall_avg >= 95 else "B+" if overall_avg >= 90 else "B" if overall_avg >= 85 else "C" if overall_avg >= 80 else "D"
        },
        "tiers": tier_metrics,
        "languages": language_metrics,
        "industry_comparison": industry_benchmarks,
        "alerts": alerts,
        "alert_config": alert_config,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/benchmark/alerts")
async def configure_benchmark_alerts(config: BenchmarkAlert):
    """Configure translation coverage alerts"""
    global alert_config
    alert_config["threshold"] = config.threshold
    alert_config["enabled"] = config.enabled
    
    return {
        "status": "configured",
        "threshold": config.threshold,
        "enabled": config.enabled,
        "message": f"Alerts {'enabled' if config.enabled else 'disabled'} at {config.threshold}% threshold"
    }


@router.get("/benchmark/alerts")
async def get_benchmark_alerts():
    """Get current alert configuration and triggered alerts"""
    # Get current benchmark to check for alerts
    benchmark = await get_translation_benchmark()
    
    return {
        "config": alert_config,
        "current_alerts": benchmark["alerts"],
        "alert_count": len(benchmark["alerts"])
    }


@router.post("/auto-translate")
async def trigger_auto_translation(request: AutoTranslateRequest, background_tasks: BackgroundTasks):
    """
    Trigger automated AI translation to meet KPI targets
    
    - target_kpi: Target coverage percentage (default 95%)
    - tiers: List of tiers to process (default: all)
    - dry_run: If true, only calculate what would be translated
    """
    import uuid
    
    job_id = str(uuid.uuid4())[:8]
    
    # Get current benchmark
    benchmark = await get_translation_benchmark()
    
    # Identify languages needing translation
    languages_to_translate = []
    target_tiers = request.tiers or list(LANGUAGE_TIERS.keys())
    
    for lang_code, metrics in benchmark["languages"].items():
        if metrics.get("coverage", 0) < request.target_kpi:
            # Check if in target tiers
            lang_tier = metrics.get("tier")
            if lang_tier in target_tiers or not lang_tier:
                keys_needed = int((request.target_kpi - metrics.get("coverage", 0)) / 100 * benchmark["summary"]["total_ui_keys"])
                languages_to_translate.append({
                    "code": lang_code,
                    "current_coverage": metrics.get("coverage", 0),
                    "target_coverage": request.target_kpi,
                    "keys_to_translate": max(keys_needed, 0),
                    "tier": lang_tier
                })
    
    # Sort by tier priority and coverage gap
    tier_order = {"tier1": 0, "tier2": 1, "tier3": 2, None: 3}
    languages_to_translate.sort(key=lambda x: (tier_order.get(x["tier"], 3), -x["keys_to_translate"]))
    
    total_keys = sum(l["keys_to_translate"] for l in languages_to_translate)
    
    if request.dry_run:
        return {
            "job_id": job_id,
            "status": "dry_run",
            "languages_to_translate": len(languages_to_translate),
            "total_keys_to_translate": total_keys,
            "estimated_time_minutes": max(1, total_keys // 50),
            "languages": languages_to_translate,
            "target_kpi": request.target_kpi
        }
    
    # Store job info
    auto_translation_jobs[job_id] = {
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "target_kpi": request.target_kpi,
        "languages_total": len(languages_to_translate),
        "languages_completed": 0,
        "keys_translated": 0,
        "errors": [],
        "progress": []
    }
    
    # Run translation in background
    async def run_auto_translation():
        import json
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.config import EMERGENT_LLM_KEY
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        locales_dir = "/app/frontend/src/locales"
        
        # Load English master
        with open(f"{locales_dir}/en.json", 'r', encoding='utf-8') as f:
            english = json.load(f)
        
        def flatten_keys(obj, prefix=""):
            keys = {}
            for k, v in obj.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    keys.update(flatten_keys(v, full_key))
                else:
                    keys[full_key] = v
            return keys
        
        def unflatten_keys(flat_dict):
            result = {}
            for key, value in flat_dict.items():
                parts = key.split('.')
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            return result
        
        english_flat = flatten_keys(english)
        
        # Language names for translation
        lang_names = {
            "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
            "zh": "Chinese", "ko": "Korean", "ar": "Arabic", "pt-BR": "Portuguese",
            "hi": "Hindi", "it": "Italian", "nl": "Dutch", "ru": "Russian",
            "pl": "Polish", "sv": "Swedish", "tr": "Turkish", "vi": "Vietnamese",
            "sw": "Swahili", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
            "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "am": "Amharic",
            "om": "Oromo", "so": "Somali", "rw": "Kinyarwanda", "sn": "Shona",
            "ny": "Chichewa", "tw": "Twi", "wo": "Wolof", "lg": "Luganda"
        }
        
        for lang_info in languages_to_translate:
            lang_code = lang_info["code"]
            try:
                # Load locale
                locale_path = f"{locales_dir}/{lang_code}.json"
                with open(locale_path, 'r', encoding='utf-8') as f:
                    locale_data = json.load(f)
                locale_flat = flatten_keys(locale_data)
                
                # Find keys needing translation
                keys_to_translate = []
                for key, en_value in english_flat.items():
                    locale_value = locale_flat.get(key)
                    if not locale_value or locale_value == en_value:
                        keys_to_translate.append((key, en_value))
                
                # Limit to what's needed for KPI
                keys_to_translate = keys_to_translate[:lang_info["keys_to_translate"] + 20]
                
                if not keys_to_translate:
                    auto_translation_jobs[job_id]["languages_completed"] += 1
                    auto_translation_jobs[job_id]["progress"].append({
                        "language": lang_code,
                        "status": "skipped",
                        "reason": "no keys needed"
                    })
                    continue
                
                # Translate in batches
                lang_name = lang_names.get(lang_code, lang_code)
                batch_size = 20
                translated_count = 0
                
                for i in range(0, len(keys_to_translate), batch_size):
                    batch = keys_to_translate[i:i+batch_size]
                    texts = [item[1] for item in batch]
                    keys = [item[0] for item in batch]
                    
                    try:
                        chat = LlmChat(
                            api_key=EMERGENT_LLM_KEY,
                            session_id=f"auto-translate-{job_id}-{lang_code}",
                            system_message=f"Translate UI strings to {lang_name}. Keep concise for UI. Preserve {{{{placeholders}}}}. Return ONLY JSON array."
                        ).with_model("openai", "gpt-5.2")
                        
                        response = await chat.send_message(UserMessage(text=f"Translate: {json.dumps(texts, ensure_ascii=False)}"))
                        
                        clean = response.strip()
                        if clean.startswith("```"):
                            clean = clean.split("```")[1]
                            if clean.startswith("json"):
                                clean = clean[4:]
                        
                        translated = json.loads(clean)
                        
                        if isinstance(translated, list) and len(translated) == len(texts):
                            for j, key in enumerate(keys):
                                if translated[j] != texts[j]:
                                    locale_flat[key] = translated[j]
                                    translated_count += 1
                        
                        await asyncio.sleep(0.3)  # Rate limiting
                        
                    except Exception as batch_error:
                        auto_translation_jobs[job_id]["errors"].append({
                            "language": lang_code,
                            "batch": i,
                            "error": str(batch_error)
                        })
                
                # Save updated locale
                updated_data = unflatten_keys(locale_flat)
                with open(locale_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, ensure_ascii=False, indent=2)
                
                auto_translation_jobs[job_id]["languages_completed"] += 1
                auto_translation_jobs[job_id]["keys_translated"] += translated_count
                auto_translation_jobs[job_id]["progress"].append({
                    "language": lang_code,
                    "status": "completed",
                    "keys_translated": translated_count
                })
                
            except Exception as lang_error:
                auto_translation_jobs[job_id]["errors"].append({
                    "language": lang_code,
                    "error": str(lang_error)
                })
                auto_translation_jobs[job_id]["progress"].append({
                    "language": lang_code,
                    "status": "error",
                    "error": str(lang_error)
                })
        
        auto_translation_jobs[job_id]["status"] = "completed"
        auto_translation_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    background_tasks.add_task(run_auto_translation)
    
    return {
        "job_id": job_id,
        "status": "started",
        "languages_to_translate": len(languages_to_translate),
        "total_keys_to_translate": total_keys,
        "estimated_time_minutes": max(1, total_keys // 50),
        "target_kpi": request.target_kpi,
        "message": f"Auto-translation started for {len(languages_to_translate)} languages"
    }


@router.get("/auto-translate/{job_id}")
async def get_auto_translation_status(job_id: str):
    """Get status of an auto-translation job"""
    if job_id not in auto_translation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return auto_translation_jobs[job_id]

