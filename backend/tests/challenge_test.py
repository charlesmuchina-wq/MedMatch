#!/usr/bin/env python3
"""
MedMatch Challenge Test Suite
Tests system reliability, stability, and resilience
Load levels: 2000, 4000, 6000, 8000, 10000 requests
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime
from collections import defaultdict

API_URL = "https://ai-job-hunter-4.preview.emergentagent.com/api"

# Test endpoints with different complexity levels
ENDPOINTS = {
    "health": {"method": "GET", "path": "/health", "auth": False, "weight": "light"},
    "languages": {"method": "GET", "path": "/translate/languages", "auth": False, "weight": "light"},
    "id_levels": {"method": "GET", "path": "/id-verification/levels", "auth": False, "weight": "light"},
    "bio_supported": {"method": "GET", "path": "/biometric/supported", "auth": False, "weight": "light"},
    "companies": {"method": "GET", "path": "/companies/", "auth": False, "weight": "medium"},
}

AUTH_ENDPOINTS = {
    "profile": {"method": "GET", "path": "/auth/me", "weight": "light"},
    "saved_jobs": {"method": "GET", "path": "/saved-jobs", "weight": "medium"},
    "applications": {"method": "GET", "path": "/applications", "weight": "medium"},
    "notifications": {"method": "GET", "path": "/notifications/history", "weight": "medium"},
    "qa_favorites": {"method": "GET", "path": "/qa-practice/favorites", "weight": "medium"},
    "analytics": {"method": "GET", "path": "/analytics/dashboard", "weight": "heavy"},
    "messages": {"method": "GET", "path": "/messages/conversations", "weight": "heavy"},
}

class ChallengeTest:
    def __init__(self):
        self.results = defaultdict(lambda: defaultdict(list))
        self.session_cookie = None
        
    async def login(self, session):
        """Get authentication cookie"""
        try:
            async with session.post(
                f"{API_URL}/auth/login",
                json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
            ) as resp:
                if resp.status == 200:
                    # Extract session cookie
                    cookies = session.cookie_jar.filter_cookies(API_URL)
                    self.session_cookie = {k: v.value for k, v in cookies.items()}
                    return True
        except Exception as e:
            print(f"Login failed: {e}")
        return False

    async def make_request(self, session, endpoint_name, endpoint_config, use_auth=False):
        """Make a single request and measure response time"""
        url = f"{API_URL}{endpoint_config['path']}"
        method = endpoint_config.get('method', 'GET')
        
        start_time = time.perf_counter()
        try:
            if method == "GET":
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    status = resp.status
                    await resp.read()
            else:
                async with session.post(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    status = resp.status
                    await resp.read()
                    
            elapsed = (time.perf_counter() - start_time) * 1000  # ms
            return {
                "success": status < 400,
                "status": status,
                "time_ms": elapsed,
                "error": None
            }
        except asyncio.TimeoutError:
            return {"success": False, "status": 0, "time_ms": 30000, "error": "timeout"}
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return {"success": False, "status": 0, "time_ms": elapsed, "error": str(e)[:50]}

    async def run_batch(self, session, endpoint_name, endpoint_config, count, use_auth=False):
        """Run a batch of requests concurrently"""
        tasks = [
            self.make_request(session, endpoint_name, endpoint_config, use_auth)
            for _ in range(count)
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def run_challenge_level(self, level, session):
        """Run tests at a specific challenge level"""
        print(f"\n{'='*60}")
        print(f"CHALLENGE LEVEL: {level} requests")
        print(f"{'='*60}")
        
        level_results = {}
        
        # Distribute requests across endpoints
        requests_per_endpoint = level // (len(ENDPOINTS) + len(AUTH_ENDPOINTS))
        
        # Test public endpoints
        print("\n[Public Endpoints]")
        for name, config in ENDPOINTS.items():
            print(f"  Testing {name}...", end=" ", flush=True)
            start = time.perf_counter()
            results = await self.run_batch(session, name, config, requests_per_endpoint)
            elapsed = time.perf_counter() - start
            
            successes = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            times = [r["time_ms"] for r in results if isinstance(r, dict) and r.get("success")]
            
            level_results[name] = {
                "total": requests_per_endpoint,
                "success": successes,
                "failed": requests_per_endpoint - successes,
                "success_rate": (successes / requests_per_endpoint) * 100,
                "avg_time_ms": statistics.mean(times) if times else 0,
                "p95_time_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else 0,
                "p99_time_ms": sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else 0,
                "throughput_rps": requests_per_endpoint / elapsed if elapsed > 0 else 0,
                "weight": config["weight"]
            }
            print(f"✓ {successes}/{requests_per_endpoint} ({level_results[name]['success_rate']:.1f}%)")
        
        # Test authenticated endpoints
        print("\n[Authenticated Endpoints]")
        for name, config in AUTH_ENDPOINTS.items():
            print(f"  Testing {name}...", end=" ", flush=True)
            start = time.perf_counter()
            results = await self.run_batch(session, name, config, requests_per_endpoint, use_auth=True)
            elapsed = time.perf_counter() - start
            
            successes = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            times = [r["time_ms"] for r in results if isinstance(r, dict) and r.get("success")]
            
            level_results[name] = {
                "total": requests_per_endpoint,
                "success": successes,
                "failed": requests_per_endpoint - successes,
                "success_rate": (successes / requests_per_endpoint) * 100,
                "avg_time_ms": statistics.mean(times) if times else 0,
                "p95_time_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else 0,
                "p99_time_ms": sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else 0,
                "throughput_rps": requests_per_endpoint / elapsed if elapsed > 0 else 0,
                "weight": config["weight"]
            }
            print(f"✓ {successes}/{requests_per_endpoint} ({level_results[name]['success_rate']:.1f}%)")
        
        return level_results

    async def run_full_challenge(self):
        """Run the complete challenge test suite"""
        print("\n" + "="*70)
        print("MEDMATCH CHALLENGE TEST SUITE")
        print("Reliability, Stability & Resilience Assessment")
        print("="*70)
        print(f"Start Time: {datetime.now().isoformat()}")
        print(f"API Target: {API_URL}")
        print(f"Challenge Levels: 2000, 4000, 6000, 8000, 10000")
        
        challenge_levels = [2000, 4000, 6000, 8000, 10000]
        all_results = {}
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Login first
            print("\n[Authentication]")
            if await self.login(session):
                print("  ✓ Login successful")
            else:
                print("  ✗ Login failed - some tests will fail")
            
            # Run each challenge level
            for level in challenge_levels:
                try:
                    results = await self.run_challenge_level(level, session)
                    all_results[level] = results
                except Exception as e:
                    print(f"  ✗ Level {level} failed: {e}")
                    all_results[level] = {"error": str(e)}
                
                # Brief pause between levels
                await asyncio.sleep(2)
        
        return all_results

    def generate_report(self, all_results):
        """Generate comprehensive test report"""
        report = {
            "test_date": datetime.now().isoformat(),
            "api_url": API_URL,
            "challenge_levels": list(all_results.keys()),
            "results_by_level": all_results,
            "summary": {},
            "reliability_score": 0,
            "stability_score": 0,
            "resilience_score": 0
        }
        
        # Calculate aggregate metrics
        total_requests = 0
        total_successes = 0
        all_response_times = []
        success_rates_by_level = []
        
        for level, endpoints in all_results.items():
            if isinstance(endpoints, dict) and "error" not in endpoints:
                level_successes = 0
                level_total = 0
                for name, metrics in endpoints.items():
                    if isinstance(metrics, dict) and "success" in metrics:
                        total_requests += metrics["total"]
                        total_successes += metrics["success"]
                        level_successes += metrics["success"]
                        level_total += metrics["total"]
                        if metrics["avg_time_ms"] > 0:
                            all_response_times.append(metrics["avg_time_ms"])
                
                if level_total > 0:
                    success_rates_by_level.append((level_successes / level_total) * 100)
        
        # Reliability Score (based on overall success rate)
        if total_requests > 0:
            overall_success_rate = (total_successes / total_requests) * 100
            report["reliability_score"] = min(100, overall_success_rate)
        
        # Stability Score (based on consistency across levels)
        if len(success_rates_by_level) > 1:
            variance = statistics.variance(success_rates_by_level)
            # Lower variance = higher stability
            report["stability_score"] = max(0, 100 - (variance * 2))
        else:
            report["stability_score"] = report["reliability_score"]
        
        # Resilience Score (how well it handles increasing load)
        if len(success_rates_by_level) >= 2:
            # Compare first level vs last level
            degradation = success_rates_by_level[0] - success_rates_by_level[-1]
            report["resilience_score"] = max(0, 100 - (degradation * 2))
        else:
            report["resilience_score"] = report["reliability_score"]
        
        # Overall summary
        report["summary"] = {
            "total_requests": total_requests,
            "total_successes": total_successes,
            "overall_success_rate": (total_successes / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time_ms": statistics.mean(all_response_times) if all_response_times else 0,
            "success_rates_by_level": dict(zip(all_results.keys(), success_rates_by_level))
        }
        
        return report

def print_final_report(report):
    """Print formatted final report"""
    print("\n" + "="*70)
    print("CHALLENGE TEST RESULTS")
    print("="*70)
    
    print(f"\n📊 SUMMARY")
    print(f"   Total Requests: {report['summary']['total_requests']:,}")
    print(f"   Total Successes: {report['summary']['total_successes']:,}")
    print(f"   Overall Success Rate: {report['summary']['overall_success_rate']:.2f}%")
    print(f"   Avg Response Time: {report['summary']['avg_response_time_ms']:.2f}ms")
    
    print(f"\n📈 SUCCESS RATES BY LEVEL")
    for level, rate in report['summary'].get('success_rates_by_level', {}).items():
        bar = "█" * int(rate / 5) + "░" * (20 - int(rate / 5))
        print(f"   {level:>5} requests: {bar} {rate:.1f}%")
    
    print(f"\n🏆 SCORES")
    print(f"   Reliability Score:  {report['reliability_score']:.1f}/100", end="")
    print(f" {'✅ EXCELLENT' if report['reliability_score'] >= 95 else '⚠️ NEEDS IMPROVEMENT' if report['reliability_score'] >= 80 else '❌ CRITICAL'}")
    
    print(f"   Stability Score:    {report['stability_score']:.1f}/100", end="")
    print(f" {'✅ STABLE' if report['stability_score'] >= 90 else '⚠️ VARIABLE' if report['stability_score'] >= 70 else '❌ UNSTABLE'}")
    
    print(f"   Resilience Score:   {report['resilience_score']:.1f}/100", end="")
    print(f" {'✅ RESILIENT' if report['resilience_score'] >= 90 else '⚠️ DEGRADING' if report['resilience_score'] >= 70 else '❌ FRAGILE'}")
    
    overall = (report['reliability_score'] + report['stability_score'] + report['resilience_score']) / 3
    print(f"\n   OVERALL GRADE: {overall:.1f}/100", end="")
    if overall >= 95:
        print(" 🏅 PRODUCTION READY")
    elif overall >= 85:
        print(" ✅ GOOD")
    elif overall >= 70:
        print(" ⚠️ ACCEPTABLE")
    else:
        print(" ❌ NEEDS WORK")
    
    print("\n" + "="*70)

async def main():
    tester = ChallengeTest()
    results = await tester.run_full_challenge()
    report = tester.generate_report(results)
    
    # Save detailed report
    with open("/app/test_reports/challenge_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print_final_report(report)
    
    print(f"\n📁 Detailed report saved: /app/test_reports/challenge_test_report.json")
    print(f"⏱️  Test completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
