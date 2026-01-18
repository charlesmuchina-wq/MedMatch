"""
AI Supervisor Service
Intelligent load management, auto-scaling, and request orchestration
Handles up to 3000 concurrent users with adaptive resource allocation
"""
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import statistics
import uuid

logger = logging.getLogger(__name__)

# ============== Enums ==============

class RequestPriority(Enum):
    CRITICAL = 1    # Health checks, auth
    HIGH = 2        # User-facing API calls
    NORMAL = 3      # Standard requests
    LOW = 4         # Background tasks
    BULK = 5        # Batch operations

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery

class SystemHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OVERLOADED = "overloaded"

# ============== Data Classes ==============

@dataclass
class RequestMetrics:
    """Tracks request performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        if len(self.response_times) < 2:
            return 0.0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]

@dataclass
class QueuedRequest:
    """Represents a queued request"""
    id: str
    priority: RequestPriority
    created_at: float
    handler: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout: float = 30.0
    
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.timeout

# ============== Circuit Breaker ==============

class CircuitBreaker:
    """
    Implements circuit breaker pattern to prevent cascade failures
    """
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN")
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Record successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recovered)")
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (failed during recovery)")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name}: CLOSED -> OPEN (threshold reached)")
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold
        }

# ============== Request Queue ==============

class PriorityRequestQueue:
    """
    Priority-based request queue with intelligent scheduling
    """
    def __init__(self, max_size: int = 5000):
        self.max_size = max_size
        self.queues: Dict[RequestPriority, deque] = {
            priority: deque() for priority in RequestPriority
        }
        self.total_queued = 0
        self._lock = asyncio.Lock()
    
    async def enqueue(self, request: QueuedRequest) -> bool:
        """Add request to appropriate priority queue"""
        async with self._lock:
            if self.total_queued >= self.max_size:
                # Shed low priority requests first
                if request.priority.value >= RequestPriority.LOW.value:
                    return False
                # Try to make room by dropping bulk requests
                if self.queues[RequestPriority.BULK]:
                    self.queues[RequestPriority.BULK].popleft()
                    self.total_queued -= 1
            
            self.queues[request.priority].append(request)
            self.total_queued += 1
            return True
    
    async def dequeue(self) -> Optional[QueuedRequest]:
        """Get highest priority non-expired request"""
        async with self._lock:
            for priority in RequestPriority:
                queue = self.queues[priority]
                while queue:
                    request = queue.popleft()
                    self.total_queued -= 1
                    if not request.is_expired():
                        return request
                    # Skip expired requests
                    logger.debug(f"Dropped expired request {request.id}")
            return None
    
    def get_stats(self) -> dict:
        return {
            "total_queued": self.total_queued,
            "max_size": self.max_size,
            "by_priority": {
                p.name: len(self.queues[p]) for p in RequestPriority
            }
        }

# ============== Adaptive Rate Limiter ==============

class AdaptiveRateLimiter:
    """
    AI-powered adaptive rate limiting based on system health
    """
    def __init__(
        self,
        base_rate: int = 1000,  # requests per second
        min_rate: int = 100,
        max_rate: int = 3000,
        window_size: float = 1.0  # seconds
    ):
        self.base_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.current_rate = base_rate
        self.window_size = window_size
        
        self.request_timestamps: deque = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Try to acquire a rate limit token"""
        async with self._lock:
            now = time.time()
            
            # Remove old timestamps
            while self.request_timestamps and \
                  self.request_timestamps[0] < now - self.window_size:
                self.request_timestamps.popleft()
            
            # Check rate limit
            if len(self.request_timestamps) >= self.current_rate:
                return False
            
            self.request_timestamps.append(now)
            return True
    
    def adjust_rate(self, health: SystemHealth, metrics: RequestMetrics):
        """Adjust rate limit based on system health"""
        if health == SystemHealth.HEALTHY:
            # Gradually increase rate
            self.current_rate = min(
                self.max_rate,
                int(self.current_rate * 1.1)
            )
        elif health == SystemHealth.DEGRADED:
            # Maintain current rate
            pass
        elif health == SystemHealth.CRITICAL:
            # Reduce rate significantly
            self.current_rate = max(
                self.min_rate,
                int(self.current_rate * 0.5)
            )
        elif health == SystemHealth.OVERLOADED:
            # Emergency reduction
            self.current_rate = self.min_rate
        
        logger.info(f"Rate limit adjusted to {self.current_rate} req/sec (health: {health.value})")
    
    def get_stats(self) -> dict:
        return {
            "current_rate": self.current_rate,
            "base_rate": self.base_rate,
            "min_rate": self.min_rate,
            "max_rate": self.max_rate,
            "current_load": len(self.request_timestamps)
        }

# ============== Worker Pool ==============

class WorkerPool:
    """
    Dynamic worker pool for processing requests
    """
    def __init__(
        self,
        min_workers: int = 10,
        max_workers: int = 100,
        target_queue_time_ms: float = 100.0
    ):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.target_queue_time_ms = target_queue_time_ms
        
        self.current_workers = min_workers
        self.active_workers = 0
        self.workers: List[asyncio.Task] = []
        self._running = False
        self._queue: Optional[PriorityRequestQueue] = None
    
    async def start(self, queue: PriorityRequestQueue):
        """Start the worker pool"""
        self._queue = queue
        self._running = True
        
        for i in range(self.current_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self.workers.append(worker)
        
        logger.info(f"Worker pool started with {self.current_workers} workers")
    
    async def stop(self):
        """Stop the worker pool"""
        self._running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("Worker pool stopped")
    
    async def _worker_loop(self, worker_id: int):
        """Worker loop to process requests"""
        while self._running:
            try:
                request = await self._queue.dequeue()
                if request:
                    self.active_workers += 1
                    try:
                        await request.handler(*request.args, **request.kwargs)
                    except Exception as e:
                        logger.error(f"Worker {worker_id} error: {e}")
                    finally:
                        self.active_workers -= 1
                else:
                    await asyncio.sleep(0.01)  # Prevent busy loop
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} fatal error: {e}")
                await asyncio.sleep(1)
    
    def scale(self, health: SystemHealth, queue_stats: dict):
        """Scale workers based on health and queue depth"""
        queue_depth = queue_stats.get("total_queued", 0)
        
        if health == SystemHealth.OVERLOADED or queue_depth > 1000:
            # Scale up
            new_workers = min(self.max_workers, self.current_workers + 10)
        elif health == SystemHealth.HEALTHY and queue_depth < 100:
            # Scale down
            new_workers = max(self.min_workers, self.current_workers - 5)
        else:
            new_workers = self.current_workers
        
        if new_workers != self.current_workers:
            logger.info(f"Scaling workers: {self.current_workers} -> {new_workers}")
            self.current_workers = new_workers
    
    def get_stats(self) -> dict:
        return {
            "current_workers": self.current_workers,
            "active_workers": self.active_workers,
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
            "utilization": (self.active_workers / self.current_workers * 100) if self.current_workers > 0 else 0
        }

# ============== AI Supervisor ==============

class AISupervisor:
    """
    Central AI Supervisor that orchestrates all scaling and load management
    Designed to handle up to 3000 concurrent users
    """
    
    def __init__(self):
        # Components
        self.request_queue = PriorityRequestQueue(max_size=5000)
        self.rate_limiter = AdaptiveRateLimiter(
            base_rate=1000,
            min_rate=100,
            max_rate=3000
        )
        self.worker_pool = WorkerPool(
            min_workers=10,
            max_workers=100
        )
        
        # Circuit breakers for different services
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            "database": CircuitBreaker("database", failure_threshold=5),
            "cache": CircuitBreaker("cache", failure_threshold=10),
            "external_api": CircuitBreaker("external_api", failure_threshold=3),
            "ai_service": CircuitBreaker("ai_service", failure_threshold=3)
        }
        
        # Metrics
        self.metrics = RequestMetrics()
        self.endpoint_metrics: Dict[str, RequestMetrics] = {}
        
        # State
        self.health = SystemHealth.HEALTHY
        self.started = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.health_check_interval = 5.0  # seconds
        self.metrics_window = 60.0  # seconds for metrics calculation
        
        logger.info("AI Supervisor initialized")
    
    async def start(self):
        """Start the AI Supervisor"""
        if self.started:
            return
        
        self.started = True
        await self.worker_pool.start(self.request_queue)
        self._monitor_task = asyncio.create_task(self._health_monitor())
        logger.info("AI Supervisor started - ready for up to 3000 concurrent users")
    
    async def stop(self):
        """Stop the AI Supervisor"""
        self.started = False
        if self._monitor_task:
            self._monitor_task.cancel()
        await self.worker_pool.stop()
        logger.info("AI Supervisor stopped")
    
    async def process_request(
        self,
        handler: Callable,
        *args,
        priority: RequestPriority = RequestPriority.NORMAL,
        service: str = "default",
        timeout: float = 30.0,
        **kwargs
    ) -> Any:
        """
        Process a request through the AI Supervisor
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Check circuit breaker
        circuit = self.circuit_breakers.get(service, self.circuit_breakers["database"])
        if not circuit.can_execute():
            self.metrics.failed_requests += 1
            raise Exception(f"Service {service} circuit breaker is OPEN")
        
        # Check rate limit
        if not await self.rate_limiter.acquire():
            # Queue the request instead of rejecting
            request = QueuedRequest(
                id=request_id,
                priority=priority,
                created_at=start_time,
                handler=handler,
                args=args,
                kwargs=kwargs,
                timeout=timeout
            )
            
            if await self.request_queue.enqueue(request):
                logger.debug(f"Request {request_id} queued (priority: {priority.name})")
                return {"status": "queued", "request_id": request_id}
            else:
                self.metrics.failed_requests += 1
                raise Exception("System overloaded - request queue full")
        
        # Execute immediately
        try:
            self.metrics.total_requests += 1
            result = await handler(*args, **kwargs)
            
            # Record success
            elapsed = (time.time() - start_time) * 1000
            self.metrics.successful_requests += 1
            self.metrics.response_times.append(elapsed)
            circuit.record_success()
            
            return result
            
        except Exception as e:
            self.metrics.failed_requests += 1
            circuit.record_failure()
            raise
    
    async def _health_monitor(self):
        """Background task to monitor system health and adjust resources"""
        while self.started:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Calculate health score
                health_score = self._calculate_health_score()
                old_health = self.health
                
                if health_score >= 90:
                    self.health = SystemHealth.HEALTHY
                elif health_score >= 70:
                    self.health = SystemHealth.DEGRADED
                elif health_score >= 50:
                    self.health = SystemHealth.CRITICAL
                else:
                    self.health = SystemHealth.OVERLOADED
                
                if self.health != old_health:
                    logger.info(f"System health changed: {old_health.value} -> {self.health.value} (score: {health_score:.1f})")
                
                # Adjust resources based on health
                self.rate_limiter.adjust_rate(self.health, self.metrics)
                self.worker_pool.scale(self.health, self.request_queue.get_stats())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        scores = []
        
        # Success rate (weight: 40%)
        success_score = self.metrics.success_rate
        scores.append(success_score * 0.4)
        
        # Response time (weight: 30%)
        avg_time = self.metrics.avg_response_time
        if avg_time < 100:
            time_score = 100
        elif avg_time < 500:
            time_score = 100 - ((avg_time - 100) / 4)
        elif avg_time < 1000:
            time_score = 50 - ((avg_time - 500) / 10)
        else:
            time_score = max(0, 50 - ((avg_time - 1000) / 20))
        scores.append(time_score * 0.3)
        
        # Queue depth (weight: 20%)
        queue_stats = self.request_queue.get_stats()
        queue_ratio = queue_stats["total_queued"] / queue_stats["max_size"]
        queue_score = max(0, 100 - (queue_ratio * 100))
        scores.append(queue_score * 0.2)
        
        # Circuit breaker health (weight: 10%)
        open_circuits = sum(
            1 for cb in self.circuit_breakers.values()
            if cb.state != CircuitState.CLOSED
        )
        circuit_score = 100 - (open_circuits * 25)
        scores.append(max(0, circuit_score) * 0.1)
        
        return sum(scores)
    
    def get_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            "health": self.health.value,
            "health_score": self._calculate_health_score(),
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": f"{self.metrics.success_rate:.1f}%",
                "avg_response_time_ms": f"{self.metrics.avg_response_time:.1f}",
                "p95_response_time_ms": f"{self.metrics.p95_response_time:.1f}"
            },
            "rate_limiter": self.rate_limiter.get_stats(),
            "queue": self.request_queue.get_stats(),
            "workers": self.worker_pool.get_stats(),
            "circuit_breakers": {
                name: cb.get_status()
                for name, cb in self.circuit_breakers.items()
            },
            "capacity": {
                "max_concurrent_users": 3000,
                "current_rate_limit": self.rate_limiter.current_rate,
                "queue_capacity": self.request_queue.max_size - self.request_queue.total_queued
            }
        }

# ============== Global Instance ==============
ai_supervisor = AISupervisor()

# ============== Decorators ==============

def supervised(
    priority: RequestPriority = RequestPriority.NORMAL,
    service: str = "default",
    timeout: float = 30.0
):
    """
    Decorator to run a function through the AI Supervisor
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await ai_supervisor.process_request(
                func,
                *args,
                priority=priority,
                service=service,
                timeout=timeout,
                **kwargs
            )
        return wrapper
    return decorator

# ============== Export ==============
__all__ = [
    'AISupervisor',
    'ai_supervisor',
    'RequestPriority',
    'CircuitState',
    'SystemHealth',
    'supervised'
]
