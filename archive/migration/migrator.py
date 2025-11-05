import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import inspect
from ..config.database import DatabaseManager
from ..config.environments import Environments
from ..repositories.repository_factory import RepositoryFactory as PythonFactory
from ...typescript.data import DataAccessFactory as TypeScriptFactory
from ..models.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Manages the migration from TypeScript to Python data access layer."""
    
    def __init__(self):
        self.py_factory = PythonFactory.get_instance()
        self.ts_factory = TypeScriptFactory.getInstance()
        self.stats: Dict[str, Any] = {
            "started_at": None,
            "completed_at": None,
            "errors": [],
            "metrics": {}
        }
    
    async def execute_migration(self) -> bool:
        """Execute the complete migration process."""
        self.stats["started_at"] = datetime.now()
        success = False
        
        try:
            # Phase 1: Verification
            logger.info("Starting pre-migration verification...")
            if not await self._verify_implementations():
                raise RuntimeError("Pre-migration verification failed")
            
            # Phase 2: Data Migration
            logger.info("Starting data migration...")
            if not await self._migrate_data():
                raise RuntimeError("Data migration failed")
            
            # Phase 3: Validation
            logger.info("Starting post-migration validation...")
            if not await self._validate_migration():
                raise RuntimeError("Post-migration validation failed")
            
            success = True
            logger.info("Migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.stats["errors"].append(str(e))
            await self._execute_rollback()
            
        finally:
            self.stats["completed_at"] = datetime.now()
            await self._save_migration_stats()
            
        return success
    
    async def _verify_implementations(self) -> bool:
        """Verify Python implementation matches TypeScript functionality."""
        try:
            # Verify connection
            py_conn = await self._check_connection(self.py_factory)
            ts_conn = await self._check_connection(self.ts_factory)
            if not (py_conn and ts_conn):
                return False
            
            # Verify repositories
            if not await self._verify_repositories():
                return False
            
            # Verify transactions
            if not await self._verify_transactions():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Implementation verification failed: {str(e)}")
            return False
    
    async def _migrate_data(self) -> bool:
        """Perform the actual data migration."""
        try:
            # Get document counts for verification
            ts_docs = await self._count_documents(self.ts_factory)
            
            # Migrate in batches
            batch_size = 100
            offset = 0
            
            while True:
                docs = await self._get_document_batch(offset, batch_size)
                if not docs:
                    break
                
                if not await self._migrate_document_batch(docs):
                    return False
                
                offset += batch_size
                
            # Verify counts match
            py_docs = await self._count_documents(self.py_factory)
            if py_docs != ts_docs:
                raise RuntimeError(f"Document count mismatch: TS={ts_docs}, PY={py_docs}")
            
            return True
            
        except Exception as e:
            logger.error(f"Data migration failed: {str(e)}")
            return False
    
    async def _validate_migration(self) -> bool:
        """Validate the migration results."""
        try:
            # Compare random sample of documents
            sample_size = 100
            if not await self._validate_document_sample(sample_size):
                return False
            
            # Validate relationships
            if not await self._validate_relationships():
                return False
            
            # Validate performance
            if not await self._validate_performance():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Migration validation failed: {str(e)}")
            return False
    
    async def _execute_rollback(self) -> None:
        """Execute rollback procedure on migration failure."""
        logger.warning("Executing migration rollback...")
        try:
            # Restore original TypeScript connections
            self.ts_factory.resetConnections()
            
            # Clear any partial Python data
            await self._clear_python_data()
            
            logger.info("Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
    
    async def _save_migration_stats(self) -> None:
        """Save migration statistics and metrics."""
        try:
            duration = (self.stats["completed_at"] - self.stats["started_at"]).total_seconds()
            self.stats["duration_seconds"] = duration
            
            # Add final metrics
            self.stats["metrics"].update({
                "total_documents": await self._count_documents(self.py_factory),
                "error_count": len(self.stats["errors"]),
                "success": len(self.stats["errors"]) == 0
            })
            
            # Save stats to file
            import json
            from pathlib import Path
            
            stats_file = Path("migration_stats.json")
            with stats_file.open("w") as f:
                json.dump(self.stats, f, default=str, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save migration stats: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def main():
        migrator = DatabaseMigrator()
        success = await migrator.execute_migration()
        if not success:
            logger.error("Migration failed - check logs for details")
            exit(1)
    
    asyncio.run(main())
