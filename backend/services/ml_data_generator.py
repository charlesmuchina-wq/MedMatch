"""
ML Training Data Generator
Automatically generates diverse training data for ML model improvement.
Runs as a background task to simulate various system states.
"""
import asyncio
import logging
import random
from typing import Dict

from services.ml_data_collector import ml_collector, EventType, EventSeverity

logger = logging.getLogger(__name__)


class MLDataGenerator:
    """
    Generates synthetic but realistic training data for ML models.
    Creates diverse scenarios to improve model accuracy.
    """
    
    def __init__(self):
        self.is_running = False
        self.generation_task = None
    
    async def start(self, interval_seconds: int = 60):
        """Start periodic data generation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.generation_task = asyncio.create_task(
            self._run_periodic_generation(interval_seconds)
        )
        logger.info(f"ML Data Generator started - interval: {interval_seconds}s")
    
    async def stop(self):
        """Stop data generation"""
        self.is_running = False
        if self.generation_task:
            self.generation_task.cancel()
        logger.info("ML Data Generator stopped")
    
    async def _run_periodic_generation(self, interval_seconds: int):
        """Run data generation on interval"""
        while self.is_running:
            try:
                await self.generate_batch()
            except Exception as e:
                logger.error(f"Data generation error: {e}")
            
            await asyncio.sleep(interval_seconds)
    
    async def generate_batch(self, count: int = 10) -> Dict:
        """Generate a batch of diverse training events"""
        generated = {
            "api_calls": 0,
            "user_actions": 0,
            "system_events": 0,
            "errors": 0
        }
        
        # Simulate various scenarios
        scenarios = [
            self._generate_healthy_scenario,
            self._generate_degraded_scenario,
            self._generate_high_load_scenario,
            self._generate_error_spike_scenario,
            self._generate_normal_usage_scenario
        ]
        
        # Weight towards normal/healthy scenarios (80% normal, 20% issues)
        weights = [0.3, 0.1, 0.05, 0.05, 0.5]
        
        for _ in range(count):
            scenario = random.choices(scenarios, weights=weights)[0]
            result = await scenario()
            for key in generated:
                generated[key] += result.get(key, 0)
        
        return generated
    
    async def _generate_healthy_scenario(self) -> Dict:
        """Generate events for a healthy system state"""
        count = {"api_calls": 0, "user_actions": 0, "system_events": 0, "errors": 0}
        
        # Simulate successful API calls
        endpoints = [
            "/api/auth/me", "/api/jobs/search", "/api/resume/parse",
            "/api/applications", "/api/dashboard", "/api/settings"
        ]
        
        for _ in range(random.randint(3, 8)):
            await ml_collector.log_api_call(
                path=random.choice(endpoints),
                method="GET",
                status_code=200,
                response_time_ms=random.uniform(10, 200),
                user_id=f"user_{random.randint(1, 100)}"
            )
            count["api_calls"] += 1
        
        # Simulate user actions
        actions = [
            EventType.JOB_SEARCH,
            EventType.USER_LOGIN,
            EventType.RESUME_PARSE
        ]
        
        for _ in range(random.randint(1, 3)):
            await ml_collector.log_user_action(
                action=random.choice(actions),
                user_id=f"user_{random.randint(1, 100)}",
                data={"source": "data_generator"}
            )
            count["user_actions"] += 1
        
        return count
    
    async def _generate_degraded_scenario(self) -> Dict:
        """Generate events for a degraded system state"""
        count = {"api_calls": 0, "user_actions": 0, "system_events": 0, "errors": 0}
        
        # Mix of successful and slow/failed calls
        for _ in range(random.randint(5, 10)):
            status = random.choices([200, 500, 503], weights=[0.7, 0.2, 0.1])[0]
            response_time = random.uniform(500, 1500) if status == 200 else random.uniform(2000, 5000)
            
            await ml_collector.log_api_call(
                path="/api/jobs/search",
                method="GET",
                status_code=status,
                response_time_ms=response_time
            )
            count["api_calls"] += 1
            if status >= 500:
                count["errors"] += 1
        
        # Log warning events
        await ml_collector.log_event(
            event_type=EventType.SYSTEM_WARNING,
            severity=EventSeverity.WARNING,
            message="Elevated response times detected",
            data={"avg_response_time": random.uniform(800, 1500)}
        )
        count["system_events"] += 1
        
        return count
    
    async def _generate_high_load_scenario(self) -> Dict:
        """Generate events simulating high system load"""
        count = {"api_calls": 0, "user_actions": 0, "system_events": 0, "errors": 0}
        
        # High CPU/Memory metrics
        await ml_collector.log_performance_metric(
            metric_name="cpu_usage",
            value=random.uniform(75, 95),
            unit="%"
        )
        await ml_collector.log_performance_metric(
            metric_name="memory_usage",
            value=random.uniform(80, 92),
            unit="%"
        )
        count["system_events"] += 2
        
        # Slower API responses under load
        for _ in range(random.randint(3, 6)):
            await ml_collector.log_api_call(
                path="/api/ai/generate",
                method="POST",
                status_code=200,
                response_time_ms=random.uniform(1000, 3000)
            )
            count["api_calls"] += 1
        
        return count
    
    async def _generate_error_spike_scenario(self) -> Dict:
        """Generate events simulating an error spike"""
        count = {"api_calls": 0, "user_actions": 0, "system_events": 0, "errors": 0}
        
        # Multiple errors in quick succession
        error_codes = [500, 502, 503, 504]
        
        for _ in range(random.randint(3, 8)):
            await ml_collector.log_api_call(
                path="/api/external/service",
                method="POST",
                status_code=random.choice(error_codes),
                response_time_ms=random.uniform(5000, 10000)
            )
            count["api_calls"] += 1
            count["errors"] += 1
        
        # Log system error
        await ml_collector.log_system_error(
            message="External service connection failed",
            data={"service": "payment_gateway", "retry_count": random.randint(1, 5)}
        )
        count["system_events"] += 1
        
        return count
    
    async def _generate_normal_usage_scenario(self) -> Dict:
        """Generate events for normal daily usage"""
        count = {"api_calls": 0, "user_actions": 0, "system_events": 0, "errors": 0}
        
        # Regular API traffic
        endpoints = [
            ("/api/auth/me", "GET", [200]),
            ("/api/jobs/search", "GET", [200, 200, 200, 404]),
            ("/api/applications", "GET", [200]),
            ("/api/notifications", "GET", [200]),
            ("/api/resume/parse", "POST", [200, 200, 400]),
        ]
        
        for endpoint, method, status_options in endpoints:
            if random.random() < 0.7:  # 70% chance to call each endpoint
                status = random.choice(status_options)
                await ml_collector.log_api_call(
                    path=endpoint,
                    method=method,
                    status_code=status,
                    response_time_ms=random.uniform(20, 300),
                    user_id=f"user_{random.randint(1, 100)}"
                )
                count["api_calls"] += 1
                if status >= 400:
                    count["errors"] += 1
        
        # Occasional AI interactions
        if random.random() < 0.3:
            await ml_collector.log_ai_interaction(
                ai_type="cover_letter",
                user_id=f"user_{random.randint(1, 100)}",
                input_summary="Generate cover letter for software engineer position",
                output_summary="Cover letter generated successfully",
                tokens_used=random.randint(500, 2000),
                response_time_ms=random.uniform(1000, 5000),
                success=True
            )
            count["user_actions"] += 1
        
        return count
    
    async def generate_historical_data(self, hours: int = 24, events_per_hour: int = 50) -> Dict:
        """
        Generate historical training data for a specified time period.
        Useful for bootstrapping the ML model with diverse data.
        """
        total_generated = {
            "api_calls": 0,
            "user_actions": 0,
            "system_events": 0,
            "errors": 0,
            "hours_covered": hours
        }
        
        logger.info(f"Generating {hours} hours of historical training data...")
        
        for hour_offset in range(hours):
            # Generate events for this hour
            batch_result = await self.generate_batch(count=events_per_hour)
            
            for key in ["api_calls", "user_actions", "system_events", "errors"]:
                total_generated[key] += batch_result.get(key, 0)
            
            # Small delay to prevent overwhelming the system
            if hour_offset % 10 == 0:
                await asyncio.sleep(0.1)
        
        # Flush all generated data
        await ml_collector._flush_buffer()
        
        logger.info(f"Historical data generation complete: {total_generated}")
        return total_generated


# Global instance
ml_data_generator = MLDataGenerator()


# Export
__all__ = ['MLDataGenerator', 'ml_data_generator']
