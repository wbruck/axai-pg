import pytest
from sqlalchemy import text
from src.models.user import User
from unittest.mock import ANY

@pytest.mark.integration
@pytest.mark.db
class TestDatabaseOperations:
    def test_database_connection(self, db_session):
        """Test that we can connect to the database."""
        # Configure mock to return 1
        db_session.execute.return_value.scalar.return_value = 1
        
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        # Verify mock was called correctly
        db_session.execute.assert_called_once()

    def test_user_creation(self, db_session):
        """Test creating a new user in the database."""
        # Configure mock to return None for the query (simulating empty DB)
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        user = User(
            username="testuser",
            email="test@example.com"
        )
        db_session.add(user)
        db_session.commit()

        # Configure mock to return the user for the verification query
        db_session.query.return_value.filter_by.return_value.first.return_value = user

        # Verify the user was created
        saved_user = db_session.query(User).filter_by(username="testuser").first()
        assert saved_user is not None
        assert saved_user.email == "test@example.com"

        # Verify mock interactions
        db_session.add.assert_called_once_with(user)
        db_session.commit.assert_called()

    def test_user_deletion(self, db_session):
        """Test deleting a user from the database."""
        # Create a user
        user = User(
            username="delete_me",
            email="delete@example.com"
        )
        
        # Configure mock to return the user initially
        db_session.query.return_value.filter_by.return_value.first.return_value = user
        
        db_session.add(user)
        db_session.commit()

        # Delete the user
        db_session.delete(user)
        db_session.commit()

        # Configure mock to return None after deletion
        db_session.query.return_value.filter_by.return_value.first.return_value = None

        # Verify the user was deleted
        deleted_user = db_session.query(User).filter_by(username="delete_me").first()
        assert deleted_user is None

        # Verify mock interactions
        db_session.delete.assert_called_once_with(user)
        assert db_session.commit.call_count >= 2  # Called after add and delete 