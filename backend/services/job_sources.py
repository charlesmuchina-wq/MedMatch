"""
Job Sources Service - Multi-Board Integration
Aggregates jobs from 15+ specialized job boards across Healthcare, Engineering, Tech, Pharma, and Med Device.

Priority Boards:
1. PharmiWeb.Jobs - Pharma & Life Sciences
2. MedDeviceJobs - Medical Devices  
3. Health eCareers - Clinical Healthcare
4. Dice - Tech & Engineering
5. Wellfound - Tech & Med-Tech Startups
6. BioSpace - Biotech & Pharma
7. Crunchboard - Tech & Startup Eng
8. We Work Remotely - All Remote
9. USAJOBS - Public Healthcare & Eng
10. RemoteOK - Remote Tech
11. Remotive - Remote All Industries
12. Himalayas - Remote Jobs
13. Arbeitnow - EU Remote
14. Jobicy - Remote Tech
15. Google CSE (Indeed, LinkedIn, Glassdoor)
"""
import asyncio
import httpx
import logging
import re
import hashlib
import html
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
import uuid

logger = logging.getLogger(__name__)

# Industry-specific job board configurations
JOB_BOARDS = {
    "pharmiweb": {
        "name": "PharmiWeb.Jobs",
        "focus": "Pharma & Life Sciences",
        "base_url": "https://www.pharmiweb.com/api/jobs",
        "active": True
    },
    "meddevicejobs": {
        "name": "MedDeviceJobs", 
        "focus": "Medical Devices",
        "base_url": "https://www.meddevicejobs.com",
        "active": True
    },
    "healthecareers": {
        "name": "Health eCareers",
        "focus": "Clinical Healthcare",
        "base_url": "https://www.healthecareers.com",
        "active": True
    },
    "biospace": {
        "name": "BioSpace",
        "focus": "Biotech & Pharma",
        "base_url": "https://www.biospace.com/jobs",
        "active": True
    },
    "weworkremotely": {
        "name": "We Work Remotely",
        "focus": "Remote Tech/Eng",
        "base_url": "https://weworkremotely.com/api/listings",
        "active": True
    },
    "usajobs": {
        "name": "USAJOBS",
        "focus": "Government Healthcare & Eng",
        "base_url": "https://data.usajobs.gov/api/search",
        "active": True
    },
    "remoteok": {
        "name": "RemoteOK",
        "focus": "Remote Tech",
        "base_url": "https://remoteok.com/api",
        "active": True
    },
    "remotive": {
        "name": "Remotive",
        "focus": "Remote All",
        "base_url": "https://remotive.com/api/remote-jobs",
        "active": True
    },
    "himalayas": {
        "name": "Himalayas",
        "focus": "Remote Jobs",
        "base_url": "https://himalayas.app/jobs/api",
        "active": True
    },
    "arbeitnow": {
        "name": "Arbeitnow",
        "focus": "EU Remote",
        "base_url": "https://www.arbeitnow.com/api/job-board-api",
        "active": True
    },
    "jobicy": {
        "name": "Jobicy",
        "focus": "Remote Tech",
        "base_url": "https://jobicy.com/api/v2/remote-jobs",
        "active": True
    }
}

# Keywords for industry-specific searches
INDUSTRY_KEYWORDS = {
    "pharma": ["pharmaceutical", "pharma", "drug", "clinical trial", "GMP", "FDA", "regulatory"],
    "medical_device": ["medical device", "medtech", "ISO 13485", "510k", "implant", "diagnostic"],
    "healthcare": ["healthcare", "clinical", "nurse", "physician", "hospital", "patient care"],
    "biotech": ["biotech", "biotechnology", "genomics", "cell therapy", "biologics"],
    "engineering": ["engineer", "manufacturing", "quality", "process", "validation"]
}


class JobSourcesService:
    """
    Service to fetch jobs from multiple specialized job boards.
    """
    
    def __init__(self, google_api_key: str = None, google_cse_id: str = None):
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.client = None
    
    def _clean_text(self, text: str) -> str:
        """Clean and decode HTML entities from text"""
        if not text:
            return ""
        # Decode HTML entities (e.g., &amp;#8211; -> –)
        text = html.unescape(text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _clean_tags(self, tags) -> List[str]:
        """Clean and flatten tags list, decode HTML entities"""
        if not tags:
            return []
        
        cleaned = []
        for tag in tags:
            if isinstance(tag, list):
                # Flatten nested lists
                for t in tag:
                    if t:
                        cleaned.append(self._clean_text(str(t)))
            elif tag:
                cleaned.append(self._clean_text(str(tag)))
        
        # Remove empty strings and duplicates while preserving order
        seen = set()
        result = []
        for t in cleaned:
            if t and t not in seen:
                seen.add(t)
                result.append(t)
        return result
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=20.0)
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
    
    def _generate_job_id(self, url: str) -> str:
        """Generate unique job ID from URL"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _calculate_freshness(self, posted_date: str) -> Dict:
        """Calculate job freshness and return badge info"""
        try:
            if not posted_date:
                return {"badge": "Unknown", "is_fresh": False, "minutes_ago": None}
            
            # Try parsing different date formats
            now = datetime.now(timezone.utc)
            posted = None
            
            # ISO format
            try:
                posted = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
            except Exception:
                pass
            
            # Try RFC 2822 format (common in RSS feeds)
            if not posted:
                try:
                    from email.utils import parsedate_to_datetime
                    posted = parsedate_to_datetime(posted_date)
                except Exception:
                    pass
            
            if not posted:
                return {"badge": "Recently", "is_fresh": True, "minutes_ago": None}
            
            # Ensure posted is timezone-aware
            if posted.tzinfo is None:
                posted = posted.replace(tzinfo=timezone.utc)
            
            diff = now - posted
            minutes = diff.total_seconds() / 60
            hours = minutes / 60
            days = hours / 24
            
            if minutes < 60:
                badge = f"Posted {int(minutes)} min ago"
                is_fresh = True
            elif hours < 24:
                badge = f"Posted {int(hours)}h ago"
                is_fresh = True
            elif days < 2:
                badge = "Posted yesterday"
                is_fresh = True
            elif days < 7:
                badge = f"Posted {int(days)} days ago"
                is_fresh = days < 3
            elif days < 30:
                badge = f"Posted {int(days/7)} weeks ago"
                is_fresh = False
            else:
                badge = f"Posted {int(days/30)} months ago"
                is_fresh = False
            
            return {"badge": badge, "is_fresh": is_fresh, "minutes_ago": int(minutes)}
        except Exception as e:
            logger.error(f"Freshness calculation error: {e}")
            return {"badge": "Recently", "is_fresh": True, "minutes_ago": None}
    
    # ============== RemoteOK ==============
    async def fetch_remoteok(self, query: str = "") -> List[Dict]:
        """Fetch jobs from RemoteOK API"""
        jobs = []
        try:
            client = await self.get_client()
            response = await client.get(
                "https://remoteok.com/api",
                headers={"User-Agent": "MedMatch/2.0"}
            )
            if response.status_code == 200:
                data = response.json()
                for item in data[1:25]:  # Skip first (legal) item
                    if query and query.lower() not in str(item).lower():
                        continue
                    
                    posted = item.get("date", "")
                    freshness = self._calculate_freshness(posted)
                    
                    jobs.append({
                        "id": self._generate_job_id(item.get("url", str(uuid.uuid4()))),
                        "title": item.get("position", ""),
                        "company": item.get("company", ""),
                        "location": item.get("location", "Remote"),
                        "description": item.get("description", "")[:500],
                        "url": item.get("url", ""),
                        "salary": item.get("salary", ""),
                        "tags": item.get("tags", []),
                        "source": "RemoteOK",
                        "source_logo": "https://remoteok.com/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,
                        "industry": "Tech"
                    })
        except Exception as e:
            logger.error(f"RemoteOK error: {e}")
        return jobs
    
    # ============== Remotive ==============
    async def fetch_remotive(self, query: str = "") -> List[Dict]:
        """Fetch jobs from Remotive API"""
        jobs = []
        try:
            client = await self.get_client()
            params = {"limit": 25}
            if query:
                params["search"] = query
            
            response = await client.get(
                "https://remotive.com/api/remote-jobs",
                params=params
            )
            if response.status_code == 200:
                data = response.json()
                for item in data.get("jobs", [])[:25]:
                    posted = item.get("publication_date", "")
                    freshness = self._calculate_freshness(posted)
                    
                    jobs.append({
                        "id": self._generate_job_id(item.get("url", str(uuid.uuid4()))),
                        "title": item.get("title", ""),
                        "company": item.get("company_name", ""),
                        "location": item.get("candidate_required_location", "Remote"),
                        "description": item.get("description", "")[:500],
                        "url": item.get("url", ""),
                        "salary": item.get("salary", ""),
                        "tags": [item.get("category", "")],
                        "source": "Remotive",
                        "source_logo": "https://remotive.com/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,
                        "industry": item.get("category", "Tech")
                    })
        except Exception as e:
            logger.error(f"Remotive error: {e}")
        return jobs
    
    # ============== We Work Remotely ==============
    async def fetch_weworkremotely(self, query: str = "") -> List[Dict]:
        """Fetch jobs from We Work Remotely - hand-screened, low ghost job volume"""
        jobs = []
        try:
            client = await self.get_client()
            # WWR uses categories - fetch programming and design
            categories = ["programming", "design", "devops-sysadmin", "product", "customer-support"]
            
            for category in categories[:2]:  # Limit to avoid rate limiting
                try:
                    response = await client.get(
                        f"https://weworkremotely.com/categories/{category}/jobs.rss",
                        headers={"User-Agent": "MedMatch/2.0"}
                    )
                    if response.status_code == 200:
                        # Parse RSS
                        items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                        for item in items[:10]:
                            title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                            link_match = re.search(r'<link>(.*?)</link>', item)
                            desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item, re.DOTALL)
                            pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                            
                            if title_match and link_match:
                                title = title_match.group(1).strip()
                                if query and query.lower() not in title.lower():
                                    continue
                                
                                url = link_match.group(1).strip()
                                desc = re.sub(r'<[^>]+>', '', desc_match.group(1))[:500] if desc_match else ""
                                posted = pub_match.group(1) if pub_match else ""
                                freshness = self._calculate_freshness(posted)
                                
                                # Extract company from title (format: "Company: Job Title")
                                company = ""
                                if ": " in title:
                                    parts = title.split(": ", 1)
                                    company = parts[0]
                                    title = parts[1] if len(parts) > 1 else title
                                
                                jobs.append({
                                    "id": self._generate_job_id(url),
                                    "title": title[:100],
                                    "company": company[:50],
                                    "location": "Remote",
                                    "description": desc,
                                    "url": url,
                                    "tags": [category],
                                    "source": "WeWorkRemotely",
                                    "source_logo": "https://weworkremotely.com/favicon.ico",
                                    "posted_at": posted,
                                    "freshness": freshness,
                                    "verified": True,  # Hand-screened
                                    "industry": "Tech"
                                })
                except Exception as e:
                    logger.error(f"WWR category {category} error: {e}")
        except Exception as e:
            logger.error(f"WeWorkRemotely error: {e}")
        return jobs
    
    # ============== Himalayas ==============
    async def fetch_himalayas(self, query: str = "") -> List[Dict]:
        """Fetch jobs from Himalayas API"""
        jobs = []
        try:
            client = await self.get_client()
            response = await client.get(
                "https://himalayas.app/jobs/api",
                params={"limit": 25}
            )
            if response.status_code == 200:
                data = response.json()
                for item in data.get("jobs", [])[:25]:
                    if query and query.lower() not in str(item).lower():
                        continue
                    
                    posted = item.get("pubDate", "")
                    freshness = self._calculate_freshness(posted)
                    
                    jobs.append({
                        "id": self._generate_job_id(item.get("applicationLink", str(uuid.uuid4()))),
                        "title": item.get("title", ""),
                        "company": item.get("companyName", ""),
                        "location": "Remote",
                        "description": item.get("description", "")[:500],
                        "url": item.get("applicationLink", ""),
                        "tags": item.get("categories", []),
                        "source": "Himalayas",
                        "source_logo": "https://himalayas.app/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,
                        "industry": "Tech"
                    })
        except Exception as e:
            logger.error(f"Himalayas error: {e}")
        return jobs
    
    # ============== Arbeitnow (EU) ==============
    async def fetch_arbeitnow(self, query: str = "") -> List[Dict]:
        """Fetch jobs from Arbeitnow API - EU focused"""
        jobs = []
        try:
            client = await self.get_client()
            response = await client.get("https://www.arbeitnow.com/api/job-board-api")
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", [])[:25]:
                    if query and query.lower() not in str(item).lower():
                        continue
                    
                    posted = item.get("created_at", "")
                    freshness = self._calculate_freshness(posted)
                    
                    jobs.append({
                        "id": self._generate_job_id(item.get("url", str(uuid.uuid4()))),
                        "title": item.get("title", ""),
                        "company": item.get("company_name", ""),
                        "location": item.get("location", "Remote EU"),
                        "description": item.get("description", "")[:500],
                        "url": item.get("url", ""),
                        "tags": item.get("tags", []),
                        "source": "Arbeitnow",
                        "source_logo": "https://arbeitnow.com/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,
                        "industry": "Tech"
                    })
        except Exception as e:
            logger.error(f"Arbeitnow error: {e}")
        return jobs
    
    # ============== Jobicy ==============
    async def fetch_jobicy(self, query: str = "") -> List[Dict]:
        """Fetch jobs from Jobicy API"""
        jobs = []
        try:
            client = await self.get_client()
            params = {"count": 25, "geo": "usa"}
            if query:
                params["tag"] = query
            
            response = await client.get(
                "https://jobicy.com/api/v2/remote-jobs",
                params=params
            )
            if response.status_code == 200:
                data = response.json()
                for item in data.get("jobs", [])[:25]:
                    posted = item.get("pubDate", "")
                    freshness = self._calculate_freshness(posted)
                    
                    salary = ""
                    if item.get("annualSalaryMin") and item.get("annualSalaryMax"):
                        salary = f"${item.get('annualSalaryMin', 0):,} - ${item.get('annualSalaryMax', 0):,}"
                    
                    jobs.append({
                        "id": self._generate_job_id(item.get("url", str(uuid.uuid4()))),
                        "title": item.get("jobTitle", ""),
                        "company": item.get("companyName", ""),
                        "location": item.get("jobGeo", "Remote"),
                        "description": item.get("jobExcerpt", "")[:500],
                        "url": item.get("url", ""),
                        "salary": salary,
                        "tags": [item.get("jobIndustry", "")],
                        "source": "Jobicy",
                        "source_logo": "https://jobicy.com/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,
                        "industry": item.get("jobIndustry", "Tech")
                    })
        except Exception as e:
            logger.error(f"Jobicy error: {e}")
        return jobs
    
    # ============== USAJOBS (Government) ==============
    async def fetch_usajobs(self, query: str = "", location: str = "") -> List[Dict]:
        """Fetch jobs from USAJOBS API - Government healthcare & engineering"""
        jobs = []
        try:
            client = await self.get_client()
            
            # USAJOBS requires API key - using public endpoint
            search_query = query if query else "healthcare OR engineering OR quality"
            
            params = {
                "Keyword": search_query,
                "ResultsPerPage": 25
            }
            
            headers = {
                "User-Agent": "MedMatch/2.0",
                "Host": "data.usajobs.gov"
            }
            
            response = await client.get(
                "https://data.usajobs.gov/api/search",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("SearchResult", {}).get("SearchResultItems", [])[:25]:
                    job = item.get("MatchedObjectDescriptor", {})
                    posted = job.get("PublicationStartDate", "")
                    freshness = self._calculate_freshness(posted)
                    
                    # Extract salary
                    salary = ""
                    remuneration = job.get("PositionRemuneration", [])
                    if remuneration:
                        min_sal = remuneration[0].get("MinimumRange", "")
                        max_sal = remuneration[0].get("MaximumRange", "")
                        if min_sal and max_sal:
                            salary = f"${int(float(min_sal)):,} - ${int(float(max_sal)):,}"
                    
                    # Extract location
                    locations = job.get("PositionLocationDisplay", "")
                    
                    jobs.append({
                        "id": self._generate_job_id(job.get("ApplyURI", [str(uuid.uuid4())])[0] if job.get("ApplyURI") else str(uuid.uuid4())),
                        "title": job.get("PositionTitle", ""),
                        "company": job.get("OrganizationName", "US Government"),
                        "location": locations,
                        "description": job.get("QualificationSummary", "")[:500],
                        "url": job.get("ApplyURI", [""])[0] if job.get("ApplyURI") else "",
                        "salary": salary,
                        "tags": ["Government", "Federal"],
                        "source": "USAJOBS",
                        "source_logo": "https://www.usajobs.gov/favicon.ico",
                        "posted_at": posted,
                        "freshness": freshness,
                        "verified": True,  # Government source = highly verified
                        "industry": "Government"
                    })
        except Exception as e:
            logger.error(f"USAJOBS error: {e}")
        return jobs
    
    # ============== Google CSE (Indeed, LinkedIn, Glassdoor) ==============
    async def fetch_google_cse(self, query: str, location: str = "", site: str = "indeed.com") -> List[Dict]:
        """Fetch jobs using Google Custom Search for major job boards"""
        jobs = []
        if not self.google_api_key or not self.google_cse_id:
            return jobs
        
        try:
            client = await self.get_client()
            search_query = f"{query} {location} site:{site}"
            
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cse_id,
                    "q": search_query,
                    "num": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    url = item.get("link", "")
                    title = item.get("title", "").split(" - ")[0]
                    
                    # Extract company from pagemap
                    company = ""
                    pagemap = item.get("pagemap", {})
                    if pagemap.get("organization"):
                        company = pagemap["organization"][0].get("name", "")
                    
                    # Determine source from site
                    source_name = site.split(".")[0].title()
                    
                    jobs.append({
                        "id": self._generate_job_id(url),
                        "title": title[:100],
                        "company": company[:50] if company else "Unknown",
                        "location": location or "Various",
                        "description": item.get("snippet", "")[:500],
                        "url": url,
                        "tags": query.split()[:5],
                        "source": f"Google ({source_name})",
                        "source_logo": f"https://{site}/favicon.ico",
                        "posted_at": "",
                        "freshness": {"badge": "Recently", "is_fresh": True, "minutes_ago": None},
                        "verified": False,  # Needs liveness check
                        "industry": "Various"
                    })
        except Exception as e:
            logger.error(f"Google CSE error for {site}: {e}")
        return jobs
    
    # ============== BioSpace (Biotech/Pharma) ==============
    async def fetch_biospace(self, query: str = "") -> List[Dict]:
        """Fetch jobs from BioSpace - Biotech & Pharma focus"""
        jobs = []
        try:
            client = await self.get_client()
            search_query = query if query else "biotech pharmaceutical"
            
            # BioSpace RSS feed
            response = await client.get(
                f"https://www.biospace.com/jobs/rss?keywords={search_query.replace(' ', '+')}",
                headers={"User-Agent": "MedMatch/2.0"}
            )
            
            if response.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                for item in items[:20]:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    
                    if title_match and link_match:
                        title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                        url = link_match.group(1).strip()
                        desc = re.sub(r'<[^>]+>', '', desc_match.group(1))[:500] if desc_match else ""
                        posted = pub_match.group(1) if pub_match else ""
                        freshness = self._calculate_freshness(posted)
                        
                        jobs.append({
                            "id": self._generate_job_id(url),
                            "title": title[:100],
                            "company": "",
                            "location": "Various",
                            "description": desc,
                            "url": url,
                            "tags": ["Biotech", "Pharma"],
                            "source": "BioSpace",
                            "source_logo": "https://www.biospace.com/favicon.ico",
                            "posted_at": posted,
                            "freshness": freshness,
                            "verified": True,
                            "industry": "Biotech & Pharma"
                        })
        except Exception as e:
            logger.error(f"BioSpace error: {e}")
        return jobs
    
    # ============== PharmiWeb (Pharma & Life Sciences) ==============
    async def fetch_pharmiweb(self, query: str = "") -> List[Dict]:
        """Fetch jobs from PharmiWeb - Pharma & Life Sciences"""
        jobs = []
        try:
            client = await self.get_client()
            search_query = query if query else "pharmaceutical"
            
            response = await client.get(
                f"https://www.pharmiweb.com/jobs/rss?keywords={search_query.replace(' ', '+')}",
                headers={"User-Agent": "MedMatch/2.0"}
            )
            
            if response.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                for item in items[:20]:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    
                    if title_match and link_match:
                        title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                        url = link_match.group(1).strip()
                        desc = re.sub(r'<[^>]+>', '', desc_match.group(1))[:500] if desc_match else ""
                        posted = pub_match.group(1) if pub_match else ""
                        freshness = self._calculate_freshness(posted)
                        
                        jobs.append({
                            "id": self._generate_job_id(url),
                            "title": title[:100],
                            "company": "",
                            "location": "Various",
                            "description": desc,
                            "url": url,
                            "tags": ["Pharma", "Life Sciences"],
                            "source": "PharmiWeb",
                            "source_logo": "https://www.pharmiweb.com/favicon.ico",
                            "posted_at": posted,
                            "freshness": freshness,
                            "verified": True,
                            "industry": "Pharma & Life Sciences"
                        })
        except Exception as e:
            logger.error(f"PharmiWeb error: {e}")
        return jobs
    
    # ============== Health eCareers (Clinical Healthcare) ==============
    async def fetch_healthecareers(self, query: str = "") -> List[Dict]:
        """Fetch jobs from Health eCareers - Clinical Healthcare"""
        jobs = []
        try:
            client = await self.get_client()
            search_query = query if query else "healthcare clinical"
            
            response = await client.get(
                f"https://www.healthecareers.com/rss/jobs?q={search_query.replace(' ', '+')}",
                headers={"User-Agent": "MedMatch/2.0"}
            )
            
            if response.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                for item in items[:20]:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    
                    if title_match and link_match:
                        title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                        url = link_match.group(1).strip()
                        desc = re.sub(r'<[^>]+>', '', desc_match.group(1))[:500] if desc_match else ""
                        posted = pub_match.group(1) if pub_match else ""
                        freshness = self._calculate_freshness(posted)
                        
                        jobs.append({
                            "id": self._generate_job_id(url),
                            "title": title[:100],
                            "company": "",
                            "location": "Various",
                            "description": desc,
                            "url": url,
                            "tags": ["Healthcare", "Clinical"],
                            "source": "HealtheCareers",
                            "source_logo": "https://www.healthecareers.com/favicon.ico",
                            "posted_at": posted,
                            "freshness": freshness,
                            "verified": True,
                            "industry": "Healthcare"
                        })
        except Exception as e:
            logger.error(f"HealtheCareers error: {e}")
        return jobs
    
    # ============== MedDevice Jobs (Medical Devices) ==============
    async def fetch_meddevicejobs(self, query: str = "") -> List[Dict]:
        """Fetch jobs from MedDeviceJobs - Medical Device industry"""
        jobs = []
        try:
            client = await self.get_client()
            search_query = query if query else "medical device"
            
            response = await client.get(
                f"https://www.meddevicejobs.com/rss?keywords={search_query.replace(' ', '+')}",
                headers={"User-Agent": "MedMatch/2.0"}
            )
            
            if response.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                for item in items[:20]:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    
                    if title_match and link_match:
                        title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                        url = link_match.group(1).strip()
                        desc = re.sub(r'<[^>]+>', '', desc_match.group(1))[:500] if desc_match else ""
                        posted = pub_match.group(1) if pub_match else ""
                        freshness = self._calculate_freshness(posted)
                        
                        jobs.append({
                            "id": self._generate_job_id(url),
                            "title": title[:100],
                            "company": "",
                            "location": "Various",
                            "description": desc,
                            "url": url,
                            "tags": ["Medical Device", "MedTech"],
                            "source": "MedDeviceJobs",
                            "source_logo": "https://www.meddevicejobs.com/favicon.ico",
                            "posted_at": posted,
                            "freshness": freshness,
                            "verified": True,
                            "industry": "Medical Devices"
                        })
        except Exception as e:
            logger.error(f"MedDeviceJobs error: {e}")
        return jobs
    
    # ============== Comprehensive Search ==============
    async def search_all_sources(
        self, 
        query: str = "",
        location: str = "",
        industries: List[str] = None,
        limit_per_source: int = 15
    ) -> List[Dict]:
        """
        Search all job sources in parallel and aggregate results.
        """
        all_jobs = []
        tasks = []
        
        # Always fetch from remote job boards
        tasks.append(self.fetch_remoteok(query))
        tasks.append(self.fetch_remotive(query))
        tasks.append(self.fetch_weworkremotely(query))
        tasks.append(self.fetch_himalayas(query))
        tasks.append(self.fetch_arbeitnow(query))
        tasks.append(self.fetch_jobicy(query))
        
        # Industry-specific boards
        if not industries or "pharma" in industries or "biotech" in industries:
            tasks.append(self.fetch_biospace(query))
            tasks.append(self.fetch_pharmiweb(query))
        
        if not industries or "healthcare" in industries:
            tasks.append(self.fetch_healthecareers(query))
        
        if not industries or "medical_device" in industries:
            tasks.append(self.fetch_meddevicejobs(query))
        
        if not industries or "government" in industries:
            tasks.append(self.fetch_usajobs(query, location))
        
        # Google CSE for major boards
        if self.google_api_key and self.google_cse_id:
            for site in ["indeed.com/viewjob", "linkedin.com/jobs", "glassdoor.com/job-listing"]:
                tasks.append(self.fetch_google_cse(query, location, site))
        
        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result[:limit_per_source])
        
        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Clean text fields
                job["title"] = self._clean_text(job.get("title", ""))
                job["company"] = self._clean_text(job.get("company", ""))
                job["description"] = self._clean_text(job.get("description", ""))
                unique_jobs.append(job)
            elif not url:
                job["title"] = self._clean_text(job.get("title", ""))
                job["company"] = self._clean_text(job.get("company", ""))
                job["description"] = self._clean_text(job.get("description", ""))
                unique_jobs.append(job)
        
        # Sort by freshness (fresh jobs first)
        unique_jobs.sort(
            key=lambda x: (
                not x.get("freshness", {}).get("is_fresh", False),
                x.get("freshness", {}).get("minutes_ago") or 999999
            )
        )
        
        return unique_jobs
    
    def get_available_sources(self) -> List[Dict]:
        """Get list of available job sources with their status"""
        sources = []
        for key, board in JOB_BOARDS.items():
            sources.append({
                "id": key,
                "name": board["name"],
                "focus": board["focus"],
                "active": board["active"]
            })
        return sources


# Singleton instance
_job_sources_service = None

def get_job_sources_service(google_api_key: str = None, google_cse_id: str = None) -> JobSourcesService:
    global _job_sources_service
    if _job_sources_service is None:
        _job_sources_service = JobSourcesService(google_api_key, google_cse_id)
    return _job_sources_service
