from src.application.ports.repositories.user_repository import UserRepository
from src.domain.entities.user import User
from src.domain.services.jwt_token import JWTTokenService


class GetCurrentUser:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._jwt_service = JWTTokenService()

    async def execute(self, token: str) -> User:
        payload = self._jwt_service.decode_token(token)
        user_email = payload.get('sub')

        if not user_email:
            raise ValueError('Invalid token')

        user = await self._user_repository.find_by_email(user_email)

        return user
