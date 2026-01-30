"""
ML Issue Predictor - Rule-Based Prediction System
Uses collected ML training data to predict system issues and suggest preventive actions.
This is a simple rule-based system that can be upgraded to a trained ML model later.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics

from utils.database import db
from services.ml_data_collector import ml_collector, EventType, EventSeverity

logger = logging.getLogger(__name__)


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    API_LATENCY = "api_latency"
    DATABASE = "database"
    MEMORY = "memory"
    USER_EXPERIENCE = "user_experience"
    SECURITY = "security"


@dataclass
class PredictedIssue:
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    probability: float  # 0-100
    evidence: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    time_to_impact: Optional[str] = None  # e.g., "2 hours", "immediate"


@dataclass
class HealthScore:
    overall: float  # 0-100
    performance: float
    error_rate: float
    api_health: float
    database_health: float
    user_satisfaction: float


# ============== Rule Definitions ==============

# Thresholds for issue detection
THRESHOLDS = {
    "error_rate_warning": 10,      # % of requests that are errors (raised from 5%)
    "error_rate_critical": 25,     # % critical threshold (raised from 15%)
    "api_latency_warning": 800,    # ms average response time (raised from 500ms)
    "api_latency_critical": 3000,  # ms critical threshold (raised from 2000ms)
    "cpu_warning": 75,             # % CPU usage (raised from 70%)
    "cpu_critical": 92,            # % critical (raised from 90%)
    "memory_warning": 80,          # % memory usage (raised from 75%)
    "memory_critical": 92,         # % critical (raised from 90%)
    "error_spike_multiplier": 4,   # x normal error rate = spike (raised from 3x)
    "min_data_points": 10,         # minimum events to analyze
}


class MLIssuePredictor:
    """Rule-based issue prediction using ML training data"""
    
    def __init__(self):
        self.last_analysis_time = None
        self.cached_predictions: List[PredictedIssue] = []
        self.historical_baselines: Dict[str, float] = {}
    
    async def analyze(self, hours: int = 24) -> Dict:
        """
        Analyze recent data and predict potential issues.
        Returns predictions with confidence scores.
        """
        self.last_analysis_time = datetime.now(timezone.utc)
        predictions: List[PredictedIssue] = []
        
        # Fetch recent events
        events = await self._get_recent_events(hours)
        
        if len(events) < THRESHOLDS["min_data_points"]:
            return {
                "status": "insufficient_data",
                "events_analyzed": len(events),
                "min_required": THRESHOLDS["min_data_points"],
                "predictions": [],
                "health_score": None
            }
        
        # Calculate current metrics
        metrics = await self._calculate_metrics(events)
        
        # Run prediction rules
        predictions.extend(self._check_error_rate(events, metrics))
        predictions.extend(self._check_api_latency(events, metrics))
        predictions.extend(self._check_system_resources(events, metrics))
        predictions.extend(self._check_error_patterns(events, metrics))
        predictions.extend(self._check_user_behavior_anomalies(events, metrics))
        
        # Calculate overall health score
        health_score = self._calculate_health_score(metrics)
        
        # Sort by severity and probability
        predictions.sort(key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity.value],
            -x.probability
        ))
        
        # Cache predictions
        self.cached_predictions = predictions
        
        return {
            "status": "analyzed",
            "timestamp": self.last_analysis_time.isoformat(),
            "events_analyzed": len(events),
            "time_period_hours": hours,
            "predictions": [self._prediction_to_dict(p) for p in predictions],
            "health_score": {
                "overall": round(health_score.overall, 1),
                "performance": round(health_score.performance, 1),
                "error_rate": round(health_score.error_rate, 1),
                "api_health": round(health_score.api_health, 1),
                "database_health": round(health_score.database_health, 1),
                "user_satisfaction": round(health_score.user_satisfaction, 1)
            },
            "metrics_summary": {
                "error_rate": round(metrics.get("error_rate", 0), 2),
                "avg_response_time_ms": round(metrics.get("avg_response_time", 0), 2),
                "total_errors": metrics.get("total_errors", 0),
                "total_requests": metrics.get("total_requests", 0),
                "unique_users": metrics.get("unique_users", 0)
            }
        }
    
    async def _get_recent_events(self, hours: int) -> List[Dict]:
        """Fetch recent events from ML training data"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        try:
            cursor = db.ml_training_data.find(
                {"timestamp": {"$gte": cutoff}},
                {"_id": 0}
            ).sort("timestamp", -1)
            
            events = await cursor.to_list(length=10000)
            return events
        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")
            return []
    
    async def _calculate_metrics(self, events: List[Dict]) -> Dict:
        """Calculate key metrics from events"""
        metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "error_rate": 0,
            "response_times": [],
            "avg_response_time": 0,
            "cpu_samples": [],
            "memory_samples": [],
            "unique_users": set(),
            "error_types": {},
            "api_endpoints": {},
            "hourly_distribution": {}
        }
        
        for event in events:
            event_type = event.get("event_type")
            severity = event.get("severity")
            
            # Count requests and errors
            if event_type == "api_call":
                metrics["total_requests"] += 1
                
                status = event.get("data", {}).get("status_code", 200)
                if status >= 400:
                    metrics["total_errors"] += 1
                    error_type = f"HTTP_{status}"
                    metrics["error_types"][error_type] = metrics["error_types"].get(error_type, 0) + 1
                
                # Track response times
                response_time = event.get("response_time_ms")
                if response_time:
                    metrics["response_times"].append(response_time)
                
                # Track endpoint usage
                path = event.get("request_path", "unknown")
                metrics["api_endpoints"][path] = metrics["api_endpoints"].get(path, 0) + 1
            
            # Track errors
            if severity in ["error", "critical"]:
                metrics["total_errors"] += 1
            
            # Track system metrics
            sys_metrics = event.get("system_metrics", {})
            if sys_metrics.get("cpu_percent"):
                metrics["cpu_samples"].append(sys_metrics["cpu_percent"])
            if sys_metrics.get("memory_percent"):
                metrics["memory_samples"].append(sys_metrics["memory_percent"])
            
            # Track unique users
            user_id = event.get("user_id")
            if user_id:
                metrics["unique_users"].add(user_id)
            
            # Track hourly distribution
            timestamp = event.get("timestamp")
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                hour = timestamp.hour
                metrics["hourly_distribution"][hour] = metrics["hourly_distribution"].get(hour, 0) + 1
        
        # Calculate averages
        if metrics["total_requests"] > 0:
            metrics["error_rate"] = (metrics["total_errors"] / metrics["total_requests"]) * 100
        
        if metrics["response_times"]:
            metrics["avg_response_time"] = statistics.mean(metrics["response_times"])
            metrics["p95_response_time"] = sorted(metrics["response_times"])[int(len(metrics["response_times"]) * 0.95)] if len(metrics["response_times"]) > 20 else max(metrics["response_times"])
        
        if metrics["cpu_samples"]:
            metrics["avg_cpu"] = statistics.mean(metrics["cpu_samples"])
        
        if metrics["memory_samples"]:
            metrics["avg_memory"] = statistics.mean(metrics["memory_samples"])
        
        metrics["unique_users"] = len(metrics["unique_users"])
        
        return metrics
    
    def _check_error_rate(self, events: List[Dict], metrics: Dict) -> List[PredictedIssue]:
        """Check for elevated error rates"""
        predictions = []
        error_rate = metrics.get("error_rate", 0)
        
        if error_rate >= THRESHOLDS["error_rate_critical"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.ERROR_RATE,
                severity=IssueSeverity.CRITICAL,
                title="Critical Error Rate Detected",
                description=f"Error rate is at {error_rate:.1f}%, significantly above normal levels.",
                probability=95,
                evidence=[
                    f"Current error rate: {error_rate:.1f}%",
                    f"Total errors: {metrics.get('total_errors', 0)}",
                    f"Threshold: {THRESHOLDS['error_rate_critical']}%"
                ],
                recommended_actions=[
                    "Immediately investigate error logs",
                    "Check for recent deployments or config changes",
                    "Consider enabling maintenance mode",
                    "Alert on-call engineering team"
                ],
                affected_components=["API", "Backend Services"],
                time_to_impact="immediate"
            ))
        elif error_rate >= THRESHOLDS["error_rate_warning"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.ERROR_RATE,
                severity=IssueSeverity.MEDIUM,
                title="Elevated Error Rate",
                description=f"Error rate ({error_rate:.1f}%) is above normal but not critical.",
                probability=75,
                evidence=[
                    f"Current error rate: {error_rate:.1f}%",
                    f"Warning threshold: {THRESHOLDS['error_rate_warning']}%"
                ],
                recommended_actions=[
                    "Monitor error trends",
                    "Review recent error logs",
                    "Check external service dependencies"
                ],
                affected_components=["API"],
                time_to_impact="1-2 hours"
            ))
        
        return predictions
    
    def _check_api_latency(self, events: List[Dict], metrics: Dict) -> List[PredictedIssue]:
        """Check for API latency issues"""
        predictions = []
        avg_latency = metrics.get("avg_response_time", 0)
        p95_latency = metrics.get("p95_response_time", 0)
        
        if avg_latency >= THRESHOLDS["api_latency_critical"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.API_LATENCY,
                severity=IssueSeverity.HIGH,
                title="Critical API Latency",
                description=f"Average API response time is {avg_latency:.0f}ms, causing poor user experience.",
                probability=90,
                evidence=[
                    f"Average latency: {avg_latency:.0f}ms",
                    f"95th percentile: {p95_latency:.0f}ms",
                    f"Critical threshold: {THRESHOLDS['api_latency_critical']}ms"
                ],
                recommended_actions=[
                    "Check database query performance",
                    "Review recent code changes",
                    "Analyze slow endpoints",
                    "Consider enabling caching"
                ],
                affected_components=["API", "Database", "User Experience"],
                time_to_impact="immediate"
            ))
        elif avg_latency >= THRESHOLDS["api_latency_warning"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.API_LATENCY,
                severity=IssueSeverity.LOW,
                title="API Latency Above Normal",
                description=f"API response times ({avg_latency:.0f}ms avg) are slower than ideal.",
                probability=60,
                evidence=[
                    f"Average latency: {avg_latency:.0f}ms",
                    f"Warning threshold: {THRESHOLDS['api_latency_warning']}ms"
                ],
                recommended_actions=[
                    "Monitor latency trends",
                    "Profile slow endpoints",
                    "Check for resource contention"
                ],
                affected_components=["API"],
                time_to_impact="2-4 hours"
            ))
        
        return predictions
    
    def _check_system_resources(self, events: List[Dict], metrics: Dict) -> List[PredictedIssue]:
        """Check for system resource issues"""
        predictions = []
        
        avg_cpu = metrics.get("avg_cpu", 0)
        avg_memory = metrics.get("avg_memory", 0)
        
        # CPU checks
        if avg_cpu >= THRESHOLDS["cpu_critical"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.PERFORMANCE,
                severity=IssueSeverity.CRITICAL,
                title="Critical CPU Usage",
                description=f"CPU usage at {avg_cpu:.0f}% - system may become unresponsive.",
                probability=95,
                evidence=[f"Average CPU: {avg_cpu:.0f}%"],
                recommended_actions=[
                    "Scale up resources immediately",
                    "Identify CPU-intensive processes",
                    "Consider load balancing"
                ],
                affected_components=["System", "API"],
                time_to_impact="immediate"
            ))
        elif avg_cpu >= THRESHOLDS["cpu_warning"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.PERFORMANCE,
                severity=IssueSeverity.MEDIUM,
                title="High CPU Usage",
                description=f"CPU usage ({avg_cpu:.0f}%) approaching critical levels.",
                probability=70,
                evidence=[f"Average CPU: {avg_cpu:.0f}%"],
                recommended_actions=[
                    "Monitor CPU trends",
                    "Plan capacity upgrade",
                    "Optimize resource-heavy operations"
                ],
                affected_components=["System"],
                time_to_impact="1-2 hours"
            ))
        
        # Memory checks
        if avg_memory >= THRESHOLDS["memory_critical"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.MEMORY,
                severity=IssueSeverity.CRITICAL,
                title="Critical Memory Usage",
                description=f"Memory usage at {avg_memory:.0f}% - OOM risk imminent.",
                probability=95,
                evidence=[f"Average memory: {avg_memory:.0f}%"],
                recommended_actions=[
                    "Restart services to free memory",
                    "Investigate memory leaks",
                    "Scale up memory resources"
                ],
                affected_components=["System", "Database"],
                time_to_impact="immediate"
            ))
        elif avg_memory >= THRESHOLDS["memory_warning"]:
            predictions.append(PredictedIssue(
                category=IssueCategory.MEMORY,
                severity=IssueSeverity.MEDIUM,
                title="High Memory Usage",
                description=f"Memory usage ({avg_memory:.0f}%) is elevated.",
                probability=65,
                evidence=[f"Average memory: {avg_memory:.0f}%"],
                recommended_actions=[
                    "Monitor memory trends",
                    "Check for memory leaks",
                    "Plan memory upgrade"
                ],
                affected_components=["System"],
                time_to_impact="2-4 hours"
            ))
        
        return predictions
    
    def _check_error_patterns(self, events: List[Dict], metrics: Dict) -> List[PredictedIssue]:
        """Detect error patterns and spikes"""
        predictions = []
        error_types = metrics.get("error_types", {})
        
        # Check for concentrated error types
        for error_type, count in error_types.items():
            if count > 10:  # More than 10 of same error type
                severity = IssueSeverity.MEDIUM
                if count > 50:
                    severity = IssueSeverity.HIGH
                
                predictions.append(PredictedIssue(
                    category=IssueCategory.ERROR_RATE,
                    severity=severity,
                    title=f"Repeated {error_type} Errors",
                    description=f"Detected {count} occurrences of {error_type} errors.",
                    probability=80,
                    evidence=[
                        f"Error type: {error_type}",
                        f"Occurrences: {count}"
                    ],
                    recommended_actions=[
                        f"Investigate root cause of {error_type}",
                        "Check affected endpoints",
                        "Review error logs for details"
                    ],
                    affected_components=["API"],
                    time_to_impact="ongoing"
                ))
        
        return predictions
    
    def _check_user_behavior_anomalies(self, events: List[Dict], metrics: Dict) -> List[PredictedIssue]:
        """Detect unusual user behavior patterns"""
        predictions = []
        
        # Check for unusual hourly distribution (potential bot activity)
        hourly = metrics.get("hourly_distribution", {})
        if hourly:
            avg_hourly = statistics.mean(hourly.values()) if hourly else 0
            for hour, count in hourly.items():
                if count > avg_hourly * 3:  # 3x average traffic in any hour
                    predictions.append(PredictedIssue(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.LOW,
                        title="Traffic Spike Detected",
                        description=f"Unusual traffic spike at hour {hour}:00 UTC.",
                        probability=50,
                        evidence=[
                            f"Traffic at {hour}:00: {count} events",
                            f"Average hourly: {avg_hourly:.0f}"
                        ],
                        recommended_actions=[
                            "Review traffic sources",
                            "Check for bot activity",
                            "Monitor rate limiting effectiveness"
                        ],
                        affected_components=["API", "Security"],
                        time_to_impact="monitoring"
                    ))
                    break  # Only report first anomaly
        
        return predictions
    
    def _calculate_health_score(self, metrics: Dict) -> HealthScore:
        """Calculate overall system health score"""
        # Performance score (based on response time)
        avg_latency = metrics.get("avg_response_time", 0)
        performance = 100
        if avg_latency > 0:
            if avg_latency <= 100:
                performance = 100
            elif avg_latency <= 500:
                performance = 100 - ((avg_latency - 100) / 400 * 30)  # 70-100
            elif avg_latency <= 2000:
                performance = 70 - ((avg_latency - 500) / 1500 * 50)  # 20-70
            else:
                performance = max(0, 20 - ((avg_latency - 2000) / 3000 * 20))
        
        # Error rate score
        error_rate = metrics.get("error_rate", 0)
        error_score = 100
        if error_rate > 0:
            if error_rate <= 1:
                error_score = 100 - error_rate * 10
            elif error_rate <= 5:
                error_score = 90 - (error_rate - 1) * 10
            elif error_rate <= 15:
                error_score = 50 - (error_rate - 5) * 3
            else:
                error_score = max(0, 20 - (error_rate - 15))
        
        # API health (combination of latency and errors)
        api_health = (performance * 0.6 + error_score * 0.4)
        
        # Database health (based on DB operation times if available)
        db_health = 90  # Default good score
        
        # User satisfaction (estimated from error rate and latency)
        user_satisfaction = (performance * 0.5 + error_score * 0.5)
        
        # Overall score
        overall = (
            performance * 0.25 +
            error_score * 0.30 +
            api_health * 0.20 +
            db_health * 0.15 +
            user_satisfaction * 0.10
        )
        
        return HealthScore(
            overall=overall,
            performance=performance,
            error_rate=error_score,
            api_health=api_health,
            database_health=db_health,
            user_satisfaction=user_satisfaction
        )
    
    def _prediction_to_dict(self, prediction: PredictedIssue) -> Dict:
        """Convert prediction to dictionary for JSON response"""
        return {
            "category": prediction.category.value,
            "severity": prediction.severity.value,
            "title": prediction.title,
            "description": prediction.description,
            "probability": prediction.probability,
            "evidence": prediction.evidence,
            "recommended_actions": prediction.recommended_actions,
            "affected_components": prediction.affected_components,
            "time_to_impact": prediction.time_to_impact
        }


# Global instance
issue_predictor = MLIssuePredictor()


# Export
__all__ = ['MLIssuePredictor', 'issue_predictor', 'IssueSeverity', 'IssueCategory', 'PredictedIssue']
