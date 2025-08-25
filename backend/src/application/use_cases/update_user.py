from src.application.dto import UpdateUserCommand
from src.application.ports.repositories import UserRepository
from src.domain.entities import User
from src.domain.exceptions import (
    InsufficientPermissionsError,
)


class UpdateUser:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, command: UpdateUserCommand, current_user: User) -> User:
        if current_user.id != command.user_id:
            if not current_user.is_admin:
                raise InsufficientPermissionsError('Not enough permissions')

        update_user = await self._user_repository.find_by_id(command.user_id)

        if command.username and command.username != update_user.username:
            update_user.update_username(command.username)

        if command.first_name is not None or command.last_name is not None:
            update_user.update_profile(first_name=command.first_name, last_name=command.last_name)

        return await self._user_repository.update(update_user)
