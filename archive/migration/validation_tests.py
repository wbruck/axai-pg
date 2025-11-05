from typing import Any, Dict, List
import pytest
from sqlalchemy.orm import Session
from ..config.database import DatabaseManager
from ..config.environments import Environments
from ..repositories.repository_factory import RepositoryFactory as PythonFactory
from ...typescript.data import DataAccessFactory as TypeScriptFactory
from ..models.document import Document

class MigrationValidator:
    """Validates data access between TypeScript and Python implementations."""
    
    def __init__(self):
        self.py_factory = PythonFactory.get_instance()
        self.ts_factory = TypeScriptFactory.getInstance()
        
    async def compare_document_operations(self) -> Dict[str, bool]:
        """Compare document operations between implementations."""
        results = {
            "read_match": False,
            "write_match": False,
            "query_match": False,
            "transaction_match": False
        }
        
        # Get repositories
        py_repo = self.py_factory.get_repository(Document)
        ts_repo = self.ts_factory.getDocumentRepository()
        
        # Test document creation
        test_doc = {
            "title": "Migration Test",
            "content": "Testing TypeScript to Python migration",
            "owner_id": 1,
            "org_id": 1
        }
        
        # Compare writes
        py_doc = await py_repo.create(test_doc)
        ts_doc = await ts_repo.create(test_doc)
        results["write_match"] = self._compare_documents(py_doc, ts_doc)
        
        # Compare reads
        py_read = await py_repo.find_by_id(py_doc.id)
        ts_read = await ts_repo.findById(ts_doc.id)
        results["read_match"] = self._compare_documents(py_read, ts_read)
        
        # Compare queries
        py_query = await py_repo.find_many({"owner_id": 1})
        ts_query = await ts_repo.findMany({"owner_id": 1})
        results["query_match"] = self._compare_document_lists(py_query, ts_query)
        
        # Compare transactions
        async def test_transaction(repo: Any) -> bool:
            try:
                async with repo.transaction() as txn:
                    doc1 = await repo.create({"title": "Doc 1", "owner_id": 1})
                    doc2 = await repo.create({"title": "Doc 2", "owner_id": 1})
                    return True
            except:
                return False
        
        py_txn = await test_transaction(py_repo)
        ts_txn = await test_transaction(ts_repo)
        results["transaction_match"] = py_txn == ts_txn
        
        return results
    
    def _compare_documents(self, py_doc: Any, ts_doc: Any) -> bool:
        """Compare core document attributes."""
        if not py_doc or not ts_doc:
            return False
            
        return all([
            py_doc.title == ts_doc.title,
            py_doc.content == ts_doc.content,
            py_doc.owner_id == ts_doc.owner_id,
            py_doc.org_id == ts_doc.org_id
        ])
    
    def _compare_document_lists(self, py_docs: List[Any], ts_docs: List[Any]) -> bool:
        """Compare lists of documents."""
        if len(py_docs) != len(ts_docs):
            return False
            
        return all(
            self._compare_documents(py_doc, ts_doc)
            for py_doc, ts_doc in zip(py_docs, ts_docs)
        )

@pytest.fixture
def validator():
    """Create and configure validator instance."""
    # Set up test database connection
    config = Environments.get_test_config()
    DatabaseManager.initialize(config.conn_config, config.pool_config)
    return MigrationValidator()

@pytest.mark.asyncio
async def test_document_operations(validator):
    """Test document operations between implementations."""
    results = await validator.compare_document_operations()
    
    # All operations should match
    assert all(results.values()), f"Migration validation failed: {results}"

@pytest.mark.asyncio
async def test_performance_comparison(validator):
    """Compare performance between implementations."""
    import time
    
    py_repo = validator.py_factory.get_repository(Document)
    ts_repo = validator.ts_factory.getDocumentRepository()
    
    # Measure write performance
    py_start = time.time()
    await py_repo.create({"title": "Performance Test", "owner_id": 1})
    py_duration = time.time() - py_start
    
    ts_start = time.time()
    await ts_repo.create({"title": "Performance Test", "owner_id": 1})
    ts_duration = time.time() - ts_start
    
    # Python implementation should be within 20% of TypeScript performance
    assert py_duration <= ts_duration * 1.2, "Python performance exceeds threshold"

@pytest.mark.asyncio
async def test_error_handling(validator):
    """Compare error handling between implementations."""
    py_repo = validator.py_factory.get_repository(Document)
    ts_repo = validator.ts_factory.getDocumentRepository()
    
    # Test invalid operations
    async def test_invalid_create(repo):
        try:
            await repo.create({})  # Missing required fields
            return False
        except:
            return True
    
    py_error = await test_invalid_create(py_repo)
    ts_error = await test_invalid_create(ts_repo)
    
    assert py_error == ts_error, "Error handling behavior differs"
