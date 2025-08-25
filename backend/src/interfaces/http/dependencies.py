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


# Use Cases
def create_user(
    user_repository=Depends(user_repository),
):
    """Dependency para use case de criação de usuário"""
    return CreateUser(user_repository)


def get_users(user_repository=Depends(user_repository)):
    """Dependency para use case de busca de usuários"""
    return GetUsers(user_repository)


def update_user(user_repository=Depends(user_repository)):
    """Dependency para use case de atualização de usuário"""
    return UpdateUser(user_repository)


def get_current_user(user_repository=Depends(user_repository)):
    """Dependency para obter o usuário atual"""
    return GetCurrentUser(user_repository)


def login(user_repository=Depends(user_repository)):
    """Dependency para use case de login"""
    return Login(user_repository)


CreateUserDependency = Annotated[CreateUser, Depends(create_user)]
GetUsersDependency = Annotated[GetUsers, Depends(get_users)]
UpdateUserDependency = Annotated[UpdateUser, Depends(update_user)]
LoginDependency = Annotated[Login, Depends(login)]
GetCurrentUserDependency = Annotated[GetCurrentUser, Depends(get_current_user)]
