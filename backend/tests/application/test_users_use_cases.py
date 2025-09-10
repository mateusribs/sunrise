import pytest

from src.application.dto.user_dto import (
    CreateUserCommand,
    GetUsersCommand,
    LoginCommand,
    UpdateUserCommand,
)
from src.application.exceptions.sql_database import EntityAlreadyExistsError, EntityNotFoundError
from src.application.use_cases.users import (
    create_user,
    get_access_token,
    get_current_user,
    list_users,
    update_user,
)
from src.domain.exceptions.user_exceptions import (
    InactiveUserError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidUsernameError,
)
from src.domain.services.jwt_token import JWTTokenService


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository):
        user_command = CreateUserCommand(
            username='testuser',
            email='testuser@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        await create_user(user_repository, user_command)

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
    async def test_create_user_with_invalid_username(self, user_repository):
        user_command = CreateUserCommand(
            username='',
            email='testuser@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        with pytest.raises(InvalidUsernameError, match='Username cannot be empty'):
            await create_user(user_repository, user_command)

    @pytest.mark.asyncio
    async def test_create_user_with_short_password(self, user_repository):
        user_command = CreateUserCommand(
            username='testuser',
            email='testuser@example.com',
            password='short',
            first_name='Test',
            last_name='User',
        )

        with pytest.raises(
            InvalidPasswordError, match='Password must be at least 8 characters long'
        ):
            await create_user(user_repository, user_command)

    @pytest.mark.asyncio
    async def test_create_user_with_existing_email(self, user_repository):
        user_command = CreateUserCommand(
            username='testuser',
            email='testuser@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        user_command_duplicate = CreateUserCommand(
            username='anotheruser',
            email='testuser@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        await create_user(user_repository, user_command)

        with pytest.raises(EntityAlreadyExistsError):
            await create_user(user_repository, user_command_duplicate)

    @pytest.mark.asyncio
    async def test_create_user_with_existing_username(self, user_repository):
        user_command = CreateUserCommand(
            username='testuser',
            email='testuser@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        user_command_duplicate = CreateUserCommand(
            username='testuser',
            email='testuser2@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
        )

        await create_user(user_repository, user_command)

        with pytest.raises(EntityAlreadyExistsError):
            await create_user(user_repository, user_command_duplicate)


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_get_current_user(self, user_repository, user):
        data = {'sub': user.email}
        user_token = JWTTokenService().create_access_token(data)

        current_user = await get_current_user(user_repository, user_token)

        assert current_user.id == user.id
        assert current_user.username == user.username
        assert current_user.first_name == user.first_name
        assert current_user.last_name == user.last_name

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, user_repository):
        invalid_token = {'sub': ''}
        invalid_token = JWTTokenService().create_access_token(invalid_token)

        with pytest.raises(ValueError, match='Invalid token'):
            await get_current_user(user_repository, invalid_token)

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, user_repository):
        data = {'sub': 'nonexistent@example.com'}
        user_token = JWTTokenService().create_access_token(data)

        with pytest.raises(EntityNotFoundError):
            await get_current_user(user_repository, user_token)


class TestListUsers:
    @pytest.mark.asyncio
    async def test_list_users(self, user_repository, user, other_user):
        get_users_command = GetUsersCommand(offset=0, limit=10, is_active=True, is_admin=True)

        users = await list_users(user_repository, get_users_command)
        user_domain = user_repository._model_to_entity(user)
        other_user_domain = user_repository._model_to_entity(other_user)

        assert len(users) == 2
        assert users == [user_domain, other_user_domain]

    @pytest.mark.asyncio
    async def test_list_users_with_offset(self, user_repository, user, other_user):
        get_users_command = GetUsersCommand(offset=1, limit=10, is_active=True, is_admin=True)

        users = await list_users(user_repository, get_users_command)
        other_user_domain = user_repository._model_to_entity(other_user)

        assert len(users) == 1
        assert users == [other_user_domain]

    @pytest.mark.asyncio
    async def test_list_users_when_user_is_not_admin(self, user_repository, user, other_user):
        get_users_command = GetUsersCommand(offset=0, limit=10, is_active=True, is_admin=False)

        with pytest.raises(
            InsufficientPermissionsError, match='Only admin users can retrieve the user list'
        ):
            await list_users(user_repository, get_users_command)

    @pytest.mark.asyncio
    async def test_list_users_when_user_is_inactive(self, user_repository, user, other_user):
        get_users_command = GetUsersCommand(offset=0, limit=10, is_active=False, is_admin=True)

        with pytest.raises(InactiveUserError, match='Inactive users cannot perform this action'):
            await list_users(user_repository, get_users_command)


class TestGetAccessToken:
    @pytest.mark.asyncio
    async def test_get_access_token_user(self, user_repository, user):
        login_command = LoginCommand(email=user.email, password=user.clean_password)

        result = await get_access_token(user_repository, login_command)

        jwt_token_service = JWTTokenService()

        assert result is not None
        assert jwt_token_service.decode_token(result)

    @pytest.mark.asyncio
    async def test_get_access_token_user_with_invalid_email(self, user_repository, user):
        login_command = LoginCommand(email='invalid@example.com', password=user.clean_password)

        with pytest.raises(EntityNotFoundError, match='User not found'):
            await get_access_token(user_repository, login_command)

    @pytest.mark.asyncio
    async def test_get_access_token_user_with_invalid_password(self, user_repository, user):
        login_command = LoginCommand(email=user.email, password='wrongpassword')

        with pytest.raises(InvalidCredentialsError, match='Incorrect username or password'):
            await get_access_token(user_repository, login_command)

    @pytest.mark.asyncio
    async def test_get_access_token_user_with_inactive_account(self, user_repository, user):
        user.is_active = False
        await user_repository.update(user)

        login_command = LoginCommand(email=user.email, password=user.clean_password)

        with pytest.raises(InactiveUserError, match='User account is inactive'):
            await get_access_token(user_repository, login_command)


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_user_when_is_admin(self, user_repository, user, other_user):
        user_command = UpdateUserCommand(
            user_id=user.id, username='newusername', first_name='New', last_name='Name'
        )

        current_user = user_repository._model_to_entity(other_user)
        current_user.is_admin = True

        await update_user(user_repository, user_command, current_user)

        updated_user = await user_repository.find_by_email(user.email)

        assert updated_user.username == user_command.username
        assert updated_user.first_name == user_command.first_name
        assert updated_user.last_name == user_command.last_name

    @pytest.mark.asyncio
    async def test_update_user_when_is_same_user(self, user_repository, user):
        user_command = UpdateUserCommand(
            user_id=user.id, username='newusername', first_name='New', last_name='Name'
        )

        current_user = user_repository._model_to_entity(user)

        await update_user(user_repository, user_command, current_user)

        updated_user = await user_repository.find_by_email(user.email)

        assert updated_user.username == user_command.username
        assert updated_user.first_name == user_command.first_name
        assert updated_user.last_name == user_command.last_name

    @pytest.mark.asyncio
    async def test_update_different_id(self, user_repository, user):
        user_command = UpdateUserCommand(user_id='nonexistent-id', username='newusername')

        user_domain = user_repository._model_to_entity(user)

        with pytest.raises(InsufficientPermissionsError):
            await update_user(user_repository, user_command, user_domain)

    @pytest.mark.asyncio
    async def test_update_username_already_exists(self, user_repository, user, other_user):
        user_domain = user_repository._model_to_entity(user)

        user_command = UpdateUserCommand(user_id=user_domain.id, username=other_user.username)

        with pytest.raises(EntityAlreadyExistsError):
            await update_user(user_repository, user_command, user_domain)
