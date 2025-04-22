import asyncio
import logging
import signal
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path
from .migrator import DatabaseMigrator
from .health_monitor import HealthMonitor
from ..config.environments import Environments
from ..config.database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger(__name__)

class MigrationOrchestrator:
    """Orchestrates the TypeScript to Python migration process."""
    
    def __init__(self):
        self.migrator = DatabaseMigrator()
        self.health_monitor = HealthMonitor()
        self.monitor_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    async def start(self):
        """Start the migration process."""
        try:
            # Create migration directory
            migration_dir = Path("migration_logs")
            migration_dir.mkdir(exist_ok=True)
            
            # Initialize database
            self._initialize_database()
            
            # Start health monitoring
            logger.info("Starting health monitoring...")
            self.monitor_task = asyncio.create_task(
                self.health_monitor.start_monitoring(interval_seconds=30)
            )
            
            # Execute migration
            logger.info("Starting migration process...")
            success = await self.migrator.execute_migration()
            
            if success:
                logger.info("Migration completed successfully")
                await self._generate_success_report()
            else:
                logger.error("Migration failed")
                await self._generate_failure_report()
            
        except Exception as e:
            logger.error(f"Migration orchestration failed: {str(e)}")
            await self._generate_failure_report()
            raise
        
        finally:
            await self.shutdown()
    
    def _initialize_database(self):
        """Initialize database connections."""
        # Get production configuration
        config = Environments.get_production_config()
        
        # Initialize database manager
        DatabaseManager.initialize(config.conn_config, config.pool_config)
        
        logger.info("Database connections initialized")
    
    async def _generate_success_report(self):
        """Generate migration success report."""
        report = {
            "status": "success",
            "completed_at": datetime.now(),
            "migration_stats": self.migrator.stats,
            "health_metrics": self.health_monitor.metrics
        }
        
        report_file = Path("migration_logs/success_report.json")
        with report_file.open("w") as f:
            import json
            json.dump(report, f, default=str, indent=2)
        
        logger.info("Success report generated")
    
    async def _generate_failure_report(self):
        """Generate migration failure report."""
        report = {
            "status": "failed",
            "failed_at": datetime.now(),
            "migration_stats": self.migrator.stats,
            "health_metrics": self.health_monitor.metrics,
            "errors": self.migrator.stats.get("errors", [])
        }
        
        report_file = Path("migration_logs/failure_report.json")
        with report_file.open("w") as f:
            import json
            json.dump(report, f, default=str, indent=2)
        
        logger.info("Failure report generated")
    
    async def shutdown(self):
        """Shutdown migration process."""
        if self._shutdown:
            return
            
        self._shutdown = True
        logger.info("Shutting down migration process...")
        
        # Cancel health monitoring
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Migration process shutdown complete")

def handle_signal(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    if orchestrator:
        asyncio.create_task(orchestrator.shutdown())

if __name__ == "__main__":
    # Register signal handlers
    orchestrator = None
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        # Create and start orchestrator
        orchestrator = MigrationOrchestrator()
        asyncio.run(orchestrator.start())
        
        # Exit with success if migration completed
        if orchestrator.migrator.stats.get("errors"):
            sys.exit(1)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)
