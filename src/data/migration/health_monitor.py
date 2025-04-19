import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import psutil
import json
from pathlib import Path
from ..config.database import DatabaseManager
from ..repositories.repository_factory import RepositoryFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitors database and application health during migration."""
    
    def __init__(self):
        self.db_manager = DatabaseManager.get_instance()
        self.factory = RepositoryFactory.get_instance()
        self.metrics: Dict[str, Any] = {}
        self.alert_thresholds = {
            "connection_errors": 3,
            "response_time_ms": 1000,
            "cpu_percent": 80,
            "memory_percent": 80,
            "error_rate": 0.01
        }
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous health monitoring."""
        logger.info("Starting health monitoring...")
        
        while True:
            try:
                # Collect metrics
                current_metrics = await self._collect_metrics()
                self._update_metrics(current_metrics)
                
                # Check for issues
                issues = self._check_health(current_metrics)
                if issues:
                    await self._handle_health_issues(issues)
                
                # Save metrics
                await self._save_metrics()
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current health metrics."""
        metrics = {
            "timestamp": datetime.now(),
            "database": await self._get_database_metrics(),
            "system": self._get_system_metrics(),
            "application": await self._get_application_metrics()
        }
        return metrics
    
    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Collect database-specific metrics."""
        engine = self.db_manager.engine
        pool = engine.pool
        
        return {
            "pool_size": pool.size(),
            "checkedin": pool.checkedin(),
            "checkedout": pool.checkedout(),
            "overflow": pool.overflow(),
            "connection_errors": await self._test_connections(),
            "response_time_ms": await self._measure_db_response()
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    async def _get_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics."""
        metrics = {}
        
        # Collect metrics from all repositories
        for repo_name, repo in self.factory._repositories.items():
            repo_metrics = self.factory.get_metrics(repo_name)
            if repo_metrics:
                metrics[repo_name] = {
                    "operation_count": repo_metrics.operation_count,
                    "error_count": repo_metrics.error_count,
                    "slow_query_count": repo_metrics.slow_query_count,
                    "avg_operation_time": repo_metrics.avg_operation_time
                }
        
        return metrics
    
    async def _test_connections(self) -> int:
        """Test database connections and return error count."""
        error_count = 0
        engine = self.db_manager.engine
        
        for _ in range(3):  # Test multiple connections
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
            except Exception as e:
                error_count += 1
                logger.error(f"Connection test failed: {str(e)}")
        
        return error_count
    
    async def _measure_db_response(self) -> float:
        """Measure database response time in milliseconds."""
        start = datetime.now()
        
        try:
            engine = self.db_manager.engine
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            
            duration = datetime.now() - start
            return duration.total_seconds() * 1000
            
        except Exception as e:
            logger.error(f"Response time measurement failed: {str(e)}")
            return float('inf')
    
    def _check_health(self, metrics: Dict[str, Any]) -> List[str]:
        """Check metrics against thresholds."""
        issues = []
        
        # Check database metrics
        db_metrics = metrics["database"]
        if db_metrics["connection_errors"] >= self.alert_thresholds["connection_errors"]:
            issues.append("High database connection error rate")
        if db_metrics["response_time_ms"] >= self.alert_thresholds["response_time_ms"]:
            issues.append("Slow database response time")
        
        # Check system metrics
        sys_metrics = metrics["system"]
        if sys_metrics["cpu_percent"] >= self.alert_thresholds["cpu_percent"]:
            issues.append("High CPU usage")
        if sys_metrics["memory_percent"] >= self.alert_thresholds["memory_percent"]:
            issues.append("High memory usage")
        
        # Check application metrics
        app_metrics = metrics["application"]
        for repo_name, repo_metrics in app_metrics.items():
            error_rate = repo_metrics["error_count"] / repo_metrics["operation_count"] if repo_metrics["operation_count"] > 0 else 0
            if error_rate >= self.alert_thresholds["error_rate"]:
                issues.append(f"High error rate in {repo_name} repository")
        
        return issues
    
    async def _handle_health_issues(self, issues: List[str]) -> None:
        """Handle detected health issues."""
        logger.warning("Health issues detected:")
        for issue in issues:
            logger.warning(f"- {issue}")
        
        # Save issue report
        report = {
            "timestamp": datetime.now(),
            "issues": issues,
            "metrics": self.metrics
        }
        
        report_file = Path("health_issues.json")
        with report_file.open("a") as f:
            json.dump(report, f, default=str)
            f.write("\n")
    
    def _update_metrics(self, current_metrics: Dict[str, Any]) -> None:
        """Update stored metrics history."""
        self.metrics[current_metrics["timestamp"].isoformat()] = current_metrics
        
        # Keep only last 24 hours of metrics
        cutoff = datetime.now() - timedelta(hours=24)
        self.metrics = {
            ts: metrics for ts, metrics in self.metrics.items()
            if datetime.fromisoformat(ts) > cutoff
        }
    
    async def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            metrics_file = Path("health_metrics.json")
            with metrics_file.open("w") as f:
                json.dump(self.metrics, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")

if __name__ == "__main__":
    async def main():
        monitor = HealthMonitor()
        await monitor.start_monitoring()
    
    asyncio.run(main())
