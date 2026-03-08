#!/usr/bin/env python3
"""
MedMatch Gradual Load Test
More realistic load testing with proper pacing
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime

API_URL = "https://karau-enzi-nexus.preview.emergentagent.com/api"

# Endpoints to test
ENDPOINTS = [
    {"name": "health", "path": "/health", "auth": False},
    {"name": "languages", "path": "/translate/languages", "auth": False},
    {"name": "id_levels", "path": "/id-verification/levels", "auth": False},
    {"name": "biometric", "path": "/biometric/supported", "auth": False},
    {"name": "companies", "path": "/companies/", "auth": False},
    {"name": "profile", "path": "/auth/me", "auth": True},
    {"name": "saved_jobs", "path": "/saved-jobs", "auth": True},
    {"name": "qa_favorites", "path": "/qa-practice/favorites", "auth": True},
    {"name": "notifications", "path": "/notifications/preferences", "auth": True},
]

async def login(session):
    """Get authentication"""
    async with session.post(
        f"{API_URL}/auth/login",
        json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
    ) as resp:
        return resp.status == 200

async def test_endpoint(session, endpoint, semaphore):
    """Test single endpoint with rate limiting"""
    async with semaphore:
        start = time.perf_counter()
        try:
            async with session.get(
                f"{API_URL}{endpoint['path']}", 
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                elapsed = (time.perf_counter() - start) * 1000
                return {
                    "success": resp.status < 400,
                    "status": resp.status,
                    "time_ms": elapsed
                }
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return {"success": False, "status": 0, "time_ms": elapsed, "error": str(e)[:30]}

async def run_load_level(session, level, concurrency=20):
    """Run tests at a specific load level with controlled concurrency"""
    semaphore = asyncio.Semaphore(concurrency)
    results = {ep["name"]: [] for ep in ENDPOINTS}
    
    requests_per_endpoint = level // len(ENDPOINTS)
    
    print(f"\n  Level {level}: Testing with {concurrency} concurrent connections...")
    
    for endpoint in ENDPOINTS:
        tasks = [test_endpoint(session, endpoint, semaphore) for _ in range(requests_per_endpoint)]
        endpoint_results = await asyncio.gather(*tasks)
        results[endpoint["name"]] = endpoint_results
    
    return results

def calculate_metrics(results):
    """Calculate metrics from results"""
    metrics = {}
    for name, data in results.items():
        successes = [r for r in data if r.get("success")]
        times = [r["time_ms"] for r in successes]
        
        metrics[name] = {
            "total": len(data),
            "success": len(successes),
            "success_rate": (len(successes) / len(data) * 100) if data else 0,
            "avg_time_ms": statistics.mean(times) if times else 0,
            "p95_time_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else 0,
            "min_time_ms": min(times) if times else 0,
            "max_time_ms": max(times) if times else 0,
        }
    return metrics

async def main():
    print("="*70)
    print("MEDMATCH GRADUAL LOAD TEST")
    print("="*70)
    print(f"Start: {datetime.now().isoformat()}")
    print(f"Target: {API_URL}")
    
    # Test levels with different concurrency
    test_config = [
        {"requests": 100, "concurrency": 10, "label": "Light Load"},
        {"requests": 500, "concurrency": 25, "label": "Medium Load"},
        {"requests": 1000, "concurrency": 50, "label": "Heavy Load"},
        {"requests": 2000, "concurrency": 75, "label": "Stress Load"},
        {"requests": 3000, "concurrency": 100, "label": "Peak Load"},
    ]
    
    all_results = {}
    
    connector = aiohttp.TCPConnector(limit=150, limit_per_host=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Login
        print("\n[Authenticating...]")
        if await login(session):
            print("  ✓ Authenticated")
        
        for config in test_config:
            print(f"\n{'='*60}")
            print(f"{config['label'].upper()} ({config['requests']} requests, {config['concurrency']} concurrent)")
            print("="*60)
            
            start = time.perf_counter()
            results = await run_load_level(session, config["requests"], config["concurrency"])
            elapsed = time.perf_counter() - start
            
            metrics = calculate_metrics(results)
            all_results[config["requests"]] = {
                "config": config,
                "metrics": metrics,
                "total_time_sec": elapsed
            }
            
            # Print summary for this level
            total_success = sum(m["success"] for m in metrics.values())
            total_requests = sum(m["total"] for m in metrics.values())
            avg_times = [m["avg_time_ms"] for m in metrics.values() if m["avg_time_ms"] > 0]
            
            print("\n  Results:")
            print(f"    Total Requests: {total_requests}")
            print(f"    Successful: {total_success} ({total_success/total_requests*100:.1f}%)")
            print(f"    Avg Response: {statistics.mean(avg_times):.1f}ms" if avg_times else "    Avg Response: N/A")
            print(f"    Throughput: {total_requests/elapsed:.1f} req/sec")
            
            # Brief pause between levels
            await asyncio.sleep(3)
    
    # Final Report
    print("\n" + "="*70)
    print("FINAL ASSESSMENT")
    print("="*70)
    
    # Calculate overall scores
    success_rates = []
    for level, data in all_results.items():
        total = sum(m["total"] for m in data["metrics"].values())
        success = sum(m["success"] for m in data["metrics"].values())
        if total > 0:
            success_rates.append((level, success/total*100))
    
    if success_rates:
        print("\n📊 Success Rates by Load Level:")
        for level, rate in success_rates:
            bar = "█" * int(rate / 5) + "░" * (20 - int(rate / 5))
            status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
            print(f"   {level:>5} requests: {bar} {rate:.1f}% {status}")
        
        # Scores
        reliability = statistics.mean([r for _, r in success_rates])
        stability = 100 - statistics.stdev([r for _, r in success_rates]) if len(success_rates) > 1 else reliability
        
        # Resilience: compare light vs peak load
        if len(success_rates) >= 2:
            degradation = success_rates[0][1] - success_rates[-1][1]
            resilience = max(0, 100 - degradation)
        else:
            resilience = reliability
        
        print("\n🏆 SCORES:")
        print(f"   Reliability:  {reliability:.1f}/100 {'✅' if reliability >= 90 else '⚠️' if reliability >= 70 else '❌'}")
        print(f"   Stability:    {stability:.1f}/100 {'✅' if stability >= 85 else '⚠️' if stability >= 70 else '❌'}")
        print(f"   Resilience:   {resilience:.1f}/100 {'✅' if resilience >= 85 else '⚠️' if resilience >= 70 else '❌'}")
        
        overall = (reliability + stability + resilience) / 3
        print(f"\n   OVERALL: {overall:.1f}/100", end=" ")
        if overall >= 90:
            print("🏅 EXCELLENT - Production Ready")
        elif overall >= 80:
            print("✅ GOOD - Minor optimizations recommended")
        elif overall >= 70:
            print("⚠️ ACCEPTABLE - Needs optimization for scale")
        else:
            print("❌ NEEDS IMPROVEMENT")
        
        # Save report
        report = {
            "test_date": datetime.now().isoformat(),
            "results": all_results,
            "scores": {
                "reliability": reliability,
                "stability": stability,
                "resilience": resilience,
                "overall": overall
            }
        }
        
        with open("/app/test_reports/gradual_load_test.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print("\n📁 Report saved: /app/test_reports/gradual_load_test.json")

if __name__ == "__main__":
    asyncio.run(main())
