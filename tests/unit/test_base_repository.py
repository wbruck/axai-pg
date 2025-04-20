import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from src.data.repositories.base_repository import BaseRepository
from src.models.user import User

@pytest.mark.unit
@pytest.mark.asyncio
class TestBaseRepository:
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.query.return_value = session
        session.filter_by.return_value = session
        session.filter.return_value = session
        session.first.return_value = None
        session.all.return_value = []
        session.offset.return_value = session
        session.limit.return_value = session
        session.order_by.return_value = session
        
        # Configure context manager methods
        session.__enter__.return_value = session
        session.__exit__.return_value = None
        
        return session

    @pytest.fixture
    def user_repository(self, mock_session):
        """Create a User repository with mocked session."""
        with patch('src.data.repositories.base_repository.DatabaseManager.get_instance') as mock_db:
            mock_db.return_value.get_session.return_value = mock_session
            return BaseRepository(User)

    async def test_find_by_id_success(self, user_repository, mock_session):
        """Test successful find_by_id operation."""
        # Setup
        test_user = User(username="testuser", email="test@example.com")
        mock_session.first.return_value = test_user

        # Execute
        result = await user_repository.find_by_id(1)

        # Verify
        assert result == test_user
        mock_session.query.assert_called_once_with(User)
        mock_session.filter_by.assert_called_once_with(id=1)

    async def test_find_by_id_not_found(self, user_repository, mock_session):
        """Test find_by_id when entity is not found."""
        # Setup
        mock_session.first.return_value = None

        # Execute
        result = await user_repository.find_by_id(1)

        # Verify
        assert result is None
        mock_session.query.assert_called_once_with(User)
        mock_session.filter_by.assert_called_once_with(id=1)

    async def test_find_by_id_error(self, user_repository, mock_session):
        """Test find_by_id with database error."""
        # Setup
        mock_session.query.side_effect = SQLAlchemyError("Test error")

        # Execute & Verify
        with pytest.raises(RuntimeError) as exc_info:
            await user_repository.find_by_id(1)
        assert "Database error in find_by_id" in str(exc_info.value)

    async def test_find_many_success(self, user_repository, mock_session):
        """Test successful find_many operation."""
        # Setup
        test_users = [
            User(username="user1", email="user1@example.com"),
            User(username="user2", email="user2@example.com")
        ]
        mock_session.all.return_value = test_users

        # Execute
        result = await user_repository.find_many({"username": "test"})

        # Verify
        assert result == test_users
        mock_session.query.assert_called_once_with(User)
        mock_session.filter.assert_called_once()

    async def test_find_many_with_options(self, user_repository, mock_session):
        """Test find_many with pagination and ordering options."""
        # Setup
        test_users = [User(username="user1", email="user1@example.com")]
        mock_session.all.return_value = test_users

        # Execute
        result = await user_repository.find_many(
            {"username": "test"},
            {"offset": 0, "limit": 10, "order_by": {"username": "DESC"}}
        )

        # Verify
        assert result == test_users
        mock_session.offset.assert_called_once_with(0)
        mock_session.limit.assert_called_once_with(10)
        mock_session.order_by.assert_called_once()

    async def test_create_success(self, user_repository, mock_session):
        """Test successful create operation."""
        # Setup
        user_data = {"username": "newuser", "email": "new@example.com"}
        test_user = User(**user_data)
        mock_session.refresh.return_value = test_user

        # Execute
        result = await user_repository.create(user_data)

        # Verify
        assert isinstance(result, User)
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_update_success(self, user_repository, mock_session):
        """Test successful update operation."""
        # Setup
        test_user = User(username="olduser", email="old@example.com")
        mock_session.first.return_value = test_user
        update_data = {"username": "newuser", "email": "new@example.com"}

        # Execute
        result = await user_repository.update(1, update_data)

        # Verify
        assert result == test_user
        assert test_user.username == update_data["username"]
        assert test_user.email == update_data["email"]
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_update_not_found(self, user_repository, mock_session):
        """Test update when entity is not found."""
        # Setup
        mock_session.first.return_value = None

        # Execute
        result = await user_repository.update(1, {"username": "newuser"})

        # Verify
        assert result is None
        mock_session.commit.assert_not_called()

    async def test_delete_success(self, user_repository, mock_session):
        """Test successful delete operation."""
        # Setup
        test_user = User(username="todelete", email="delete@example.com")
        mock_session.first.return_value = test_user

        # Execute
        result = await user_repository.delete(1)

        # Verify
        assert result is True
        mock_session.delete.assert_called_once_with(test_user)
        mock_session.commit.assert_called_once()

    async def test_delete_not_found(self, user_repository, mock_session):
        """Test delete when entity is not found."""
        # Setup
        mock_session.first.return_value = None

        # Execute
        result = await user_repository.delete(1)

        # Verify
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    async def test_transaction_success(self, user_repository, mock_session):
        """Test successful transaction operation."""
        # Setup
        async def test_operation(session):
            return "success"

        # Execute
        result = await user_repository.transaction(test_operation)

        # Verify
        assert result == "success"
        mock_session.commit.assert_called_once()

    async def test_transaction_error(self, user_repository, mock_session):
        """Test transaction with error."""
        # Setup
        async def test_operation(session):
            raise Exception("Test error")

        # Execute & Verify
        with pytest.raises(RuntimeError) as exc_info:
            await user_repository.transaction(test_operation)
        assert "Transaction error" in str(exc_info.value)
        mock_session.rollback.assert_called_once()