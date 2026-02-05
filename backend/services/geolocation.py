"""
Geolocation & Geofencing Service for MedMatch AI
Provides location-based job matching and proximity alerts.

Features:
- Haversine distance calculation (server-side, no API calls)
- User location preferences (home coordinates, preferred radius)
- Proximity-based job matching
- Geofence triggers for hybrid/onsite jobs
- Drive time estimates integration (optional)
"""
import math
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from utils.database import db

logger = logging.getLogger(__name__)

# Default radius settings by job type (in miles)
DEFAULT_RADIUS_SETTINGS = {
    "remote": None,  # No radius for remote jobs
    "hybrid": 30,    # 30 miles for hybrid
    "onsite": 25,    # 25 miles for onsite
    "clinical": 15,  # 15 miles for clinical healthcare
    "manufacturing": 20,  # 20 miles for manufacturing/pharma
}

# Major tech/healthcare hub coordinates for context
MAJOR_HUBS = {
    "san_francisco": {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco Bay Area"},
    "boston": {"lat": 42.3601, "lon": -71.0589, "name": "Boston/Cambridge (Biotech)"},
    "new_york": {"lat": 40.7128, "lon": -74.0060, "name": "New York City"},
    "san_diego": {"lat": 32.7157, "lon": -117.1611, "name": "San Diego (Biotech)"},
    "research_triangle": {"lat": 35.8992, "lon": -78.8644, "name": "Research Triangle, NC"},
    "minneapolis": {"lat": 44.9778, "lon": -93.2650, "name": "Minneapolis (Med Device)"},
    "los_angeles": {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles"},
    "chicago": {"lat": 41.8781, "lon": -87.6298, "name": "Chicago"},
    "seattle": {"lat": 47.6062, "lon": -122.3321, "name": "Seattle"},
    "austin": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
    "denver": {"lat": 39.7392, "lon": -104.9903, "name": "Denver"},
    "philadelphia": {"lat": 39.9526, "lon": -75.1652, "name": "Philadelphia (Pharma)"},
    "new_jersey": {"lat": 40.0583, "lon": -74.4057, "name": "New Jersey (Pharma Corridor)"},
    "indianapolis": {"lat": 39.7684, "lon": -86.1581, "name": "Indianapolis (Pharma)"},
    "houston": {"lat": 29.7604, "lon": -95.3698, "name": "Houston (Medical Center)"},
}


class GeolocationService:
    """
    Service for location-based job matching and geofencing.
    """
    
    def __init__(self):
        self.earth_radius_miles = 3958.8  # Earth's radius in miles
        self.earth_radius_km = 6371.0     # Earth's radius in kilometers
    
    def haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: str = "miles"
    ) -> float:
        """
        Calculate the great-circle distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates (user location)
            lat2, lon2: Second point coordinates (job location)
            unit: "miles" or "km"
        
        Returns:
            Distance in specified unit
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Calculate distance
        if unit == "km":
            return self.earth_radius_km * c
        return self.earth_radius_miles * c
    
    def is_within_radius(
        self,
        user_lat: float,
        user_lon: float,
        job_lat: float,
        job_lon: float,
        radius_miles: float
    ) -> Tuple[bool, float]:
        """
        Check if a job is within the user's preferred radius.
        
        Returns:
            Tuple of (is_within, actual_distance)
        """
        distance = self.haversine_distance(user_lat, user_lon, job_lat, job_lon)
        return (distance <= radius_miles, round(distance, 1))
    
    def get_nearest_hub(self, lat: float, lon: float) -> Dict:
        """
        Find the nearest major tech/healthcare hub to a location.
        """
        nearest = None
        min_distance = float('inf')
        
        for hub_id, hub in MAJOR_HUBS.items():
            distance = self.haversine_distance(lat, lon, hub["lat"], hub["lon"])
            if distance < min_distance:
                min_distance = distance
                nearest = {
                    "hub_id": hub_id,
                    "name": hub["name"],
                    "distance_miles": round(distance, 1)
                }
        
        return nearest
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Convert an address to coordinates.
        Note: In production, use Google Geocoding API or similar.
        This is a simplified version using common city mappings.
        """
        # Simplified geocoding for common cities
        address_lower = address.lower()
        
        city_coords = {
            "san francisco": {"lat": 37.7749, "lon": -122.4194},
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "los angeles": {"lat": 34.0522, "lon": -118.2437},
            "chicago": {"lat": 41.8781, "lon": -87.6298},
            "boston": {"lat": 42.3601, "lon": -71.0589},
            "seattle": {"lat": 47.6062, "lon": -122.3321},
            "austin": {"lat": 30.2672, "lon": -97.7431},
            "denver": {"lat": 39.7392, "lon": -104.9903},
            "san diego": {"lat": 32.7157, "lon": -117.1611},
            "philadelphia": {"lat": 39.9526, "lon": -75.1652},
            "houston": {"lat": 29.7604, "lon": -95.3698},
            "phoenix": {"lat": 33.4484, "lon": -112.0740},
            "dallas": {"lat": 32.7767, "lon": -96.7970},
            "san jose": {"lat": 37.3382, "lon": -121.8863},
            "minneapolis": {"lat": 44.9778, "lon": -93.2650},
            "atlanta": {"lat": 33.7490, "lon": -84.3880},
            "miami": {"lat": 25.7617, "lon": -80.1918},
            "raleigh": {"lat": 35.7796, "lon": -78.6382},
            "remote": None,  # No coordinates for remote
        }
        
        for city, coords in city_coords.items():
            if city in address_lower:
                if coords:
                    return {"address": address, **coords, "source": "city_mapping"}
                return None
        
        return None
    
    async def save_user_location_preferences(
        self,
        user_id: str,
        home_lat: float = None,
        home_lon: float = None,
        home_address: str = None,
        preferred_radius_miles: int = 25,
        commute_preference: str = "driving",  # driving, transit, walking
        location_alerts_enabled: bool = True,
        preferred_work_types: List[str] = None  # ["remote", "hybrid", "onsite"]
    ) -> Dict:
        """
        Save user's location preferences for job matching.
        """
        preferences = {
            "home_coordinates": {
                "lat": home_lat,
                "lon": home_lon,
                "address": home_address
            } if home_lat and home_lon else None,
            "preferred_radius_miles": preferred_radius_miles,
            "commute_preference": commute_preference,
            "location_alerts_enabled": location_alerts_enabled,
            "preferred_work_types": preferred_work_types or ["remote", "hybrid", "onsite"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"location_preferences": preferences}}
            )
            
            return {"success": True, "preferences": preferences}
        except Exception as e:
            logger.error(f"Failed to save location preferences: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_location_preferences(self, user_id: str) -> Optional[Dict]:
        """
        Get user's location preferences.
        """
        try:
            user = await db.users.find_one(
                {"user_id": user_id},
                {"_id": 0, "location_preferences": 1}
            )
            
            if user and user.get("location_preferences"):
                return user["location_preferences"]
            
            # Return defaults
            return {
                "home_coordinates": None,
                "preferred_radius_miles": 25,
                "commute_preference": "driving",
                "location_alerts_enabled": True,
                "preferred_work_types": ["remote", "hybrid", "onsite"]
            }
        except Exception as e:
            logger.error(f"Failed to get location preferences: {e}")
            return None
    
    async def match_jobs_by_location(
        self,
        user_id: str,
        jobs: List[Dict]
    ) -> List[Dict]:
        """
        Filter and score jobs based on user's location preferences.
        """
        preferences = await self.get_user_location_preferences(user_id)
        
        if not preferences:
            return jobs
        
        home = preferences.get("home_coordinates")
        radius = preferences.get("preferred_radius_miles", 25)
        work_types = preferences.get("preferred_work_types", ["remote", "hybrid", "onsite"])
        
        matched_jobs = []
        
        for job in jobs:
            # Check work type preference
            job_work_type = self._detect_work_type(job)
            
            if job_work_type not in work_types:
                continue
            
            # Remote jobs always match
            if job_work_type == "remote":
                job["distance_miles"] = None
                job["within_radius"] = True
                job["work_type"] = "Remote"
                matched_jobs.append(job)
                continue
            
            # For hybrid/onsite, check distance if we have coordinates
            if home and home.get("lat") and home.get("lon"):
                job_coords = await self._get_job_coordinates(job)
                
                if job_coords:
                    within, distance = self.is_within_radius(
                        home["lat"], home["lon"],
                        job_coords["lat"], job_coords["lon"],
                        radius
                    )
                    
                    job["distance_miles"] = distance
                    job["within_radius"] = within
                    job["work_type"] = job_work_type.title()
                    
                    if within:
                        # Boost match score based on proximity
                        current_score = job.get("match_score", 50)
                        proximity_boost = max(0, (radius - distance) / radius * 10)
                        job["match_score"] = min(100, current_score + proximity_boost)
                        job["proximity_badge"] = f"{distance:.1f} mi away"
                        matched_jobs.append(job)
                else:
                    # No coordinates, include with location info
                    job["distance_miles"] = None
                    job["within_radius"] = None
                    job["work_type"] = job_work_type.title()
                    matched_jobs.append(job)
            else:
                # No home coordinates set, include all
                job["work_type"] = job_work_type.title()
                matched_jobs.append(job)
        
        # Sort by distance (closest first), then by match score
        matched_jobs.sort(key=lambda x: (
            x.get("distance_miles") or 999999,
            -x.get("match_score", 0)
        ))
        
        return matched_jobs
    
    def _detect_work_type(self, job: Dict) -> str:
        """
        Detect if a job is remote, hybrid, or onsite.
        """
        location = (job.get("location", "") or "").lower()
        title = (job.get("title", "") or "").lower()
        description = (job.get("description", "") or "").lower()
        
        text = f"{location} {title} {description}"
        
        if any(kw in text for kw in ["remote", "work from home", "wfh", "anywhere", "distributed"]):
            return "remote"
        elif any(kw in text for kw in ["hybrid", "flexible", "partial remote", "2-3 days"]):
            return "hybrid"
        else:
            return "onsite"
    
    async def _get_job_coordinates(self, job: Dict) -> Optional[Dict]:
        """
        Get coordinates for a job location.
        """
        location = job.get("location", "")
        
        if not location or location.lower() in ["remote", "anywhere", "worldwide"]:
            return None
        
        # Try to geocode the location
        coords = await self.geocode_address(location)
        return coords
    
    async def check_proximity_alerts(
        self,
        user_id: str,
        new_jobs: List[Dict]
    ) -> List[Dict]:
        """
        Check if any new jobs trigger proximity alerts.
        Returns list of jobs that should generate notifications.
        """
        preferences = await self.get_user_location_preferences(user_id)
        
        if not preferences or not preferences.get("location_alerts_enabled"):
            return []
        
        home = preferences.get("home_coordinates")
        if not home or not home.get("lat"):
            return []
        
        radius = preferences.get("preferred_radius_miles", 25)
        alert_jobs = []
        
        for job in new_jobs:
            # Skip remote jobs for proximity alerts
            work_type = self._detect_work_type(job)
            if work_type == "remote":
                continue
            
            job_coords = await self._get_job_coordinates(job)
            if not job_coords:
                continue
            
            within, distance = self.is_within_radius(
                home["lat"], home["lon"],
                job_coords["lat"], job_coords["lon"],
                radius
            )
            
            if within:
                job["distance_miles"] = distance
                job["alert_type"] = "proximity"
                job["alert_message"] = f"New {work_type} job {distance:.1f} miles from you!"
                alert_jobs.append(job)
        
        return alert_jobs
    
    def calculate_commute_estimate(
        self,
        distance_miles: float,
        mode: str = "driving"
    ) -> Dict:
        """
        Estimate commute time based on distance and mode.
        Note: This is a rough estimate. For accurate times, use Google Distance Matrix API.
        """
        # Average speeds by mode (mph)
        avg_speeds = {
            "driving": 25,       # City driving with traffic
            "driving_highway": 45,  # Highway commute
            "transit": 15,       # Public transit
            "walking": 3,        # Walking
            "cycling": 12        # Cycling
        }
        
        speed = avg_speeds.get(mode, 25)
        time_hours = distance_miles / speed
        time_minutes = int(time_hours * 60)
        
        # Add buffer for traffic/delays
        traffic_factor = 1.3 if mode == "driving" else 1.2
        time_with_traffic = int(time_minutes * traffic_factor)
        
        return {
            "distance_miles": round(distance_miles, 1),
            "mode": mode,
            "estimated_minutes": time_minutes,
            "with_traffic_minutes": time_with_traffic,
            "display": f"{time_with_traffic} min {mode}"
        }
    
    async def get_jobs_near_hub(
        self,
        hub_id: str,
        jobs: List[Dict],
        radius_miles: float = 50
    ) -> List[Dict]:
        """
        Get jobs near a specific tech/healthcare hub.
        """
        if hub_id not in MAJOR_HUBS:
            return []
        
        hub = MAJOR_HUBS[hub_id]
        hub_lat, hub_lon = hub["lat"], hub["lon"]
        
        nearby_jobs = []
        
        for job in jobs:
            job_coords = await self._get_job_coordinates(job)
            if not job_coords:
                continue
            
            within, distance = self.is_within_radius(
                hub_lat, hub_lon,
                job_coords["lat"], job_coords["lon"],
                radius_miles
            )
            
            if within:
                job["distance_from_hub"] = distance
                job["hub_name"] = hub["name"]
                nearby_jobs.append(job)
        
        return nearby_jobs


# Singleton instance
_geolocation_service = None

def get_geolocation_service() -> GeolocationService:
    global _geolocation_service
    if _geolocation_service is None:
        _geolocation_service = GeolocationService()
    return _geolocation_service
