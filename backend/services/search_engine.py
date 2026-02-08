"""
Enhanced Search Engine Service
Implements advanced search features:
- Fuzzy matching for typo handling
- Autocomplete suggestions
- Spell correction
- Synonym mapping
- Semantic search with NLP
- CTR tracking for algorithm refinement
- Performance optimizations
"""
import os
import re
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
from bson import ObjectId

# Fuzzy matching library
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logging.warning("rapidfuzz not installed, falling back to basic fuzzy matching")

# Database connection
from utils.db import get_database

logger = logging.getLogger(__name__)


# ============== Synonym Mapping ==============
SYNONYM_MAP = {
    # Job titles
    "engineer": ["developer", "programmer", "coder", "technician"],
    "developer": ["engineer", "programmer", "coder", "software engineer"],
    "manager": ["lead", "supervisor", "director", "head"],
    "analyst": ["specialist", "consultant", "advisor"],
    "scientist": ["researcher", "investigator", "specialist"],
    
    # Industries
    "biotech": ["biotechnology", "life sciences", "pharma", "pharmaceutical"],
    "pharma": ["pharmaceutical", "biotech", "drug", "medicine"],
    "medical": ["healthcare", "clinical", "health"],
    "quality": ["qa", "qc", "quality assurance", "quality control"],
    
    # Skills
    "python": ["py", "python3"],
    "javascript": ["js", "nodejs", "node.js"],
    "react": ["reactjs", "react.js"],
    
    # Locations
    "remote": ["work from home", "wfh", "virtual", "telecommute"],
    "nyc": ["new york", "new york city", "manhattan"],
    "sf": ["san francisco", "bay area"],
    "la": ["los angeles"],
}

# Common typos and corrections
COMMON_TYPOS = {
    "enginer": "engineer",
    "developr": "developer",
    "managr": "manager",
    "analist": "analyst",
    "qualtiy": "quality",
    "suply": "supply",
    "supplyer": "supplier",
    "manufcturing": "manufacturing",
    "pharmceutical": "pharmaceutical",
    "biotechnolgy": "biotechnology",
    "reserch": "research",
    "sceintist": "scientist",
}


class SearchEngineService:
    """Enhanced search engine with fuzzy matching, autocomplete, and semantic search"""
    
    def __init__(self):
        self.db = get_database()
        self.search_history = defaultdict(list)
        self.popular_searches = []
        self.ctr_data = defaultdict(lambda: {"impressions": 0, "clicks": 0})
        
    # ============== Spell Correction ==============
    
    def correct_spelling(self, query: str) -> Tuple[str, bool]:
        """
        Correct common spelling mistakes in search queries
        Returns: (corrected_query, was_corrected)
        """
        words = query.lower().split()
        corrected_words = []
        was_corrected = False
        
        for word in words:
            if word in COMMON_TYPOS:
                corrected_words.append(COMMON_TYPOS[word])
                was_corrected = True
            else:
                # Check for close matches in common typos
                for typo, correction in COMMON_TYPOS.items():
                    if self._similarity(word, typo) > 0.85:
                        corrected_words.append(correction)
                        was_corrected = True
                        break
                else:
                    corrected_words.append(word)
        
        return " ".join(corrected_words), was_corrected
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        if RAPIDFUZZ_AVAILABLE:
            return fuzz.ratio(a, b) / 100
        return SequenceMatcher(None, a, b).ratio()
    
    # ============== Fuzzy Matching ==============
    
    def fuzzy_match(self, query: str, candidates: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
        """
        Find fuzzy matches for a query in a list of candidates
        Returns: List of (match, score) tuples sorted by score
        """
        if RAPIDFUZZ_AVAILABLE:
            results = process.extract(query, candidates, scorer=fuzz.WRatio, limit=20)
            return [(match, score/100) for match, score, _ in results if score/100 >= threshold]
        
        # Fallback to basic matching
        matches = []
        for candidate in candidates:
            score = self._similarity(query.lower(), candidate.lower())
            if score >= threshold:
                matches.append((candidate, score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)[:20]
    
    # ============== Synonym Expansion ==============
    
    def expand_synonyms(self, query: str) -> List[str]:
        """
        Expand query with synonyms for broader search
        Returns: List of expanded query variations
        """
        words = query.lower().split()
        expanded = [query]
        
        for i, word in enumerate(words):
            if word in SYNONYM_MAP:
                for synonym in SYNONYM_MAP[word]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    expanded.append(" ".join(new_words))
        
        return list(set(expanded))
    
    # ============== Autocomplete ==============
    
    async def get_autocomplete_suggestions(
        self, 
        partial_query: str, 
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get autocomplete suggestions based on:
        1. Popular searches
        2. User's search history
        3. Job titles in database
        4. Fuzzy matches
        """
        suggestions = []
        partial_lower = partial_query.lower()
        
        # 1. Check popular searches first
        for search in self.popular_searches:
            if search.lower().startswith(partial_lower):
                suggestions.append({
                    "text": search,
                    "type": "popular",
                    "score": 1.0
                })
        
        # 2. Check user's search history
        if user_id and user_id in self.search_history:
            for search in self.search_history[user_id][-20:]:
                if search.lower().startswith(partial_lower):
                    suggestions.append({
                        "text": search,
                        "type": "history",
                        "score": 0.9
                    })
        
        # 3. Get job titles from database
        try:
            jobs_collection = self.db.jobs
            pipeline = [
                {"$match": {"title": {"$regex": f"^{re.escape(partial_query)}", "$options": "i"}}},
                {"$group": {"_id": "$title"}},
                {"$limit": 20}
            ]
            async for doc in jobs_collection.aggregate(pipeline):
                suggestions.append({
                    "text": doc["_id"],
                    "type": "job_title",
                    "score": 0.8
                })
        except Exception as e:
            logger.error(f"Error fetching job titles: {e}")
        
        # 4. Add fuzzy matches for common job titles
        common_titles = [
            "Software Engineer", "Quality Engineer", "Data Scientist",
            "Product Manager", "Supplier Quality Manager", "Research Scientist",
            "Manufacturing Engineer", "Clinical Research Associate", "Biotech Analyst",
            "Regulatory Affairs Specialist", "Medical Device Engineer"
        ]
        
        fuzzy_matches = self.fuzzy_match(partial_query, common_titles, threshold=0.5)
        for match, score in fuzzy_matches:
            suggestions.append({
                "text": match,
                "type": "suggested",
                "score": score * 0.7
            })
        
        # Deduplicate and sort by score
        seen = set()
        unique_suggestions = []
        for s in sorted(suggestions, key=lambda x: x["score"], reverse=True):
            if s["text"].lower() not in seen:
                seen.add(s["text"].lower())
                unique_suggestions.append(s)
        
        return unique_suggestions[:limit]
    
    # ============== Semantic Search ==============
    
    def extract_search_intent(self, query: str) -> Dict:
        """
        Extract search intent using basic NLP
        Returns: Dict with intent type and extracted entities
        """
        query_lower = query.lower()
        
        intent = {
            "type": "job_search",  # default
            "job_title": None,
            "location": None,
            "job_type": None,
            "experience_level": None,
            "salary_range": None,
            "keywords": []
        }
        
        # Detect location
        location_patterns = [
            r"in\s+([a-zA-Z\s]+?)(?:\s+area|\s+region|$)",
            r"near\s+([a-zA-Z\s]+)",
            r"at\s+([a-zA-Z\s]+)",
        ]
        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                intent["location"] = match.group(1).strip()
                break
        
        # Detect job type
        if any(word in query_lower for word in ["remote", "work from home", "wfh", "virtual"]):
            intent["job_type"] = "remote"
        elif "hybrid" in query_lower:
            intent["job_type"] = "hybrid"
        elif any(word in query_lower for word in ["on-site", "onsite", "in-office"]):
            intent["job_type"] = "onsite"
        
        # Detect experience level
        if any(word in query_lower for word in ["senior", "sr.", "lead", "principal"]):
            intent["experience_level"] = "senior"
        elif any(word in query_lower for word in ["junior", "jr.", "entry", "associate"]):
            intent["experience_level"] = "entry"
        elif any(word in query_lower for word in ["mid", "intermediate"]):
            intent["experience_level"] = "mid"
        
        # Detect salary expectations
        salary_match = re.search(r"\$?(\d{2,3})k?(?:\s*-\s*\$?(\d{2,3})k?)?", query_lower)
        if salary_match:
            min_salary = int(salary_match.group(1)) * 1000
            max_salary = int(salary_match.group(2)) * 1000 if salary_match.group(2) else min_salary * 1.5
            intent["salary_range"] = {"min": min_salary, "max": max_salary}
        
        # Extract job title (words that aren't location/modifiers)
        stop_words = {"in", "at", "near", "for", "with", "and", "or", "the", "a", "an", 
                      "remote", "hybrid", "onsite", "senior", "junior", "entry", "mid",
                      "job", "jobs", "position", "positions", "role", "roles", "work",
                      "looking", "find", "search", "interested"}
        
        words = query_lower.split()
        title_words = [w for w in words if w not in stop_words and not w.startswith("$")]
        
        if title_words:
            intent["job_title"] = " ".join(title_words[:4])  # Max 4 words for job title
            intent["keywords"] = title_words
        
        return intent
    
    # ============== CTR Tracking ==============
    
    async def track_impression(self, query: str, result_ids: List[str]):
        """Track impressions for search results"""
        for result_id in result_ids:
            key = f"{query}:{result_id}"
            self.ctr_data[key]["impressions"] += 1
        
        # Persist to database periodically
        try:
            await self.db.search_analytics.update_one(
                {"query": query.lower(), "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                {"$inc": {"impressions": len(result_ids)}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error tracking impression: {e}")
    
    async def track_click(self, query: str, result_id: str, position: int):
        """Track click on a search result"""
        key = f"{query}:{result_id}"
        self.ctr_data[key]["clicks"] += 1
        
        try:
            await self.db.search_analytics.update_one(
                {"query": query.lower(), "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                {
                    "$inc": {"clicks": 1},
                    "$push": {"click_positions": position}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error tracking click: {e}")
    
    def get_ctr_boost(self, query: str, result_id: str) -> float:
        """
        Calculate CTR-based boost for a result
        Higher CTR = higher boost
        """
        key = f"{query}:{result_id}"
        data = self.ctr_data[key]
        
        if data["impressions"] < 10:
            return 1.0  # Not enough data
        
        ctr = data["clicks"] / data["impressions"]
        
        # Boost based on CTR (1.0 to 1.5 range)
        return 1.0 + min(ctr * 2, 0.5)
    
    # ============== Search History ==============
    
    def add_to_search_history(self, user_id: str, query: str):
        """Add query to user's search history"""
        if query not in self.search_history[user_id]:
            self.search_history[user_id].append(query)
            # Keep only last 100 searches
            if len(self.search_history[user_id]) > 100:
                self.search_history[user_id] = self.search_history[user_id][-100:]
    
    def update_popular_searches(self, query: str):
        """Update popular searches list"""
        if query not in self.popular_searches:
            self.popular_searches.append(query)
        
        # Sort by frequency and keep top 50
        # In production, this would be calculated from database
        if len(self.popular_searches) > 50:
            self.popular_searches = self.popular_searches[-50:]
    
    # ============== Enhanced Search ==============
    
    async def enhanced_search(
        self,
        query: str,
        user_id: Optional[str] = None,
        filters: Optional[Dict] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """
        Perform enhanced search with all optimizations:
        1. Spell correction
        2. Synonym expansion
        3. Fuzzy matching
        4. Semantic intent extraction
        5. CTR-based ranking
        """
        start_time = datetime.now(timezone.utc)
        
        # Step 1: Spell correction
        corrected_query, was_corrected = self.correct_spelling(query)
        
        # Step 2: Extract search intent
        intent = self.extract_search_intent(corrected_query)
        
        # Step 3: Expand with synonyms
        expanded_queries = self.expand_synonyms(corrected_query)
        
        # Step 4: Build search criteria
        search_criteria = self._build_search_criteria(intent, filters)
        
        # Step 5: Execute search
        results = await self._execute_search(search_criteria, expanded_queries, page, limit)
        
        # Step 6: Apply CTR boost
        for result in results:
            result["_score"] *= self.get_ctr_boost(query, str(result.get("_id", "")))
        
        # Sort by score
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        
        # Step 7: Track metrics
        if user_id:
            self.add_to_search_history(user_id, query)
        self.update_popular_searches(query)
        
        # Calculate response time
        end_time = datetime.now(timezone.utc)
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return {
            "query": query,
            "corrected_query": corrected_query if was_corrected else None,
            "intent": intent,
            "results": results,
            "total": len(results),
            "page": page,
            "limit": limit,
            "response_time_ms": round(response_time_ms, 2),
            "expanded_queries": expanded_queries[:3]  # Show top 3 expansions
        }
    
    def _build_search_criteria(self, intent: Dict, filters: Optional[Dict]) -> Dict:
        """Build MongoDB search criteria from intent and filters"""
        criteria = {}
        
        if intent.get("job_title"):
            criteria["$or"] = [
                {"title": {"$regex": intent["job_title"], "$options": "i"}},
                {"description": {"$regex": intent["job_title"], "$options": "i"}}
            ]
        
        if intent.get("location"):
            criteria["location"] = {"$regex": intent["location"], "$options": "i"}
        
        if intent.get("job_type"):
            criteria["job_type"] = intent["job_type"]
        
        if intent.get("experience_level"):
            criteria["experience_level"] = intent["experience_level"]
        
        # Apply additional filters
        if filters:
            if filters.get("salary_min"):
                criteria["salary_min"] = {"$gte": filters["salary_min"]}
            if filters.get("salary_max"):
                criteria["salary_max"] = {"$lte": filters["salary_max"]}
            if filters.get("company"):
                criteria["company"] = {"$regex": filters["company"], "$options": "i"}
        
        return criteria
    
    async def _execute_search(
        self, 
        criteria: Dict, 
        expanded_queries: List[str],
        page: int,
        limit: int
    ) -> List[Dict]:
        """Execute search against database"""
        results = []
        skip = (page - 1) * limit
        
        try:
            jobs_collection = self.db.jobs
            
            # If no criteria, return recent jobs
            if not criteria:
                async for job in jobs_collection.find().sort("posted_date", -1).skip(skip).limit(limit):
                    job["_id"] = str(job["_id"])
                    job["_score"] = 50  # Base score
                    results.append(job)
            else:
                async for job in jobs_collection.find(criteria).skip(skip).limit(limit):
                    job["_id"] = str(job["_id"])
                    job["_score"] = self._calculate_relevance_score(job, expanded_queries)
                    results.append(job)
        
        except Exception as e:
            logger.error(f"Search execution error: {e}")
        
        return results
    
    def _calculate_relevance_score(self, job: Dict, queries: List[str]) -> float:
        """Calculate relevance score for a job based on queries"""
        score = 50  # Base score
        
        job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}".lower()
        
        for query in queries:
            for word in query.lower().split():
                if word in job_text:
                    score += 10
                    if word in job.get('title', '').lower():
                        score += 15  # Title match is more important
        
        return min(score, 100)


# Singleton instance
_search_service = None

def get_search_service() -> SearchEngineService:
    """Get singleton search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchEngineService()
    return _search_service
