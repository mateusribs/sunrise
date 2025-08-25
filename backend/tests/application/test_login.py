import pytest

from src.application.exceptions import EntityNotFoundError
from src.application.dto import LoginCommand
from src.application.use_cases import Login
from src.domain.exceptions import InactiveUserError, InvalidCredentialsError
from src.domain.services.jwt_token import JWTTokenService


@pytest.mark.asyncio
async def test_login_user(user_repository, user):
    login_command = LoginCommand(
        email=user.email,
        password=user.clean_password
    )

    login = Login(
        user_repository=user_repository
    )

    result = await login.execute(login_command)

    jwt_token_service = JWTTokenService()

    assert result is not None
    assert jwt_token_service.decode_token(result)


@pytest.mark.asyncio
async def test_login_user_with_invalid_email(user_repository, user):
    login_command = LoginCommand(
        email="invalid@example.com",
        password=user.clean_password
    )

    login = Login(
        user_repository=user_repository
    )

    with pytest.raises(EntityNotFoundError, match="User not found"):
        await login.execute(login_command)


@pytest.mark.asyncio
async def test_login_user_with_invalid_password(user_repository, user):
    login_command = LoginCommand(
        email=user.email,
        password="wrongpassword"
    )

    login = Login(
        user_repository=user_repository
    )

    with pytest.raises(InvalidCredentialsError, match="Incorrect username or password"):
        await login.execute(login_command)


@pytest.mark.asyncio
async def test_login_inactive_user(user_repository, user):
    user.is_active = False
    await user_repository.update(user)

    login_command = LoginCommand(
        email=user.email,
        password=user.clean_password
    )

    login = Login(
        user_repository=user_repository
    )

    with pytest.raises(InactiveUserError, match="User account is inactive"):
        await login.execute(login_command)
