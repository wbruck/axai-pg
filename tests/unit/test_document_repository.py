import pytest
from unittest.mock import patch
from src.axai_pg.data.repositories.document_repository import DocumentRepository
from src.axai_pg.data.repositories.decorators import track_metrics
from src.axai_pg.data.models.document import Document
from src.axai_pg.data.models.summary import Summary
from src.axai_pg.data.models.topic import Topic

class TestDocumentRepository:
    @pytest.fixture
    def document_repo(self, mock_db_session, mock_metrics, mock_cache):
        return DocumentRepository(mock_db_session)

    def test_find_by_organization(self, document_repo, mock_db_session, mock_document):
        """Test basic organization document retrieval."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        
        # Execute
        result = document_repo.find_by_organization(1)
        
        # Verify
        assert result == [mock_document]
        mock_db_session.query.assert_called_once_with(Document)
        mock_db_session.filter.assert_called_once()

    def test_find_by_owner(self, document_repo, mock_db_session, mock_document):
        """Test document retrieval by owner."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        
        # Execute
        result = document_repo.find_by_owner(1)
        
        # Verify
        assert result == [mock_document]
        mock_db_session.query.assert_called_once_with(Document)
        mock_db_session.filter.assert_called_once()

    def test_find_by_topic(self, document_repo, mock_db_session, mock_document, mock_topic):
        """Test document-topic relationships."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        
        # Execute
        result = document_repo.find_by_topic(1)
        
        # Verify
        assert result == [mock_document]
        mock_db_session.query.assert_called_once_with(Document)
        mock_db_session.filter.assert_called_once()

    def test_find_related_documents(self, document_repo, mock_db_session, mock_document):
        """Test direct relationships."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        
        # Execute
        result = document_repo.find_related_documents(1)
        
        # Verify
        assert result == [mock_document]
        mock_db_session.query.assert_called_once_with(Document)
        mock_db_session.filter.assert_called_once()

    def test_create_with_summary(self, document_repo, mock_db_session, mock_document, mock_summary):
        """Test document creation with summary."""
        # Setup
        mock_db_session.refresh.return_value = mock_document
        
        # Execute
        result = document_repo.create_with_summary(
            {"title": "Test Doc", "content": "Test Content"},
            {"content": "Test Summary"}
        )
        
        # Verify
        assert result == mock_document
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_update_with_version(self, document_repo, mock_db_session, mock_document):
        """Test version creation."""
        # Setup
        mock_db_session.first.return_value = mock_document
        
        # Execute
        result = document_repo.update_with_version(
            1,
            {"title": "Updated Title"},
            "Test change"
        )
        
        # Verify
        assert result == mock_document
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_search(self, document_repo, mock_db_session, mock_document):
        """Test basic search."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        
        # Execute
        result = document_repo.search("test", 1)
        
        # Verify
        assert result == [mock_document]
        mock_db_session.query.assert_called_once_with(Document)
        mock_db_session.filter.assert_called()

    def test_cache_behavior(self, document_repo, mock_db_session, mock_cache, mock_document):
        """Test cache TTL."""
        # Setup
        mock_db_session.all.return_value = [mock_document]
        mock_cache.get.return_value = [mock_document]
        
        # Execute
        result = document_repo.find_by_organization(1)
        
        # Verify
        assert result == [mock_document]
        mock_cache.get.assert_called_once()
        mock_db_session.query.assert_not_called()  # Should use cache 