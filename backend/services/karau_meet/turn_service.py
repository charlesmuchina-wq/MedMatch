"""
AI KARAU Meeting - TURN Server Service
Fetches ICE servers from Xirsys for WebRTC NAT traversal
"""

import os
import logging
import aiohttp
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Xirsys credentials
XIRSYS_IDENT = os.environ.get("XIRSYS_IDENT", "")
XIRSYS_SECRET = os.environ.get("XIRSYS_SECRET", "")
XIRSYS_CHANNEL = os.environ.get("XIRSYS_CHANNEL", "default")

# Default STUN servers (free, no credentials needed)
DEFAULT_ICE_SERVERS = [
    {"urls": "stun:stun.l.google.com:19302"},
    {"urls": "stun:stun1.l.google.com:19302"},
    {"urls": "stun:stun2.l.google.com:19302"},
    {"urls": "stun:stun3.l.google.com:19302"},
    {"urls": "stun:stun4.l.google.com:19302"},
]


async def get_ice_servers() -> Dict:
    """
    Fetch ICE servers (STUN + TURN) for WebRTC
    
    Returns Xirsys TURN servers if configured, otherwise falls back to Google STUN
    """
    
    if not XIRSYS_IDENT or not XIRSYS_SECRET:
        logger.info("Xirsys not configured, using default STUN servers")
        return {
            "success": True,
            "ice_servers": DEFAULT_ICE_SERVERS,
            "turn_enabled": False
        }
    
    try:
        # Fetch TURN credentials from Xirsys
        url = f"https://global.xirsys.net/_turn/{XIRSYS_CHANNEL}"
        
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(XIRSYS_IDENT, XIRSYS_SECRET)
            
            async with session.put(url, auth=auth) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("s") == "ok":
                        ice_servers = data.get("v", {}).get("iceServers", [])
                        
                        logger.info(f"Fetched {len(ice_servers)} ICE servers from Xirsys")
                        
                        return {
                            "success": True,
                            "ice_servers": ice_servers,
                            "turn_enabled": True
                        }
                    else:
                        logger.error(f"Xirsys error: {data.get('v')}")
                else:
                    logger.error(f"Xirsys HTTP error: {response.status}")
        
    except Exception as e:
        logger.error(f"Failed to fetch Xirsys ICE servers: {e}")
    
    # Fallback to default STUN servers
    return {
        "success": True,
        "ice_servers": DEFAULT_ICE_SERVERS,
        "turn_enabled": False,
        "fallback": True
    }


def get_default_ice_servers() -> List[Dict]:
    """Get default STUN servers (no TURN)"""
    return DEFAULT_ICE_SERVERS
