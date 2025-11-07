"""
Integration tests for CRUD operations.

These tests verify that all model CRUD operations work correctly with a real
PostgreSQL database, including relationships and queries.
"""

import pytest
import uuid
from axai_pg import Organization, User, Document, Summary, Topic, DocumentTopic


@pytest.mark.integration
@pytest.mark.db
class TestCRUDOperations:
    """Test CRUD operations for all models."""

    def test_create_organization_and_user(self, db_session):
        """Test creating organization and user with relationships."""
        # Create organization
        org = Organization(name="Test Organization")
        db_session.add(org)
        db_session.flush()

        assert org.id is not None
        assert isinstance(org.id, uuid.UUID)
        assert org.name == "Test Organization"

        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.org_id, uuid.UUID)
        assert user.org_id == org.id
        assert user.username == "testuser"

        # Verify relationship
        assert user.organization.id == org.id
        assert org.users.first().id == user.id

    def test_create_document_with_summary(self, db_session):
        """Test creating document with summary and relationships."""
        # Create organization and user first
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        # Create document
        content = "This is a test document content"
        document = Document(
            title="Test Document",
            content=content,
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft",
            filename="test_document.txt",
            file_path="/test/path/test_document.txt",
            size=len(content),
            content_type="text/plain"
        )
        db_session.add(document)
        db_session.flush()

        assert document.id is not None
        assert isinstance(document.id, uuid.UUID)
        assert isinstance(document.owner_id, uuid.UUID)
        assert isinstance(document.org_id, uuid.UUID)
        assert document.owner_id == user.id
        assert document.org_id == org.id

        # Create summary
        summary = Summary(
            document_id=document.id,
            content="This is a summary of the test document",
            summary_type="abstract",
            tool_agent="test-agent",
            confidence_score=0.95
        )
        db_session.add(summary)
        db_session.flush()

        assert summary.id is not None
        assert isinstance(summary.id, uuid.UUID)
        assert isinstance(summary.document_id, uuid.UUID)
        assert summary.document_id == document.id
        assert summary.confidence_score == 0.95

    def test_create_topic_and_associate_with_document(self, db_session):
        """Test creating topic and associating with document via junction table."""
        # Create organization, user, and document
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        content = "This is a test document content"
        document = Document(
            title="Test Document",
            content=content,
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft",
            filename="test_document.txt",
            file_path="/test/path/test_document.txt",
            size=len(content),
            content_type="text/plain"
        )
        db_session.add(document)
        db_session.flush()

        # Create topic
        topic = Topic(
            name="Test Topic",
            description="A test topic",
            keywords=["test", "example"],
            extraction_method="manual",
            global_importance=0.8
        )
        db_session.add(topic)
        db_session.flush()

        assert topic.id is not None
        assert isinstance(topic.id, uuid.UUID)
        assert topic.name == "Test Topic"
        assert topic.keywords == ["test", "example"]

        # Verify document-topic relationship
        doc_topic = DocumentTopic(
            document_id=document.id,
            topic_id=topic.id,
            relevance_score=0.9,
            extracted_by_tool="test-tool"
        )
        db_session.add(doc_topic)
        db_session.flush()

        assert doc_topic.id is not None
        assert isinstance(doc_topic.id, uuid.UUID)
        assert isinstance(doc_topic.document_id, uuid.UUID)
        assert isinstance(doc_topic.topic_id, uuid.UUID)
        assert doc_topic.document_id == document.id
        assert doc_topic.topic_id == topic.id
        assert doc_topic.relevance_score == 0.9

    def test_query_operations(self, db_session):
        """Test various query operations on models."""
        # Create test data
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        content = "This is a test document content"
        document = Document(
            title="Test Document",
            content=content,
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft",
            filename="test_document.txt",
            file_path="/test/path/test_document.txt",
            size=len(content),
            content_type="text/plain"
        )
        db_session.add(document)
        db_session.flush()

        # Test queries
        # Get organization by name
        queried_org = db_session.query(Organization).filter_by(name="Test Org").first()
        assert queried_org.id == org.id
        assert isinstance(queried_org.id, uuid.UUID)

        # Get user by username
        queried_user = db_session.query(User).filter_by(username="testuser").first()
        assert queried_user.id == user.id
        assert isinstance(queried_user.id, uuid.UUID)

        # Get documents for organization
        org_documents = db_session.query(Document).filter_by(org_id=org.id).all()
        assert len(org_documents) == 1
        assert org_documents[0].id == document.id
        assert isinstance(org_documents[0].id, uuid.UUID)

        # Get documents owned by user
        user_documents = db_session.query(Document).filter_by(owner_id=user.id).all()
        assert len(user_documents) == 1
        assert user_documents[0].id == document.id
        assert isinstance(user_documents[0].id, uuid.UUID)

    def test_update_user(self, db_session):
        """Test updating user fields."""
        # Create organization and user
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        user = User(
            username="original_username",
            email="original@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        original_id = user.id

        # Update user
        user.username = "updated_username"
        user.email = "updated@example.com"
        db_session.flush()

        # Verify updates persisted
        updated_user = db_session.query(User).filter_by(id=original_id).first()
        assert updated_user.id == original_id
        assert updated_user.username == "updated_username"
        assert updated_user.email == "updated@example.com"
        assert updated_user.org_id == org.id  # Foreign key unchanged

    def test_update_document_status(self, db_session):
        """Test updating document status and content."""
        # Create organization, user, and document
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        db_session.add(user)
        db_session.flush()

        original_content = "Original content"
        document = Document(
            title="Original Title",
            content=original_content,
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft",
            filename="original.txt",
            file_path="/test/path/original.txt",
            size=len(original_content),
            content_type="text/plain"
        )
        db_session.add(document)
        db_session.flush()

        original_id = document.id

        # Update document
        document.title = "Updated Title"
        document.content = "Updated content with more information"
        document.status = "published"
        db_session.flush()

        # Verify updates persisted
        updated_doc = db_session.query(Document).filter_by(id=original_id).first()
        assert updated_doc.id == original_id
        assert updated_doc.title == "Updated Title"
        assert updated_doc.content == "Updated content with more information"
        assert updated_doc.status == "published"
        assert updated_doc.owner_id == user.id  # Foreign key unchanged
        assert updated_doc.org_id == org.id  # Foreign key unchanged 