from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories.user_repository import UserRepository
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_session)]


def user_repository(session: AsyncSessionDependency) -> UserRepository:
    """Dependency para repositório de usuários"""
    return SQLAlchemyUserRepository(session)


UserRepositoryDependency = Annotated[UserRepository, Depends(user_repository)]
