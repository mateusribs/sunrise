import pytest

from src.application.dto import CreateUserCommand
from src.application.exceptions import EntityAlreadyExistsError
from src.application.use_cases import CreateUser
from src.domain.exceptions import InvalidPasswordError, InvalidUsernameError


@pytest.mark.asyncio
async def test_create_user(user_repository):
    user_command = CreateUserCommand(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    create_user = CreateUser(user_repository)

    await create_user.execute(user_command)

    user = await user_repository.find_by_email(user_command.email)

    assert user.id is not None
    assert user.username == user_command.username
    assert user.email == user_command.email
    assert user.password != user_command.password
    assert user.first_name == user_command.first_name
    assert user.last_name == user_command.last_name
    assert user.is_active is True
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_create_user_with_invalid_username(user_repository):
    user_command = CreateUserCommand(
        username='',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    create_user = CreateUser(user_repository)

    with pytest.raises(InvalidUsernameError, match="Username cannot be empty"):
        await create_user.execute(user_command)


@pytest.mark.asyncio
async def test_create_user_with_short_password(user_repository):
    user_command = CreateUserCommand(
        username='testuser',
        email='testuser@example.com',
        password='short',
        first_name='Test',
        last_name='User'
    )

    create_user = CreateUser(user_repository)

    with pytest.raises(InvalidPasswordError, match="Password must be at least 8 characters long"):
        await create_user.execute(user_command)


@pytest.mark.asyncio
async def test_create_user_with_existing_email(user_repository):
    user_command = CreateUserCommand(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    user_command_duplicate = CreateUserCommand(
        username='anotheruser',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    create_user = CreateUser(user_repository)

    await create_user.execute(user_command)

    with pytest.raises(EntityAlreadyExistsError):
        await create_user.execute(user_command_duplicate)


@pytest.mark.asyncio
async def test_create_user_with_existing_username(user_repository):
    user_command = CreateUserCommand(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    user_command_duplicate = CreateUserCommand(
        username='testuser',
        email='testuser2@example.com',
        password='Password123',
        first_name='Test',
        last_name='User'
    )

    create_user = CreateUser(user_repository)

    await create_user.execute(user_command)

    with pytest.raises(EntityAlreadyExistsError):
        await create_user.execute(user_command_duplicate)
