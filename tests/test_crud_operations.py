import pytest
import uuid
from axai_pg import (
    Organization, User, Document, Summary, Topic,
    DatabaseManager, PostgresConnectionConfig
)

@pytest.fixture
def db():
    conn_config = PostgresConnectionConfig(
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password="test_password"
    )
    DatabaseManager.initialize(conn_config)
    return DatabaseManager.get_instance()

def test_create_organization_and_user(db):
    with db.session_scope() as session:
        # Create organization
        org = Organization(name="Test Organization")
        session.add(org)
        session.flush()
        
        assert org.id is not None
        assert isinstance(org.id, uuid.UUID)
        assert org.name == "Test Organization"
        
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        session.add(user)
        session.flush()
        
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.org_id, uuid.UUID)
        assert user.org_id == org.id
        assert user.username == "testuser"
        
        # Verify relationship
        assert user.organization.id == org.id
        assert org.users.first().id == user.id

def test_create_document_with_summary(db):
    with db.session_scope() as session:
        # Create organization and user first
        org = Organization(name="Test Org")
        session.add(org)
        session.flush()
        
        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        session.add(user)
        session.flush()
        
        # Create document
        document = Document(
            title="Test Document",
            content="This is a test document content",
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft"
        )
        session.add(document)
        session.flush()
        
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
        session.add(summary)
        session.flush()
        
        assert summary.id is not None
        assert isinstance(summary.id, uuid.UUID)
        assert isinstance(summary.document_id, uuid.UUID)
        assert summary.document_id == document.id
        assert summary.confidence_score == 0.95

def test_create_topic_and_associate_with_document(db):
    with db.session_scope() as session:
        # Create organization, user, and document
        org = Organization(name="Test Org")
        session.add(org)
        session.flush()
        
        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        session.add(user)
        session.flush()
        
        document = Document(
            title="Test Document",
            content="This is a test document content",
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft"
        )
        session.add(document)
        session.flush()
        
        # Create topic
        topic = Topic(
            name="Test Topic",
            description="A test topic",
            keywords=["test", "example"],
            extraction_method="manual",
            global_importance=0.8
        )
        session.add(topic)
        session.flush()
        
        assert topic.id is not None
        assert isinstance(topic.id, uuid.UUID)
        assert topic.name == "Test Topic"
        assert topic.keywords == ["test", "example"]
        
        # Verify document-topic relationship
        from axai_pg import DocumentTopic
        doc_topic = DocumentTopic(
            document_id=document.id,
            topic_id=topic.id,
            relevance_score=0.9,
            extracted_by_tool="test-tool"
        )
        session.add(doc_topic)
        session.flush()
        
        assert doc_topic.id is not None
        assert isinstance(doc_topic.id, uuid.UUID)
        assert isinstance(doc_topic.document_id, uuid.UUID)
        assert isinstance(doc_topic.topic_id, uuid.UUID)
        assert doc_topic.document_id == document.id
        assert doc_topic.topic_id == topic.id
        assert doc_topic.relevance_score == 0.9

def test_query_operations(db):
    with db.session_scope() as session:
        # Create test data
        org = Organization(name="Test Org")
        session.add(org)
        session.flush()
        
        user = User(
            username="testuser",
            email="test@example.com",
            org_id=org.id
        )
        session.add(user)
        session.flush()
        
        document = Document(
            title="Test Document",
            content="This is a test document content",
            owner_id=user.id,
            org_id=org.id,
            document_type="text",
            status="draft"
        )
        session.add(document)
        session.flush()
        
        # Test queries
        # Get organization by name
        queried_org = session.query(Organization).filter_by(name="Test Org").first()
        assert queried_org.id == org.id
        assert isinstance(queried_org.id, uuid.UUID)
        
        # Get user by username
        queried_user = session.query(User).filter_by(username="testuser").first()
        assert queried_user.id == user.id
        assert isinstance(queried_user.id, uuid.UUID)
        
        # Get documents for organization
        org_documents = session.query(Document).filter_by(org_id=org.id).all()
        assert len(org_documents) == 1
        assert org_documents[0].id == document.id
        assert isinstance(org_documents[0].id, uuid.UUID)
        
        # Get documents owned by user
        user_documents = session.query(Document).filter_by(owner_id=user.id).all()
        assert len(user_documents) == 1
        assert user_documents[0].id == document.id
        assert isinstance(user_documents[0].id, uuid.UUID) 