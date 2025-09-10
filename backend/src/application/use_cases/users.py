from src.application.dto.user_dto import (
    CreateUserCommand,
    GetUsersCommand,
    LoginCommand,
    UpdateUserCommand,
)
from src.application.ports.repositories.user_repository import UserRepository
from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import (
    InactiveUserError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
)
from src.domain.services.jwt_token import JWTTokenService
from src.domain.services.password import PasswordService


async def create_user(user_repository: UserRepository, command: CreateUserCommand) -> User:
    password_service = PasswordService()
    user = User(
        username=command.username,
        email=command.email,
        password=command.password,
        first_name=command.first_name,
        last_name=command.last_name,
    )

    user.password = password_service.hash_password(user.password)

    return await user_repository.save(user)


async def list_users(user_repository: UserRepository, command: GetUsersCommand) -> list[User]:
    if not command.is_admin:
        raise InsufficientPermissionsError('Only admin users can retrieve the user list')

    if not command.is_active:
        raise InactiveUserError('Inactive users cannot perform this action')

    return await user_repository.find_all(offset=command.offset, limit=command.limit)


async def get_current_user(user_repository: UserRepository, token: str) -> User:
    jwt_service = JWTTokenService()
    payload = jwt_service.decode_token(token)
    user_email = payload.get('sub')

    if not user_email:
        raise ValueError('Invalid token')

    user = await user_repository.find_by_email(user_email)

    return user


async def update_user(
    user_repository: UserRepository, command: UpdateUserCommand, current_user: User
) -> User:
    if current_user.id != command.user_id:
        if not current_user.is_admin:
            raise InsufficientPermissionsError('Not enough permissions')

    update_user = await user_repository.find_by_id(command.user_id)

    if command.username and command.username != update_user.username:
        update_user.update_username(command.username)

    if command.first_name is not None or command.last_name is not None:
        update_user.update_profile(first_name=command.first_name, last_name=command.last_name)

    return await user_repository.update(update_user)


async def get_access_token(user_repository: UserRepository, command: LoginCommand) -> str:
    user = await user_repository.find_by_email(command.email)
    if not user:
        raise InvalidCredentialsError('Incorrect username or password')

    if not user.is_active:
        raise InactiveUserError('User account is inactive')

    if not PasswordService().verify_password(command.password, user.password):
        raise InvalidCredentialsError('Incorrect username or password')

    token_data = {'sub': user.email}
    access_token = JWTTokenService().create_access_token(token_data)

    return access_token
