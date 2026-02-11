"""
Real-Time Compliance Alert Service
Monitors bias thresholds, human oversight, and regulatory deadlines
Integrates with existing notification system for in-app alerts
"""
import os
import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class ComplianceAlertService:
    """
    Real-time monitoring and alerting for AI compliance violations.
    Covers:
    - Bias threshold violations (disparate impact < 0.80)
    - Missing human oversight on AI decisions
    - Approaching regulatory deadlines
    """
    
    ALERT_TYPES = {
        "BIAS_VIOLATION": {
            "severity": "CRITICAL",
            "icon": "⚠️",
            "title": "Bias Threshold Violation Detected",
            "requires_action": True
        },
        "HUMAN_OVERSIGHT_MISSING": {
            "severity": "HIGH",
            "icon": "👁️",
            "title": "Human Oversight Required",
            "requires_action": True
        },
        "DEADLINE_APPROACHING": {
            "severity": "MEDIUM",
            "icon": "📅",
            "title": "Regulatory Deadline Approaching",
            "requires_action": False
        },
        "DEADLINE_IMMINENT": {
            "severity": "HIGH",
            "icon": "🚨",
            "title": "Regulatory Deadline Imminent",
            "requires_action": True
        },
        "INCIDENT_DETECTED": {
            "severity": "CRITICAL",
            "icon": "🔴",
            "title": "Compliance Incident Detected",
            "requires_action": True
        }
    }
    
    # Regulatory deadlines for 2026
    REGULATORY_DEADLINES = [
        {"region": "South Korea", "law": "AI Basic Act", "date": "2026-01-01", "status": "COMPLIANT"},
        {"region": "Ontario", "law": "ESA Amendment", "date": "2026-01-01", "status": "COMPLIANT"},
        {"region": "Colorado", "law": "AI Act (SB 205)", "date": "2026-06-30", "status": "ON_TRACK"},
        {"region": "Singapore", "law": "Workplace Fairness Act", "date": "2026-07-01", "status": "ON_TRACK"},
        {"region": "EU", "law": "AI Act Full Enforcement", "date": "2026-08-02", "status": "ON_TRACK"},
        {"region": "NYC", "law": "LL 144 Annual Audit", "date": "2026-01-15", "status": "COMPLIANT"}
    ]
    
    # Bias thresholds (Four-Fifths Rule)
    BIAS_THRESHOLD = 0.80
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._alert_cache = {}
    
    async def check_all_compliance(self, admin_user_id: str) -> Dict:
        """
        Run all compliance checks and return summary with any new alerts.
        """
        alerts = []
        
        # 1. Check bias thresholds
        bias_alerts = await self._check_bias_thresholds()
        alerts.extend(bias_alerts)
        
        # 2. Check human oversight compliance
        oversight_alerts = await self._check_human_oversight()
        alerts.extend(oversight_alerts)
        
        # 3. Check approaching deadlines
        deadline_alerts = await self._check_deadlines()
        alerts.extend(deadline_alerts)
        
        # Create notifications for new alerts
        for alert in alerts:
            if not await self._is_duplicate_alert(alert):
                await self._create_alert_notification(alert, admin_user_id)
        
        return {
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["severity"] == "CRITICAL"]),
            "high_alerts": len([a for a in alerts if a["severity"] == "HIGH"]),
            "alerts": alerts
        }
    
    async def _check_bias_thresholds(self) -> List[Dict]:
        """Check for bias threshold violations across protected characteristics."""
        alerts = []
        
        # Get recent AI decisions from GUAL log
        recent_decisions = await self.db.gual_log.find({
            "timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
        }).to_list(1000)
        
        if not recent_decisions:
            # Return mock data showing healthy metrics
            return []
        
        # Calculate selection rates by protected characteristic
        characteristics = ["sex", "race", "ethnicity", "age", "disability"]
        
        for char in characteristics:
            # Group decisions by characteristic value
            groups = {}
            for decision in recent_decisions:
                char_value = decision.get("candidate_characteristics", {}).get(char, "unknown")
                if char_value not in groups:
                    groups[char_value] = {"total": 0, "selected": 0}
                groups[char_value]["total"] += 1
                if decision.get("action", {}).get("output_score", 0) >= 0.7:
                    groups[char_value]["selected"] += 1
            
            # Calculate impact ratio
            if len(groups) >= 2:
                rates = []
                for group, data in groups.items():
                    if data["total"] > 0:
                        rates.append(data["selected"] / data["total"])
                
                if rates and max(rates) > 0:
                    impact_ratio = min(rates) / max(rates)
                    
                    if impact_ratio < self.BIAS_THRESHOLD:
                        alerts.append({
                            "id": f"bias_{char}_{datetime.now().strftime('%Y%m%d%H%M')}",
                            "type": "BIAS_VIOLATION",
                            "severity": "CRITICAL",
                            "characteristic": char,
                            "impact_ratio": round(impact_ratio, 3),
                            "threshold": self.BIAS_THRESHOLD,
                            "message": f"Disparate impact detected for {char}: {impact_ratio:.2%} (threshold: 80%)",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "recommended_action": "Review recent AI decisions and recalibrate model",
                            "regulatory_impact": ["NYC LL 144", "California AEDT", "EU AI Act"]
                        })
        
        return alerts
    
    async def _check_human_oversight(self) -> List[Dict]:
        """Check for AI decisions missing human review."""
        alerts = []
        
        # Find decisions requiring review that are pending
        pending_reviews = await self.db.gual_log.count_documents({
            "human_oversight.requires_manual_review": True,
            "human_oversight.review_status": "PENDING",
            "timestamp": {"$lte": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}
        })
        
        if pending_reviews > 0:
            alerts.append({
                "id": f"oversight_{datetime.now().strftime('%Y%m%d%H%M')}",
                "type": "HUMAN_OVERSIGHT_MISSING",
                "severity": "HIGH",
                "pending_count": pending_reviews,
                "message": f"{pending_reviews} AI decisions pending human review for >24 hours",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recommended_action": "Review pending decisions in the compliance dashboard",
                "regulatory_impact": ["EU AI Act Article 14", "Colorado AI Act"]
            })
        
        return alerts
    
    async def _check_deadlines(self) -> List[Dict]:
        """Check for approaching regulatory deadlines."""
        alerts = []
        today = datetime.now(timezone.utc).date()
        
        for deadline in self.REGULATORY_DEADLINES:
            deadline_date = datetime.strptime(deadline["date"], "%Y-%m-%d").date()
            days_until = (deadline_date - today).days
            
            # Skip already passed or compliant deadlines
            if days_until < 0 or deadline["status"] == "COMPLIANT":
                continue
            
            if days_until <= 7:
                alerts.append({
                    "id": f"deadline_{deadline['region']}_{deadline_date.strftime('%Y%m%d')}",
                    "type": "DEADLINE_IMMINENT",
                    "severity": "HIGH",
                    "region": deadline["region"],
                    "law": deadline["law"],
                    "deadline_date": deadline["date"],
                    "days_remaining": days_until,
                    "message": f"{deadline['law']} deadline in {days_until} days ({deadline['region']})",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "recommended_action": "Complete final compliance checks immediately"
                })
            elif days_until <= 30:
                alerts.append({
                    "id": f"deadline_{deadline['region']}_{deadline_date.strftime('%Y%m%d')}",
                    "type": "DEADLINE_APPROACHING",
                    "severity": "MEDIUM",
                    "region": deadline["region"],
                    "law": deadline["law"],
                    "deadline_date": deadline["date"],
                    "days_remaining": days_until,
                    "message": f"{deadline['law']} deadline in {days_until} days ({deadline['region']})",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "recommended_action": "Review compliance status and complete outstanding items"
                })
        
        return alerts
    
    async def _is_duplicate_alert(self, alert: Dict) -> bool:
        """Check if this alert was already created recently."""
        existing = await self.db.compliance_alerts.find_one({
            "id": alert["id"],
            "timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()}
        })
        return existing is not None
    
    async def _create_alert_notification(self, alert: Dict, user_id: str):
        """Create in-app notification for compliance alert."""
        alert_config = self.ALERT_TYPES.get(alert["type"], {})
        
        # Store alert in compliance_alerts collection
        await self.db.compliance_alerts.insert_one({
            **alert,
            "user_id": user_id,
            "acknowledged": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create notification using existing notification system
        notification = {
            "id": f"notif_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "type": "compliance_alert",
            "title": f"{alert_config.get('icon', '⚠️')} {alert_config.get('title', 'Compliance Alert')}",
            "message": alert["message"],
            "data": {
                "alert_id": alert["id"],
                "alert_type": alert["type"],
                "severity": alert["severity"],
                "requires_action": alert_config.get("requires_action", True)
            },
            "priority": "high" if alert["severity"] in ["CRITICAL", "HIGH"] else "medium",
            "read": False,
            "action_url": "/admin/global-compliance",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.notifications.insert_one(notification)
        return notification
    
    async def get_active_alerts(self, user_id: str = None) -> List[Dict]:
        """Get all active (unacknowledged) compliance alerts."""
        query = {"acknowledged": False}
        if user_id:
            query["user_id"] = user_id
        
        alerts = await self.db.compliance_alerts.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
        return alerts
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Mark an alert as acknowledged."""
        result = await self.db.compliance_alerts.update_one(
            {"id": alert_id, "user_id": user_id},
            {
                "$set": {
                    "acknowledged": True,
                    "acknowledged_at": datetime.now(timezone.utc).isoformat(),
                    "acknowledged_by": user_id
                }
            }
        )
        return result.modified_count > 0


# Singleton instance
_compliance_alert_service = None

def get_compliance_alert_service(db=None):
    global _compliance_alert_service
    if _compliance_alert_service is None and db is not None:
        _compliance_alert_service = ComplianceAlertService(db)
    return _compliance_alert_service
