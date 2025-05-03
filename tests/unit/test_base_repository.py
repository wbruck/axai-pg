import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from src.axai_pg.data.repositories.base_repository import BaseRepository
from src.axai_pg.models.user import User

@pytest.mark.unit
@pytest.mark.asyncio
class TestBaseRepository:
    @pytest.fixture
    def user_repository(self, mock_db_session, mock_metrics):
        """Create a User repository with mocked session and metrics."""
        with patch('src.axai_pg.data.repositories.base_repository.DatabaseManager.get_instance') as mock_db:
            mock_db.return_value.get_session.return_value = mock_db_session
            return BaseRepository(User)

    async def test_find_by_id_success(self, user_repository, mock_db_session, mock_user):
        """Test successful find_by_id operation."""
        # Setup
        mock_db_session.first.return_value = mock_user

        # Execute
        result = await user_repository.find_by_id(1)

        # Verify
        assert result == mock_user
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.filter_by.assert_called_once_with(id=1)

    async def test_find_by_id_not_found(self, user_repository, mock_db_session):
        """Test find_by_id when entity is not found."""
        # Setup
        mock_db_session.first.return_value = None

        # Execute
        result = await user_repository.find_by_id(1)

        # Verify
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.filter_by.assert_called_once_with(id=1)

    async def test_find_by_id_error(self, user_repository, mock_db_session, simulate_db_error):
        """Test find_by_id with database error."""
        # Setup
        mock_db_session.query.side_effect = simulate_db_error()

        # Execute & Verify
        with pytest.raises(RuntimeError) as exc_info:
            await user_repository.find_by_id(1)
        assert "Database error in find_by_id" in str(exc_info.value)

    async def test_find_many_success(self, user_repository, mock_db_session, mock_user):
        """Test successful find_many operation."""
        # Setup
        test_users = [mock_user]
        mock_db_session.all.return_value = test_users

        # Execute
        result = await user_repository.find_many({"username": "test"})

        # Verify
        assert result == test_users
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.filter.assert_called_once()

    async def test_find_many_with_options(self, user_repository, mock_db_session, mock_user):
        """Test find_many with pagination and ordering options."""
        # Setup
        test_users = [mock_user]
        mock_db_session.all.return_value = test_users

        # Execute
        result = await user_repository.find_many(
            {"username": "test"},
            {"offset": 0, "limit": 10, "order_by": {"username": "DESC"}}
        )

        # Verify
        assert result == test_users
        mock_db_session.offset.assert_called_once_with(0)
        mock_db_session.limit.assert_called_once_with(10)
        mock_db_session.order_by.assert_called_once()

    async def test_create_success(self, user_repository, mock_db_session, mock_user):
        """Test successful create operation."""
        # Setup
        user_data = {"username": "newuser", "email": "new@example.com"}
        mock_db_session.refresh.return_value = mock_user

        # Execute
        result = await user_repository.create(user_data)

        # Verify
        assert isinstance(result, User)
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_success(self, user_repository, mock_db_session, mock_user):
        """Test successful update operation."""
        # Setup
        mock_db_session.first.return_value = mock_user
        update_data = {"username": "newuser", "email": "new@example.com"}

        # Execute
        result = await user_repository.update(1, update_data)

        # Verify
        assert result == mock_user
        assert mock_user.username == update_data["username"]
        assert mock_user.email == update_data["email"]
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_not_found(self, user_repository, mock_db_session):
        """Test update when entity is not found."""
        # Setup
        mock_db_session.first.return_value = None

        # Execute
        result = await user_repository.update(1, {"username": "newuser"})

        # Verify
        assert result is None
        mock_db_session.commit.assert_not_called()

    async def test_delete_success(self, user_repository, mock_db_session, mock_user):
        """Test successful delete operation."""
        # Setup
        mock_db_session.first.return_value = mock_user

        # Execute
        result = await user_repository.delete(1)

        # Verify
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_user)
        mock_db_session.commit.assert_called_once()

    async def test_delete_not_found(self, user_repository, mock_db_session):
        """Test delete when entity is not found."""
        # Setup
        mock_db_session.first.return_value = None

        # Execute
        result = await user_repository.delete(1)

        # Verify
        assert result is False
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    async def test_transaction_success(self, user_repository, mock_db_session, mock_transaction):
        """Test successful transaction operation."""
        # Setup
        async def test_operation(session):
            return "success"

        # Execute
        result = await user_repository.transaction(test_operation)

        # Verify
        assert result == "success"
        mock_db_session.commit.assert_called_once()

    async def test_transaction_error(self, user_repository, mock_db_session, simulate_db_error):
        """Test transaction with error."""
        # Setup
        async def test_operation(session):
            raise simulate_db_error()()

        # Execute & Verify
        with pytest.raises(RuntimeError) as exc_info:
            await user_repository.transaction(test_operation)
        assert "Transaction error" in str(exc_info.value)
        mock_db_session.rollback.assert_called_once()