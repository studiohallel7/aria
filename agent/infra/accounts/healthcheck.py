"""
Health Checker - Monitors provider health and availability.
Performs periodic health checks and tracks provider status.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(Enum):
    """Health status of a provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Health information for a provider."""
    provider: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    successful_checks: int = 0
    avg_response_time_ms: float = 0.0
    error_message: Optional[str] = None


class HealthChecker:
    """Monitors provider health with periodic checks."""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.providers: Dict[str, ProviderHealth] = {}
        self._check_callbacks: Dict[str, Callable[[], bool]] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def register_provider(self, provider: str, 
                         health_check_fn: Optional[Callable[[], bool]] = None) -> None:
        """Register a provider for health monitoring."""
        self.providers[provider] = ProviderHealth(provider=provider)
        if health_check_fn:
            self._check_callbacks[provider] = health_check_fn
    
    def unregister_provider(self, provider: str) -> None:
        """Unregister a provider from health monitoring."""
        if provider in self.providers:
            del self.providers[provider]
        if provider in self._check_callbacks:
            del self._check_callbacks[provider]
    
    def check_provider(self, provider: str) -> HealthStatus:
        """Perform a health check on a provider."""
        if provider not in self.providers:
            return HealthStatus.UNKNOWN
        
        health = self.providers[provider]
        health.total_checks += 1
        health.last_check = datetime.now()
        
        # Use custom check function if available
        check_fn = self._check_callbacks.get(provider)
        
        if check_fn:
            try:
                start_time = time.time()
                success = check_fn()
                response_time = (time.time() - start_time) * 1000
                
                if success:
                    self._record_success(health, response_time)
                else:
                    self._record_failure(health, "Health check returned false")
                    
            except Exception as e:
                self._record_failure(health, str(e))
        else:
            # No check function, assume healthy if recently checked
            if health.last_check and (datetime.now() - health.last_check).seconds < 300:
                health.status = HealthStatus.HEALTHY
            else:
                health.status = HealthStatus.UNKNOWN
        
        return health.status
    
    def _record_success(self, health: ProviderHealth, response_time_ms: float) -> None:
        """Record a successful health check."""
        health.consecutive_failures = 0
        health.successful_checks += 1
        health.last_success = datetime.now()
        health.error_message = None
        
        # Update average response time
        n = health.successful_checks
        health.avg_response_time_ms = ((n - 1) * health.avg_response_time_ms + response_time_ms) / n
        
        # Update status
        if health.consecutive_failures == 0:
            health.status = HealthStatus.HEALTHY
    
    def _record_failure(self, health: ProviderHealth, error: str) -> None:
        """Record a failed health check."""
        health.consecutive_failures += 1
        health.last_failure = datetime.now()
        health.error_message = error
        
        # Update status based on failures
        if health.consecutive_failures >= 5:
            health.status = HealthStatus.UNHEALTHY
        elif health.consecutive_failures >= 2:
            health.status = HealthStatus.DEGRADED
        else:
            health.status = HealthStatus.HEALTHY
    
    def get_health(self, provider: str) -> Optional[ProviderHealth]:
        """Get health information for a provider."""
        return self.providers.get(provider)
    
    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health information for all providers."""
        result = {}
        for provider, health in self.providers.items():
            result[provider] = {
                'status': health.status.value,
                'last_check': health.last_check.isoformat() if health.last_check else None,
                'last_success': health.last_success.isoformat() if health.last_success else None,
                'last_failure': health.last_failure.isoformat() if health.last_failure else None,
                'consecutive_failures': health.consecutive_failures,
                'total_checks': health.total_checks,
                'successful_checks': health.successful_checks,
                'success_rate': health.successful_checks / health.total_checks if health.total_checks > 0 else 0,
                'avg_response_time_ms': health.avg_response_time_ms,
                'error_message': health.error_message,
            }
        return result
    
    def is_healthy(self, provider: str) -> bool:
        """Check if a provider is healthy."""
        health = self.providers.get(provider)
        if not health:
            return False
        return health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    def start_background_checks(self) -> None:
        """Start background health checking thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._background_check_loop, daemon=True)
        self._thread.start()
    
    def stop_background_checks(self) -> None:
        """Stop background health checking."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def _background_check_loop(self) -> None:
        """Background loop for periodic health checks."""
        while self._running:
            for provider in list(self.providers.keys()):
                if not self._running:
                    break
                self.check_provider(provider)
            
            time.sleep(self.check_interval)
    
    def mark_unhealthy(self, provider: str, error: str) -> None:
        """Manually mark a provider as unhealthy."""
        if provider in self.providers:
            self._record_failure(self.providers[provider], error)
    
    def mark_healthy(self, provider: str) -> None:
        """Manually mark a provider as healthy."""
        if provider in self.providers:
            health = self.providers[provider]
            health.consecutive_failures = 0
            health.status = HealthStatus.HEALTHY
            health.error_message = None
            health.last_success = datetime.now()