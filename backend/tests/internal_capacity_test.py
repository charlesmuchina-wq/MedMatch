#!/usr/bin/env python3
"""
MedMatch Internal Capacity Test
Tests actual application capacity without external rate limiting
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime

# Test against localhost to bypass external rate limiting
API_URL = "http://localhost:8001/api"

ENDPOINTS = [
    {"name": "health", "path": "/health"},
    {"name": "supervisor", "path": "/supervisor/health"},
    {"name": "languages", "path": "/cached/languages"},
    {"name": "id_levels", "path": "/cached/id-levels"},
]

async def test_endpoint(session, endpoint, semaphore):
    """Test single endpoint"""
    async with semaphore:
        start = time.perf_counter()
        try:
            async with session.get(
                f"{API_URL}{endpoint['path']}", 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                elapsed = (time.perf_counter() - start) * 1000
                return {"success": resp.status < 400, "time_ms": elapsed, "status": resp.status}
        except Exception as e:
            return {"success": False, "time_ms": 10000, "error": str(e)[:30]}

async def run_level(session, total_requests, concurrency):
    """Run load test at specified level"""
    semaphore = asyncio.Semaphore(concurrency)
    requests_per_endpoint = total_requests // len(ENDPOINTS)
    
    all_results = []
    
    for endpoint in ENDPOINTS:
        tasks = [test_endpoint(session, endpoint, semaphore) for _ in range(requests_per_endpoint)]
        results = await asyncio.gather(*tasks)
        all_results.extend(results)
    
    return all_results

async def main():
    print("="*70)
    print("MEDMATCH INTERNAL CAPACITY TEST")
    print("="*70)
    print(f"Target: {API_URL} (localhost - bypasses external rate limiting)")
    print(f"Start: {datetime.now().isoformat()}")
    
    test_levels = [
        (500, 50, "Warm-up"),
        (1000, 100, "Light"),
        (2000, 150, "Medium"),
        (3000, 200, "Heavy"),
        (5000, 250, "Stress"),
        (10000, 300, "Peak"),
    ]
    
    results_summary = []
    
    connector = aiohttp.TCPConnector(limit=500, limit_per_host=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        for total, concurrency, label in test_levels:
            print(f"\n{'='*60}")
            print(f"{label.upper()} LOAD ({total} requests, {concurrency} concurrent)")
            print("="*60)
            
            start = time.perf_counter()
            results = await run_level(session, total, concurrency)
            elapsed = time.perf_counter() - start
            
            successes = [r for r in results if r.get("success")]
            times = [r["time_ms"] for r in successes]
            
            success_rate = (len(successes) / len(results)) * 100 if results else 0
            avg_time = statistics.mean(times) if times else 0
            throughput = len(results) / elapsed if elapsed > 0 else 0
            
            results_summary.append({
                "level": label,
                "total": total,
                "concurrency": concurrency,
                "success_rate": success_rate,
                "avg_time_ms": avg_time,
                "throughput": throughput
            })
            
            print(f"\n  Total Requests: {len(results)}")
            print(f"  Successful: {len(successes)} ({success_rate:.1f}%)")
            print(f"  Avg Response: {avg_time:.1f}ms")
            print(f"  Throughput: {throughput:.1f} req/sec")
            print(f"  Duration: {elapsed:.2f}s")
            
            # Brief pause
            await asyncio.sleep(2)
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    print("\n📊 Success Rates:")
    all_success = True
    for r in results_summary:
        bar = "█" * int(r["success_rate"] / 5) + "░" * (20 - int(r["success_rate"] / 5))
        status = "✅" if r["success_rate"] >= 95 else "⚠️" if r["success_rate"] >= 80 else "❌"
        if r["success_rate"] < 95:
            all_success = False
        print(f"   {r['level']:>8} ({r['total']:>5} req): {bar} {r['success_rate']:.1f}% {status}")
    
    # Calculate max sustainable throughput
    sustainable_results = [r for r in results_summary if r["success_rate"] >= 95]
    if sustainable_results:
        max_throughput = max(r["throughput"] for r in sustainable_results)
        max_level = max(r["total"] for r in sustainable_results)
        print(f"\n🚀 Maximum Sustainable Load: {max_level} requests at {max_throughput:.0f} req/sec")
    
    print(f"\n⏱️  Test completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
