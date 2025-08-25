from src.application.dto.user_dto import GetUsersCommand
from src.application.ports.repositories.user_repository import UserRepository
from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import InactiveUserError, InsufficientPermissionsError


class GetUsers:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, command: GetUsersCommand) -> list[User]:
        if not command.is_admin:
            raise InsufficientPermissionsError('Only admin users can retrieve the user list')

        if not command.is_active:
            raise InactiveUserError('Inactive users cannot perform this action')

        return await self._user_repository.find_all(offset=command.offset, limit=command.limit)
