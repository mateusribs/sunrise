import pytest

from src.domain.entities import User


class TestSQLAlchemyUserRepository:
    @pytest.mark.asyncio
    async def test_save(self, user_repository):
        user = User(
            username="testuser",
            email="testuser@example.com",
            password="HashedPassword123",
        )

        await user_repository.save(user)
        fetched_user = await user_repository.find_by_id(user.id)

        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.email == user.email
        assert fetched_user.password == user.password
