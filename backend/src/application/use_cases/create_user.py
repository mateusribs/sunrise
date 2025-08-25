from src.application.dto import CreateUserCommand
from src.application.ports.repositories import UserRepository
from src.domain.entities import User
from src.domain.services.password import PasswordService


class CreateUser:
    """Use case para criar um usuário"""

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self._user_repository = user_repository
        self._password_service = PasswordService()

    async def execute(self, command: CreateUserCommand) -> User:
        user = User(
            username=command.username,
            email=command.email,
            password=command.password,
            first_name=command.first_name,
            last_name=command.last_name
        )

        user.password = self._password_service.hash_password(user.password)

        return await self._user_repository.save(user)
