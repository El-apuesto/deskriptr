# MONITORING & ALERTING - IMMEDIATE FIX
# Complete visibility into app performance, errors, and health

import time
import psutil
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import Request, Response, APIRouter, Depends
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
import redis
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: PROMETHEUS METRICS SETUP
# =============================================================================

class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        # Create custom registry
        self.registry = CollectorRegistry()
        
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'user_tier'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'user_tier'],
            registry=self.registry
        )
        
        # Business metrics
        self.stories_generated_total = Counter(
            'stories_generated_total',
            'Total stories generated',
            ['genre', 'user_tier', 'success'],
            registry=self.registry
        )
        
        self.users_registered_total = Counter(
            'users_registered_total',
            'Total users registered',
            registry=self.registry
        )
        
        self.api_calls_total = Counter(
            'api_calls_total',
            'Total API calls made',
            ['endpoint', 'user_tier'],
            registry=self.registry
        )
        
        # System metrics
        self.active_users = Gauge(
            'active_users_total',
            'Number of active users',
            registry=self.registry
        )
        
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors occurred',
            ['error_type', 'endpoint', 'user_tier'],
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation'],
            registry=self.registry
        )
        
        # External API metrics
        self.external_api_requests = Counter(
            'external_api_requests_total',
            'Total external API requests',
            ['api_name', 'status'],
            registry=self.registry
        )
        
        self.external_api_duration = Histogram(
            'external_api_duration_seconds',
            'External API request duration in seconds',
            ['api_name'],
            registry=self.registry
        )
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float, user_tier: str = "anonymous"):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            user_tier=user_tier
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint,
            user_tier=user_tier
        ).observe(duration)
    
    def record_story_generation(self, genre: str, user_tier: str, success: bool):
        """Record story generation metrics"""
        self.stories_generated_total.labels(
            genre=genre,
            user_tier=user_tier,
            success="true" if success else "false"
        ).inc()
    
    def record_error(self, error_type: str, endpoint: str, user_tier: str = "anonymous"):
        """Record error metrics"""
        self.errors_total.labels(
            error_type=error_type,
            endpoint=endpoint,
            user_tier=user_tier
        ).inc()
    
    def update_system_metrics(self):
        """Update system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.system_memory_usage.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.system_disk_usage.set(disk_percent)
    
    def update_database_metrics(self, active_connections: int):
        """Update database metrics"""
        self.database_connections.set(active_connections)
    
    def record_external_api_call(self, api_name: str, status: str, duration: float):
        """Record external API call metrics"""
        self.external_api_requests.labels(api_name=api_name, status=status).inc()
        self.external_api_duration.labels(api_name=api_name).observe(duration)

# Global metrics collector
metrics = MetricsCollector()

# =============================================================================
# STEP 2: HEALTH CHECK SYSTEM
# =============================================================================

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    response_time: float
    last_checked: datetime

class HealthChecker:
    """Comprehensive health checking"""
    
    def __init__(self):
        self.checks = {}
        self.redis_client = None
        self.setup_redis()
    
    def setup_redis(self):
        """Setup Redis for health checks"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        except Exception as e:
            logger.error(f"Redis health check setup failed: {str(e)}")
    
    async def check_database(self) -> HealthCheck:
        """Check database health"""
        start_time = time.time()
        
        try:
            # Add your database check here
            # For now, simulate database check
            await asyncio.sleep(0.01)  # Simulate query time
            
            response_time = time.time() - start_time
            
            if response_time > 1.0:
                return HealthCheck(
                    name="database",
                    status=HealthStatus.DEGRADED,
                    message="Database response slow",
                    response_time=response_time,
                    last_checked=datetime.utcnow()
                )
            
            return HealthCheck(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database operational",
                response_time=response_time,
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {str(e)}",
                response_time=time.time() - start_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_redis(self) -> HealthCheck:
        """Check Redis health"""
        start_time = time.time()
        
        try:
            if not self.redis_client:
                return HealthCheck(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message="Redis not configured",
                    response_time=0,
                    last_checked=datetime.utcnow()
                )
            
            # Test Redis connection
            self.redis_client.ping()
            
            response_time = time.time() - start_time
            
            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis operational",
                response_time=response_time,
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthCheck(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis error: {str(e)}",
                response_time=time.time() - start_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_external_apis(self) -> HealthCheck:
        """Check external API health"""
        start_time = time.time()
        
        try:
            # Check Groq API (or other external APIs)
            # For now, simulate API check
            await asyncio.sleep(0.05)  # Simulate API call time
            
            response_time = time.time() - start_time
            
            if response_time > 5.0:
                return HealthCheck(
                    name="external_apis",
                    status=HealthStatus.DEGRADED,
                    message="External APIs slow",
                    response_time=response_time,
                    last_checked=datetime.utcnow()
                )
            
            return HealthCheck(
                name="external_apis",
                status=HealthStatus.HEALTHY,
                message="External APIs operational",
                response_time=response_time,
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthCheck(
                name="external_apis",
                status=HealthStatus.UNHEALTHY,
                message=f"External API error: {str(e)}",
                response_time=time.time() - start_time,
                last_checked=datetime.utcnow()
            )
    
    async def check_disk_space(self) -> HealthCheck:
        """Check disk space"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            response_time = time.time() - start_time
            
            if disk_percent > 90:
                return HealthCheck(
                    name="disk_space",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Disk usage critical: {disk_percent:.1f}%",
                    response_time=response_time,
                    last_checked=datetime.utcnow()
                )
            elif disk_percent > 80:
                return HealthCheck(
                    name="disk_space",
                    status=HealthStatus.DEGRADED,
                    message=f"Disk usage high: {disk_percent:.1f}%",
                    response_time=response_time,
                    last_checked=datetime.utcnow()
                )
            
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.HEALTHY,
                message=f"Disk usage normal: {disk_percent:.1f}%",
                response_time=response_time,
                last_checked=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check error: {str(e)}",
                response_time=time.time() - start_time,
                last_checked=datetime.utcnow()
            )
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_external_apis(),
            self.check_disk_space()
        )
        
        # Determine overall status
        statuses = [check.status for check in checks]
        
        if HealthStatus.UNHEALTHY in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Update system metrics
        metrics.update_system_metrics()
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                check.name: {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time": check.response_time,
                    "last_checked": check.last_checked.isoformat()
                }
                for check in checks
            },
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                "uptime": time.time() - start_time
            }
        }

# Global health checker
health_checker = HealthChecker()
start_time = time.time()

# =============================================================================
# STEP 3: ALERTING SYSTEM
# =============================================================================

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]

class AlertManager:
    """Alert management and notification"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = self.setup_alert_rules()
        self.notification_channels = []
    
    def setup_alert_rules(self) -> List[Dict]:
        """Setup alerting rules"""
        return [
            {
                "name": "high_error_rate",
                "condition": "error_rate > 0.1",  # 10% error rate
                "level": AlertLevel.ERROR,
                "message": "High error rate detected",
                "cooldown": 300  # 5 minutes
            },
            {
                "name": "slow_response_time",
                "condition": "avg_response_time > 2.0",  # 2 seconds
                "level": AlertLevel.WARNING,
                "message": "Slow response times detected",
                "cooldown": 600  # 10 minutes
            },
            {
                "name": "high_cpu_usage",
                "condition": "cpu_usage > 90",
                "level": AlertLevel.CRITICAL,
                "message": "High CPU usage detected",
                "cooldown": 300  # 5 minutes
            },
            {
                "name": "disk_space_critical",
                "condition": "disk_usage > 95",
                "level": AlertLevel.CRITICAL,
                "message": "Critical disk space usage",
                "cooldown": 600  # 10 minutes
            },
            {
                "name": "service_unhealthy",
                "condition": "service_status != 'healthy'",
                "level": AlertLevel.ERROR,
                "message": "Service health check failed",
                "cooldown": 300  # 5 minutes
            }
        ]
    
    def check_alert_conditions(self, metrics_data: Dict[str, Any]) -> List[Alert]:
        """Check alert conditions and generate alerts"""
        alerts = []
        current_time = datetime.utcnow()
        
        for rule in self.alert_rules:
            # Check cooldown
            if self.is_in_cooldown(rule["name"], rule["cooldown"]):
                continue
            
            # Evaluate condition (simplified)
            if self.evaluate_condition(rule["condition"], metrics_data):
                alert = Alert(
                    level=rule["level"],
                    message=rule["message"],
                    source=rule["name"],
                    timestamp=current_time,
                    metadata={
                        "condition": rule["condition"],
                        "metrics": metrics_data
                    }
                )
                
                alerts.append(alert)
                self.alerts.append(alert)
                
                # Send notifications
                self.send_notification(alert)
        
        return alerts
    
    def is_in_cooldown(self, alert_name: str, cooldown_seconds: int) -> bool:
        """Check if alert is in cooldown period"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=cooldown_seconds)
        
        for alert in reversed(self.alerts):
            if alert.source == alert_name and alert.timestamp > cutoff_time:
                return True
        
        return False
    
    def evaluate_condition(self, condition: str, metrics_data: Dict[str, Any]) -> bool:
        """Evaluate alert condition (simplified)"""
        # This would be more sophisticated in production
        if "error_rate > 0.1" in condition:
            return metrics_data.get("error_rate", 0) > 0.1
        elif "avg_response_time > 2.0" in condition:
            return metrics_data.get("avg_response_time", 0) > 2.0
        elif "cpu_usage > 90" in condition:
            return metrics_data.get("cpu_usage", 0) > 90
        elif "disk_usage > 95" in condition:
            return metrics_data.get("disk_usage", 0) > 95
        elif "service_status != 'healthy'" in condition:
            return metrics_data.get("service_status") != "healthy"
        
        return False
    
    def send_notification(self, alert: Alert):
        """Send alert notification"""
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }.get(alert.level, logging.INFO)
        
        logger.log(
            log_level,
            f"ALERT: {alert.message}",
            extra={
                "alert_level": alert.level.value,
                "alert_source": alert.source,
                "alert_metadata": alert.metadata
            }
        )
        
        # Add other notification channels (email, Slack, etc.)
        # For now, just log the alert
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp > cutoff_time]

# Global alert manager
alert_manager = AlertManager()

# =============================================================================
# STEP 4: MONITORING MIDDLEWARE
# =============================================================================

async def monitoring_middleware(request: Request, call_next):
    """Monitoring middleware for all requests"""
    start_time = time.time()
    
    # Get user info
    user_tier = getattr(request.state, 'subscription_tier', 'anonymous')
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            user_tier=user_tier
        )
        
        # Add monitoring headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = getattr(request.state, 'request_id', 'unknown')
        
        return response
        
    except Exception as e:
        # Record error metrics
        duration = time.time() - start_time
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration,
            user_tier=user_tier
        )
        
        metrics.record_error(
            error_type=type(e).__name__,
            endpoint=request.url.path,
            user_tier=user_tier
        )
        
        # Check for alert conditions
        alert_data = {
            "error_rate": 1.0,  # This would be calculated from recent metrics
            "avg_response_time": duration,
            "cpu_usage": psutil.cpu_percent(),
            "disk_usage": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        }
        
        alert_manager.check_alert_conditions(alert_data)
        
        raise

# =============================================================================
# STEP 5: API ENDPOINTS
# =============================================================================

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/health")
async def health_check():
    """Basic health check"""
    health = await health_checker.get_overall_health()
    
    status_code = 200
    if health["status"] == "unhealthy":
        status_code = 503
    elif health["status"] == "degraded":
        status_code = 200  # Still serve traffic but warn
    
    return JSONResponse(
        status_code=status_code,
        content=health
    )

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with full metrics"""
    health = await health_checker.get_overall_health()
    
    # Add more detailed metrics
    health["detailed_metrics"] = {
        "process": {
            "pid": os.getpid(),
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "cpu_percent": psutil.Process().cpu_percent(),
            "create_time": datetime.fromtimestamp(psutil.Process().create_time()).isoformat()
        },
        "system": {
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
    }
    
    return health

@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics_data = generate_latest(metrics.registry)
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/alerts")
async def get_alerts(hours: int = 24):
    """Get recent alerts"""
    alerts = alert_manager.get_recent_alerts(hours)
    
    return {
        "alerts": [
            {
                "level": alert.level.value,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            for alert in alerts
        ],
        "total": len(alerts)
    }

@router.get("/stats")
async def get_stats():
    """Get application statistics"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - start_time,
        "system": {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        },
        "application": {
            "process_id": os.getpid(),
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "threads": psutil.Process().num_threads(),
            "open_files": len(psutil.Process().open_files())
        }
    }

# =============================================================================
# STEP 6: PERFORMANCE MONITORING
# =============================================================================

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.slow_queries = []
        self.performance_issues = []
    
    def record_slow_query(self, query: str, duration: float, threshold: float = 1.0):
        """Record slow database query"""
        if duration > threshold:
            self.slow_queries.append({
                "query": query,
                "duration": duration,
                "timestamp": datetime.utcnow()
            })
            
            logger.warning(
                f"Slow query detected: {duration:.3f}s",
                extra={
                    "query": query,
                    "duration": duration,
                    "threshold": threshold
                }
            )
    
    def check_performance_issues(self):
        """Check for performance issues"""
        # Check memory usage
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 85:
            self.performance_issues.append({
                "type": "high_memory",
                "value": memory_percent,
                "timestamp": datetime.utcnow()
            })
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            self.performance_issues.append({
                "type": "high_cpu",
                "value": cpu_percent,
                "timestamp": datetime.utcnow()
            })
        
        # Check disk space
        disk_percent = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        if disk_percent > 90:
            self.performance_issues.append({
                "type": "high_disk",
                "value": disk_percent,
                "timestamp": datetime.utcnow()
            })

# Global performance monitor
performance_monitor = PerformanceMonitor()

# =============================================================================
# STEP 7: ENVIRONMENT SETUP
# =============================================================================

ENVIRONMENT_CONFIG = {
    "METRICS_ENABLED": True,
    "HEALTH_CHECK_ENABLED": True,
    "ALERTING_ENABLED": True,
    "PERFORMANCE_MONITORING": True,
    "PROMETHEUS_PORT": 9090,
    "GRAFANA_PORT": 3000
}

# =============================================================================
# STEP 8: DEPLOYMENT INSTRUCTIONS
# =============================================================================

DEPLOYMENT_STEPS = """
1. Install required packages:
   pip install prometheus-client psutil redis
   
2. Add to your FastAPI app:
   from monitoring_fix import router, monitoring_middleware
   
   # Add monitoring middleware
   app.middleware("http", monitoring_middleware)
   
   # Add monitoring endpoints
   app.include_router(router)
   
3. Setup Prometheus:
   docker run -d --name prometheus -p 9090:9090 prom/prometheus
   
4. Setup Grafana:
   docker run -d --name grafana -p 3000:3000 grafana/grafana
   
5. Configure Prometheus to scrape your app:
   Add to prometheus.yml:
   scrape_configs:
     - job_name: 'story-generator'
       static_configs:
         - targets: ['localhost:8000']
       metrics_path: '/monitoring/metrics'
   
6. Test monitoring:
   - Visit http://localhost:8000/monitoring/health
   - Visit http://localhost:8000/monitoring/metrics
   - Visit http://localhost:9090 for Prometheus
   - Visit http://localhost:3000 for Grafana
"""

# =============================================================================
# STEP 9: EXAMPLE USAGE
# =============================================================================

def example_monitoring_usage():
    """Example of monitoring usage"""
    
    # Record business metrics
    metrics.record_story_generation(genre="fantasy", user_tier="free", success=True)
    metrics.record_external_api_call(api_name="groq", status="success", duration=0.5)
    
    # Record performance issue
    performance_monitor.record_slow_query("SELECT * FROM stories", 1.5)
    
    # Check for alerts
    alert_data = {
        "error_rate": 0.05,
        "avg_response_time": 1.2,
        "cpu_usage": 75,
        "disk_usage": 60
    }
    
    alerts = alert_manager.check_alert_conditions(alert_data)
    print(f"Generated {len(alerts)} alerts")
    
    print("📊 Monitoring system ready!")

if __name__ == "__main__":
    example_monitoring_usage()
