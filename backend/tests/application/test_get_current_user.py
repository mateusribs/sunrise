import pytest

from src.application.exceptions.sql_database import EntityNotFoundError
from src.application.use_cases.get_current_user import GetCurrentUser
from src.domain.services.jwt_token import JWTTokenService


@pytest.mark.asyncio
async def test_get_current_user(user_repository, user):
    data = {'sub': user.email}
    user_token = JWTTokenService().create_access_token(data)

    get_current_user = GetCurrentUser(user_repository)

    current_user = await get_current_user.execute(user_token)

    assert current_user.id == user.id
    assert current_user.username == user.username
    assert current_user.first_name == user.first_name
    assert current_user.last_name == user.last_name


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(user_repository):
    invalid_token = {'sub': ''}
    invalid_token = JWTTokenService().create_access_token(invalid_token)
    get_current_user = GetCurrentUser(user_repository)

    with pytest.raises(ValueError, match='Invalid token'):
        await get_current_user.execute(invalid_token)


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(user_repository):
    data = {'sub': 'nonexistent@example.com'}
    user_token = JWTTokenService().create_access_token(data)

    get_current_user = GetCurrentUser(user_repository)

    with pytest.raises(EntityNotFoundError):
        await get_current_user.execute(user_token)
