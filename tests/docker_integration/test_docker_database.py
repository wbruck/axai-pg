import pytest
import asyncio
from sqlalchemy import text
from src.axai_pg.data.models.user import User
from src.axai_pg.data.config.database import DatabaseManager, PostgresConnectionConfig

@pytest.mark.docker_integration
@pytest.mark.db
class TestDockerDatabaseOperations:
    @pytest.fixture
    def db_session(self):
        # Initialize database connection
        conn_config = PostgresConnectionConfig.from_env()
        DatabaseManager.initialize(conn_config)
        db_manager = DatabaseManager.get_instance()
        
        with db_manager.session_scope() as session:
            yield session

    def test_docker_database_connection(self, db_session):
        """Test that we can connect to the database in Docker."""
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_docker_user_creation(self, db_session):
        """Test creating a new user in the Docker database."""
        # Create a new user
        user = User(
            username="docker_testuser",
            email="docker_test@example.com"
        )
        db_session.add(user)
        db_session.commit()

        # Verify the user was created
        saved_user = db_session.query(User).filter_by(username="docker_testuser").first()
        assert saved_user is not None
        assert saved_user.email == "docker_test@example.com"

        # Clean up
        db_session.delete(saved_user)
        db_session.commit()

    def test_docker_user_deletion(self, db_session):
        """Test deleting a user from the Docker database."""
        # Create a user
        user = User(
            username="docker_delete_me",
            email="docker_delete@example.com"
        )
        db_session.add(user)
        db_session.commit()

        # Delete the user
        db_session.delete(user)
        db_session.commit()

        # Verify the user was deleted
        deleted_user = db_session.query(User).filter_by(username="docker_delete_me").first()
        assert deleted_user is None 