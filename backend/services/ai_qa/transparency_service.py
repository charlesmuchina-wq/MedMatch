"""
AI QA Compliance System - Transparency Dashboard Service

Provides real-time transparency metrics and audit health indicators
for regulatory compliance monitoring.
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .core_service import ai_decision_logger, bias_auditor, crypto_shredding
from .audit_service import compliance_checker, audit_scheduler
from .oversight_service import human_oversight

logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data/ai_qa")
DSAR_FILE = DATA_DIR / "dsar_requests.json"


class DSARManager:
    """
    Data Subject Access Request Manager.
    
    Handles GDPR Article 15-22 rights:
    - Right of Access
    - Right to Rectification
    - Right to Erasure
    - Right to Restriction
    - Right to Portability
    - Right to Object
    """
    
    def __init__(self):
        self.requests = self._load_requests()
    
    def _load_requests(self) -> List[Dict]:
        """Load DSAR requests."""
        if DSAR_FILE.exists():
            return json.loads(DSAR_FILE.read_text())
        return []
    
    def _save_requests(self):
        """Save requests."""
        DSAR_FILE.write_text(json.dumps(self.requests, indent=2))
    
    def submit_request(
        self,
        user_id: str,
        request_type: str,
        details: Dict
    ) -> Dict:
        """Submit a new DSAR request."""
        valid_types = ["access", "rectification", "erasure", "restriction", "portability", "object", "explanation"]
        if request_type not in valid_types:
            return {"error": f"Invalid request type. Valid types: {valid_types}"}
        
        request = {
            "request_id": f"DSAR-{datetime.now().strftime('%Y%m%d')}-{len(self.requests) + 1:04d}",
            "user_id": user_id,
            "request_type": request_type,
            "details": details,
            "status": "pending",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),  # GDPR 30-day deadline
            "processed_at": None,
            "processed_by": None,
            "response": None
        }
        
        self.requests.append(request)
        self._save_requests()
        
        logger.info(f"DSAR submitted: {request['request_id']} - {request_type}")
        return request
    
    def process_request(
        self,
        request_id: str,
        processor_id: str,
        response: Dict,
        status: str = "completed"
    ) -> Dict:
        """Process a DSAR request."""
        for req in self.requests:
            if req["request_id"] == request_id:
                req["status"] = status
                req["processed_at"] = datetime.now(timezone.utc).isoformat()
                req["processed_by"] = processor_id
                req["response"] = response
                
                # If erasure request, trigger crypto-shredding
                if req["request_type"] == "erasure" and status == "completed":
                    shred_result = crypto_shredding.shred_user_data(req["user_id"])
                    req["response"]["shredding_result"] = shred_result
                
                self._save_requests()
                return req
        
        return {"error": "Request not found"}
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending DSAR requests."""
        return [r for r in self.requests if r["status"] == "pending"]
    
    def get_request(self, request_id: str) -> Optional[Dict]:
        """Get a specific request."""
        return next((r for r in self.requests if r["request_id"] == request_id), None)
    
    def get_user_requests(self, user_id: str) -> List[Dict]:
        """Get all requests for a user."""
        return [r for r in self.requests if r["user_id"] == user_id]
    
    def get_dsar_stats(self) -> Dict:
        """Get DSAR processing statistics."""
        now = datetime.now(timezone.utc)
        
        pending = [r for r in self.requests if r["status"] == "pending"]
        overdue = [
            r for r in pending
            if datetime.fromisoformat(r["deadline"].replace("Z", "+00:00")) < now
        ]
        
        completed_30d = [
            r for r in self.requests
            if r["status"] == "completed" and 
            r.get("processed_at") and
            datetime.fromisoformat(r["processed_at"].replace("Z", "+00:00")) > now - timedelta(days=30)
        ]
        
        by_type = {}
        for r in self.requests:
            by_type[r["request_type"]] = by_type.get(r["request_type"], 0) + 1
        
        return {
            "total_requests": len(self.requests),
            "pending": len(pending),
            "overdue": len(overdue),
            "completed_last_30_days": len(completed_30d),
            "by_type": by_type,
            "compliance_status": "compliant" if not overdue else "non_compliant"
        }


class TransparencyDashboard:
    """
    Real-time Transparency Dashboard for AI QA Compliance.
    
    Provides:
    - Audit health status
    - Bias variance monitoring
    - Log integrity verification
    - DSAR tracking
    - Compliance scores
    """
    
    def __init__(self):
        self.dsar_manager = DSARManager()
    
    def get_dashboard_summary(self) -> Dict:
        """Get complete dashboard summary."""
        now = datetime.now(timezone.utc)
        
        # Get all component statuses
        decision_logs = ai_decision_logger.logs
        bias_summary = bias_auditor.get_fairness_summary()
        compliance_summary = compliance_checker.get_compliance_summary()
        oversight_stats = human_oversight.get_oversight_stats()
        dsar_stats = self.dsar_manager.get_dsar_stats()
        
        # Calculate overall health score
        health_components = {
            "bias_fairness": bias_summary.get("average_fairness_score", 100) if bias_summary.get("status") != "no_audits" else 100,
            "compliance": compliance_summary.get("average_score", 0) if compliance_summary.get("status") != "no_assessments" else 100,
            "dsar_compliance": 100 if dsar_stats["compliance_status"] == "compliant" else 50,
            "log_integrity": self._verify_log_integrity(decision_logs),
            "oversight_coverage": min(100, oversight_stats["active_overseers"] * 25)  # 4+ overseers = 100%
        }
        
        overall_health = sum(health_components.values()) / len(health_components)
        
        return {
            "timestamp": now.isoformat(),
            "overall_health": {
                "score": round(overall_health, 1),
                "status": self._health_status(overall_health),
                "components": health_components
            },
            "ai_decisions": {
                "total_logged": len(decision_logs),
                "last_24h": len([
                    d for d in decision_logs
                    if d.get("timestamp", "") > (now - timedelta(hours=24)).isoformat()
                ]),
                "human_reviewed": len([
                    d for d in decision_logs
                    if d.get("human_oversight", {}).get("action") != "PENDING_REVIEW"
                ]),
                "review_rate": self._calculate_review_rate(decision_logs)
            },
            "bias_monitoring": {
                **bias_summary,
                "alerts": self._get_bias_alerts()
            },
            "compliance": {
                **compliance_summary,
                "next_audit": self._get_next_audit()
            },
            "human_oversight": oversight_stats,
            "dsar": dsar_stats,
            "alerts": self._get_all_alerts(
                bias_summary, compliance_summary, oversight_stats, dsar_stats
            )
        }
    
    def _health_status(self, score: float) -> str:
        """Convert health score to status string."""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "needs_attention"
        else:
            return "critical"
    
    def _verify_log_integrity(self, logs: List[Dict]) -> float:
        """Verify integrity of decision logs."""
        if not logs:
            return 100.0
        
        verified = sum(1 for log in logs[-100:] if ai_decision_logger._verify_signature(log))
        return round(verified / min(len(logs), 100) * 100, 1)
    
    def _calculate_review_rate(self, logs: List[Dict]) -> float:
        """Calculate human review rate."""
        if not logs:
            return 0.0
        
        reviewed = sum(
            1 for log in logs
            if log.get("human_oversight", {}).get("action") != "PENDING_REVIEW"
        )
        return round(reviewed / len(logs) * 100, 1)
    
    def _get_bias_alerts(self) -> List[Dict]:
        """Get current bias alerts."""
        alerts = []
        
        # Check recent bias audit results
        recent_audits = bias_auditor.audit_results[-5:] if bias_auditor.audit_results else []
        
        for audit in recent_audits:
            if audit.get("adverse_impact_flags"):
                for flag in audit["adverse_impact_flags"]:
                    alerts.append({
                        "type": "adverse_impact",
                        "severity": "high",
                        "group": flag["group"],
                        "ratio": flag["ratio"],
                        "message": f"Adverse impact detected for {flag['group']} (ratio: {flag['ratio']:.2f})"
                    })
        
        return alerts
    
    def _get_next_audit(self) -> Optional[Dict]:
        """Get next scheduled audit."""
        schedules = audit_scheduler.get_schedules()
        
        # Find next due audit (simplified - in production would calculate actual dates)
        for schedule in schedules:
            if schedule.get("enabled"):
                return {
                    "name": schedule["name"],
                    "type": schedule["audit_type"],
                    "frequency": schedule["frequency"]
                }
        
        return None
    
    def _get_all_alerts(
        self,
        bias_summary: Dict,
        compliance_summary: Dict,
        oversight_stats: Dict,
        dsar_stats: Dict
    ) -> List[Dict]:
        """Get all system alerts."""
        alerts = []
        
        # Bias alerts
        if bias_summary.get("status") == "critical":
            alerts.append({
                "type": "bias",
                "severity": "critical",
                "message": "Critical fairness issues detected - immediate review required"
            })
        elif bias_summary.get("status") == "needs_review":
            alerts.append({
                "type": "bias",
                "severity": "warning",
                "message": "Fairness metrics below threshold - review recommended"
            })
        
        # Compliance alerts
        if compliance_summary.get("status") == "non_compliant":
            alerts.append({
                "type": "compliance",
                "severity": "critical",
                "message": "Compliance score below acceptable threshold"
            })
        
        # DSAR alerts
        if dsar_stats.get("overdue", 0) > 0:
            alerts.append({
                "type": "dsar",
                "severity": "critical",
                "message": f"{dsar_stats['overdue']} overdue DSAR requests - GDPR violation risk"
            })
        
        # Oversight alerts
        if oversight_stats.get("emergency_stop_active"):
            alerts.append({
                "type": "system",
                "severity": "critical",
                "message": "AI system is in EMERGENCY STOP state"
            })
        
        if oversight_stats.get("active_overseers", 0) < 2:
            alerts.append({
                "type": "oversight",
                "severity": "warning",
                "message": "Insufficient active overseers - minimum 2 required"
            })
        
        return alerts
    
    def get_audit_health_card(self) -> Dict:
        """Get audit health card for display."""
        summary = self.get_dashboard_summary()
        
        return {
            "overall_score": summary["overall_health"]["score"],
            "status": summary["overall_health"]["status"],
            "status_color": self._status_color(summary["overall_health"]["status"]),
            "key_metrics": [
                {
                    "name": "AI Decisions (24h)",
                    "value": summary["ai_decisions"]["last_24h"],
                    "trend": "stable"
                },
                {
                    "name": "Human Review Rate",
                    "value": f"{summary['ai_decisions']['review_rate']}%",
                    "trend": "up" if summary["ai_decisions"]["review_rate"] > 10 else "down"
                },
                {
                    "name": "Bias Score",
                    "value": f"{summary['bias_monitoring'].get('average_fairness_score', 100):.0f}%",
                    "trend": "stable"
                },
                {
                    "name": "Compliance Score",
                    "value": f"{summary['compliance'].get('average_score', 100):.0f}%",
                    "trend": "stable"
                },
                {
                    "name": "Pending DSARs",
                    "value": summary["dsar"]["pending"],
                    "trend": "warning" if summary["dsar"]["pending"] > 5 else "stable"
                }
            ],
            "active_alerts": len(summary["alerts"]),
            "critical_alerts": len([a for a in summary["alerts"] if a["severity"] == "critical"])
        }
    
    def _status_color(self, status: str) -> str:
        """Get color for status."""
        colors = {
            "excellent": "green",
            "good": "blue",
            "needs_attention": "yellow",
            "critical": "red"
        }
        return colors.get(status, "gray")


# Initialize
dsar_manager = DSARManager()
transparency_dashboard = TransparencyDashboard()

__all__ = [
    'dsar_manager',
    'transparency_dashboard',
    'DSARManager',
    'TransparencyDashboard'
]
