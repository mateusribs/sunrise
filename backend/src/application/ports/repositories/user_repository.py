from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.user import User


class UserRepository(ABC):
    """Port - Interface para repositório de usuários"""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Salva um usuário no repositório"""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário por email"""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca um usuário por ID"""
        pass

    @abstractmethod
    async def find_all(self, offset: int = 0, limit: int = 10) -> List[User]:
        """Busca todos os usuários com paginação"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Atualiza um usuário"""
        pass
