"""
Geolocation API Routes
Handles location preferences, proximity matching, and geofencing alerts.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

from routes.auth import get_current_user
from services.geolocation import get_geolocation_service, MAJOR_HUBS

router = APIRouter(prefix="/geolocation", tags=["Geolocation"])


class LocationPreferences(BaseModel):
    home_lat: Optional[float] = None
    home_lon: Optional[float] = None
    home_address: Optional[str] = None
    preferred_radius_miles: int = 25
    commute_preference: str = "driving"
    location_alerts_enabled: bool = True
    preferred_work_types: List[str] = ["remote", "hybrid", "onsite"]


class DistanceRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float


class GeocodeRequest(BaseModel):
    address: str


# ============== Location Preferences ==============

@router.get("/preferences")
async def get_location_preferences(request: Request):
    """Get user's location preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_geolocation_service()
    preferences = await service.get_user_location_preferences(user["user_id"])
    
    return preferences


@router.put("/preferences")
async def update_location_preferences(
    preferences: LocationPreferences,
    request: Request
):
    """Update user's location preferences"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_geolocation_service()
    result = await service.save_user_location_preferences(
        user_id=user["user_id"],
        home_lat=preferences.home_lat,
        home_lon=preferences.home_lon,
        home_address=preferences.home_address,
        preferred_radius_miles=preferences.preferred_radius_miles,
        commute_preference=preferences.commute_preference,
        location_alerts_enabled=preferences.location_alerts_enabled,
        preferred_work_types=preferences.preferred_work_types
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to save preferences"))
    
    return result


# ============== Distance Calculations ==============

@router.post("/distance")
async def calculate_distance(data: DistanceRequest, request: Request):
    """Calculate distance between two points"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_geolocation_service()
    
    distance_miles = service.haversine_distance(
        data.lat1, data.lon1,
        data.lat2, data.lon2,
        unit="miles"
    )
    
    distance_km = service.haversine_distance(
        data.lat1, data.lon1,
        data.lat2, data.lon2,
        unit="km"
    )
    
    # Get commute estimate
    commute = service.calculate_commute_estimate(distance_miles, "driving")
    
    return {
        "distance_miles": round(distance_miles, 2),
        "distance_km": round(distance_km, 2),
        "commute_estimate": commute
    }


@router.post("/geocode")
async def geocode_address(data: GeocodeRequest, request: Request):
    """Convert an address to coordinates"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = get_geolocation_service()
    coords = await service.geocode_address(data.address)
    
    if not coords:
        return {
            "found": False,
            "message": "Could not geocode address. Try a major city name."
        }
    
    return {
        "found": True,
        "coordinates": coords
    }


# ============== Hub Information ==============

@router.get("/hubs")
async def get_major_hubs(request: Request):
    """Get list of major tech/healthcare hubs"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    hubs = []
    for hub_id, hub in MAJOR_HUBS.items():
        hubs.append({
            "id": hub_id,
            "name": hub["name"],
            "lat": hub["lat"],
            "lon": hub["lon"]
        })
    
    return {"hubs": hubs, "total": len(hubs)}


@router.get("/nearest-hub")
async def get_nearest_hub(
    request: Request,
    lat: float = None,
    lon: float = None
):
    """Find the nearest major hub to a location"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not lat or not lon:
        # Try to use user's home location
        service = get_geolocation_service()
        prefs = await service.get_user_location_preferences(user["user_id"])
        
        if prefs and prefs.get("home_coordinates"):
            lat = prefs["home_coordinates"].get("lat")
            lon = prefs["home_coordinates"].get("lon")
        
        if not lat or not lon:
            raise HTTPException(
                status_code=400, 
                detail="Please provide lat/lon or set your home location in preferences"
            )
    
    service = get_geolocation_service()
    nearest = service.get_nearest_hub(lat, lon)
    
    return nearest


# ============== Commute Estimates ==============

@router.get("/commute-estimate")
async def get_commute_estimate(
    request: Request,
    distance_miles: float,
    mode: str = "driving"
):
    """Get estimated commute time for a distance"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    valid_modes = ["driving", "driving_highway", "transit", "walking", "cycling"]
    if mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    service = get_geolocation_service()
    estimate = service.calculate_commute_estimate(distance_miles, mode)
    
    return estimate


# ============== Radius Settings ==============

@router.get("/radius-settings")
async def get_radius_settings(request: Request):
    """Get default radius settings by job type"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "defaults": {
            "remote": {"radius": None, "description": "No distance limit for remote jobs"},
            "hybrid": {"radius": 30, "description": "30 miles for hybrid positions"},
            "onsite": {"radius": 25, "description": "25 miles for onsite positions"},
            "clinical": {"radius": 15, "description": "15 miles for clinical healthcare"},
            "manufacturing": {"radius": 20, "description": "20 miles for manufacturing/pharma"}
        },
        "recommended_radius_by_area": {
            "urban": 15,
            "suburban": 25,
            "rural": 50
        }
    }
