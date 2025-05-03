import pytest
import asyncio
from sqlalchemy import text
from src.axai_pg.models.user import User
from unittest.mock import ANY

@pytest.mark.integration
@pytest.mark.db
class TestDatabaseOperations:
    def test_database_connection(self, real_db_session):
        """Test that we can connect to the database."""
        result = real_db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_user_creation(self, real_db_session):
        """Test creating a new user in the database."""
        user = User(
            username="testuser",
            email="test@example.com"
        )
        real_db_session.add(user)
        real_db_session.commit()

        # Verify the user was created
        saved_user = real_db_session.query(User).filter_by(username="testuser").first()
        assert saved_user is not None
        assert saved_user.email == "test@example.com"

        # Clean up
        real_db_session.delete(saved_user)
        real_db_session.commit()

    def test_user_deletion(self, real_db_session):
        """Test deleting a user from the database."""
        # Create a user
        user = User(
            username="delete_me",
            email="delete@example.com"
        )
        real_db_session.add(user)
        real_db_session.commit()

        # Delete the user
        real_db_session.delete(user)
        real_db_session.commit()

        # Verify the user was deleted
        deleted_user = real_db_session.query(User).filter_by(username="delete_me").first()
        assert deleted_user is None 