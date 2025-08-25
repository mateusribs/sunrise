from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.create_user import CreateUser
from src.application.use_cases.get_current_user import GetCurrentUser
from src.application.use_cases.get_users import GetUsers
from src.application.use_cases.login import Login
from src.application.use_cases.update_user import UpdateUser
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


# Repositórios
def user_repository(session: AsyncSession = Depends(get_session)):
    """Dependency para repositório de usuários"""
    return SQLAlchemyUserRepository(session)


CreateUserDependency = Annotated[CreateUser, Depends(user_repository)]
GetUsersDependency = Annotated[GetUsers, Depends(user_repository)]
UpdateUserDependency = Annotated[UpdateUser, Depends(user_repository)]
GetCurrentUserDependency = Annotated[GetCurrentUser, Depends(user_repository)]
LoginDependency = Annotated[Login, Depends(user_repository)]
