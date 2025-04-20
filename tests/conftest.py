import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# Test database configuration
TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db"
)

@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DB_URL)
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="session")
def test_data():
    """Load test data fixtures."""
    # This can be expanded to load specific test data
    return {
        "sample_data": {
            "key": "value"
        }
    }

@pytest.fixture(scope="function")
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "DATABASE_URL": TEST_DB_URL,
        "ENVIRONMENT": "test",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def db_session() -> Session:
    """Create a mock database session for testing."""
    # Create a mock session
    mock_session = MagicMock(spec=Session)
    
    # Configure the mock to behave like a real session
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    mock_session.close = MagicMock()
    
    yield mock_session
    
    # Clean up after the test
    mock_session.close() 