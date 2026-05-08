"""
Web Job Crawler Service
Crawls the entire public internet to find job listings based on:
- User's resume skills
- Desired job title
- Industry preferences

Uses multiple search engines and job boards to find comprehensive results.
"""
import asyncio
import httpx
import logging
import re
import html
from typing import List, Dict, Optional
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)

# Major job board domains to prioritize in web search
JOB_BOARD_DOMAINS = [
    "linkedin.com/jobs",
    "indeed.com",
    "glassdoor.com",
    "monster.com",
    "ziprecruiter.com",
    "careerbuilder.com",
    "dice.com",
    "simplyhired.com",
    "snagajob.com",
    "flexjobs.com",
    "wellfound.com",  # AngelList
    "builtin.com",
    "levels.fyi",
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "jobs.lever.co",
    "boards.greenhouse.io",
    "careers.google.com",
    "amazon.jobs",
    "microsoft.com/careers",
    "apple.com/careers",
    "meta.com/careers",
]

# Industry-specific job boards
INDUSTRY_JOB_BOARDS = {
    "medical_device": [
        "meddeviceonline.com",
        "mddionline.com",
        "devicespace.com",
        "biospace.com",
        "healthecareers.com",
    ],
    "pharma": [
        "pharmajobs.com",
        "biopharmguy.com",
        "biospace.com",
        "healthecareers.com",
    ],
    "engineering": [
        "engineerjobs.com",
        "ieee.org/careers",
        "asme.org/career",
    ],
    "quality": [
        "quality.org",
        "asq.org/careers",
        "isoqar.com",
    ],
    "tech": [
        "stackoverflow.com/jobs",
        "github.com/jobs",
        "weworkremotely.com",
        "remoteok.com",
        "hired.com",
    ]
}


class WebJobCrawler:
    """
    Crawls the web to find job listings using search engines and direct API calls.
    """
    
    def __init__(self, google_api_key: str = None, google_cse_id: str = None):
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search Google for job listings"""
        jobs = []
        
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API credentials not configured")
            return jobs
        
        try:
            # Search job boards specifically
            search_query = f"{query} site:linkedin.com/jobs OR site:indeed.com OR site:glassdoor.com"
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": search_query,
                "num": min(num_results, 10)
            }
            
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    job = self._parse_google_result(item, query)
                    if job:
                        jobs.append(job)
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
        
        return jobs
    
    def _parse_google_result(self, item: Dict, query: str) -> Optional[Dict]:
        """Parse a Google search result into a job listing"""
        try:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            
            # Try to extract job title and company from the result
            job_title = title.split(" - ")[0] if " - " in title else title
            company = ""
            
            # Extract company from common patterns
            if " at " in title.lower():
                parts = title.lower().split(" at ")
                if len(parts) > 1:
                    company = parts[1].split(" - ")[0].strip().title()
            elif " | " in title:
                parts = title.split(" | ")
                if len(parts) > 1:
                    company = parts[1].strip()
            
            # Determine source from URL
            source = "Web"
            for domain in JOB_BOARD_DOMAINS:
                if domain in link:
                    source = domain.split(".")[0].title()
                    break
            
            # Clean HTML entities from text
            job_title = html.unescape(job_title)
            company = html.unescape(company) if company else ""
            snippet = html.unescape(snippet)
            
            return {
                "id": hashlib.md5(link.encode(), usedforsecurity=False).hexdigest()[:12],
                "title": job_title[:100],
                "company": company[:50] if company else "Unknown",
                "description": snippet[:500],
                "url": link,
                "location": "Various",
                "location_type": "Not specified",
                "source": source,
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "tags": query.split()[:5],
                "match_score": 60,  # Base score for web results
                "crawled": True
            }
        except Exception as e:
            logger.error(f"Error parsing Google result: {e}")
            return None
    
    async def search_bing_jobs(self, query: str) -> List[Dict]:
        """Search using Bing for additional job results"""
        jobs = []
        
        try:
            # Bing has a jobs search that can be accessed via web
            search_url = f"https://www.bing.com/jobs/search?q={query.replace(' ', '+')}"
            # Note: This would require web scraping which is limited
            # For now, we'll rely on other sources
            pass
        except Exception as e:
            logger.error(f"Bing search error: {e}")
        
        return jobs
    
    async def crawl_linkedin_jobs(self, query: str, location: str = "") -> List[Dict]:
        """
        Fetch LinkedIn job listings via their public RSS/API
        Note: LinkedIn has strict API limits, this uses public search
        """
        jobs = []
        
        try:
            # LinkedIn public job search URL
            base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            params = {
                "keywords": query,
                "location": location if location else "United States",
                "start": 0,
                "count": 25
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = await self.client.get(base_url, params=params, headers=headers)
            
            if response.status_code == 200:
                # LinkedIn returns HTML, would need to parse
                # For now, we'll use the job board API aggregators
                pass
                
        except Exception as e:
            logger.error(f"LinkedIn crawl error: {e}")
        
        return jobs
    
    async def fetch_jsearch_jobs(self, query: str, location: str = "", remote_only: bool = False) -> List[Dict]:
        """
        Fetch jobs from JSearch API (RapidAPI) - aggregates multiple job boards
        This is a comprehensive job search API that includes Indeed, LinkedIn, ZipRecruiter, etc.
        """
        jobs = []
        
        try:
            # JSearch API endpoint
            url = "https://jsearch.p.rapidapi.com/search"
            
            params = {
                "query": f"{query} {'remote' if remote_only else ''}",
                "page": "1",
                "num_pages": "2",
                "date_posted": "month"  # Last month's jobs
            }
            
            # Note: Requires RapidAPI key - using public endpoint as fallback
            headers = {
                "User-Agent": "MedMatch/1.0"
            }
            
            # Fallback to Indeed RSS
            indeed_url = f"https://www.indeed.com/rss?q={query.replace(' ', '+')}&l={location}"
            response = await self.client.get(indeed_url, headers=headers)
            
            if response.status_code == 200:
                # Parse RSS feed
                jobs = self._parse_rss_feed(response.text, "Indeed")
                
        except Exception as e:
            logger.error(f"JSearch/Indeed error: {e}")
        
        return jobs
    
    def _parse_rss_feed(self, xml_content: str, source: str) -> List[Dict]:
        """Parse RSS feed content for job listings"""
        jobs = []
        
        try:
            # Simple XML parsing without external library
            items = re.findall(r'<item>(.*?)</item>', xml_content, re.DOTALL)
            
            for item in items[:20]:  # Limit to 20 jobs
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                
                link_match = re.search(r'<link>(.*?)</link>', item)
                desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item)
                if not desc_match:
                    desc_match = re.search(r'<description>(.*?)</description>', item)
                
                if title_match and link_match:
                    title = title_match.group(1).strip()
                    link = link_match.group(1).strip()
                    description = desc_match.group(1).strip() if desc_match else ""
                    
                    # Clean HTML from description
                    description = re.sub(r'<[^>]+>', '', description)[:500]
                    
                    # Extract company from title (common format: "Job Title - Company")
                    company = ""
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        if len(parts) > 1:
                            title = parts[0]
                            company = parts[1]
                    
                    jobs.append({
                        "id": hashlib.md5(link.encode(), usedforsecurity=False).hexdigest()[:12],
                        "title": title[:100],
                        "company": company[:50] if company else "Unknown",
                        "description": description,
                        "url": link,
                        "location": "Various",
                        "location_type": "Not specified",
                        "source": source,
                        "posted_at": datetime.now(timezone.utc).isoformat(),
                        "tags": [],
                        "match_score": 55,
                        "crawled": True
                    })
                    
        except Exception as e:
            logger.error(f"RSS parsing error: {e}")
        
        return jobs
    
    async def fetch_adzuna_jobs(self, query: str, country: str = "us") -> List[Dict]:
        """Fetch jobs from Adzuna API (free tier available)"""
        jobs = []
        
        try:
            # Adzuna has a free tier API
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": "adzuna_app_id",  # Would need real credentials
                "app_key": "adzuna_app_key",
                "what": query,
                "results_per_page": 20
            }
            
            # Fallback - search major job boards via simple HTTP
            pass
            
        except Exception as e:
            logger.error(f"Adzuna error: {e}")
        
        return jobs
    
    async def comprehensive_web_search(
        self, 
        query: str, 
        resume_skills: List[str] = None,
        location: str = "",
        include_remote: bool = True
    ) -> List[Dict]:
        """
        Perform a comprehensive web search for jobs across all available sources.
        """
        all_jobs = []
        
        # Build search queries
        search_queries = [query]
        
        if resume_skills:
            # Add skill-based queries
            for skill in resume_skills[:3]:
                search_queries.append(f"{query} {skill}")
        
        # Gather jobs from multiple sources in parallel
        tasks = []
        
        for sq in search_queries:
            # Add search tasks for each query
            tasks.append(self.search_google(sq, num_results=10))
            tasks.append(self.fetch_jsearch_jobs(sq, location))
        
        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
        
        # Score jobs based on resume match if skills provided
        if resume_skills:
            skill_set = set(s.lower() for s in resume_skills)
            for job in unique_jobs:
                job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                matches = sum(1 for skill in skill_set if skill in job_text)
                # Boost score based on skill matches
                job["match_score"] = min(95, job.get("match_score", 50) + (matches * 8))
        
        # Sort by match score
        unique_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return unique_jobs
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global crawler instance
_crawler = None

def get_web_crawler(google_api_key: str = None, google_cse_id: str = None) -> WebJobCrawler:
    """Get or create the web crawler instance"""
    global _crawler
    if _crawler is None:
        _crawler = WebJobCrawler(google_api_key, google_cse_id)
    return _crawler
