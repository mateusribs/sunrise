from src.application.dto.user_dto import LoginCommand
from src.application.ports.repositories.user_repository import UserRepository
from src.domain.exceptions.user_exceptions import InactiveUserError, InvalidCredentialsError
from src.domain.services.jwt_token import JWTTokenService
from src.domain.services.password import PasswordService


class Login:
    """Use case para autenticação de usuário"""

    def __init__(
        self,
        user_repository: UserRepository
    ):
        self._user_repository = user_repository
        self._password_service = PasswordService()
        self._token_service = JWTTokenService()

    async def execute(self, command: LoginCommand) -> str:
        """Executa o caso de uso de login e retorna o token"""

        # Buscar usuário por email
        user = await self._user_repository.find_by_email(command.email)
        if not user:
            raise InvalidCredentialsError("Incorrect username or password")

        # Verificar se usuário está ativo
        if not user.is_active:
            raise InactiveUserError("User account is inactive")

        # Verificar senha
        if not self._password_service.verify_password(command.password, user.password):
            raise InvalidCredentialsError("Incorrect username or password")

        # Gerar token
        token_data = {'sub': user.email}
        access_token = self._token_service.create_access_token(token_data)

        return access_token
