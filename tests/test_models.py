import pytest
from axai_pg import Organization, User, Document
from axai_pg import DatabaseManager, PostgresConnectionConfig

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

def test_create_organization(db):
    with db.session_scope() as session:
        org = Organization(name="Test Org")
        session.add(org)
        session.flush()
        assert org.id is not None
        assert org.name == "Test Org"

def test_create_user_with_organization(db):
    with db.session_scope() as session:
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
        
        assert user.id is not None
        assert user.org_id == org.id
        assert user.username == "testuser" 