from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions.sql_database import EntityAlreadyExistsError, EntityNotFoundError
from src.application.ports.repositories.user_repository import UserRepository
from src.domain.entities.user import User
from src.infrastructure.database.orm import UserModel


class SQLAlchemyUserRepository(UserRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    def _model_to_entity(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            password=user_model.password,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            is_admin=user_model.is_admin,
            is_active=user_model.is_active
        )

    def _entity_to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=user.is_admin,
            is_active=user.is_active
        )

    async def save(self, user: User) -> User:
        user_model = self._entity_to_model(user)
        try:
            self._session.add(user_model)
            await self._session.commit()
            await self._session.refresh(user_model)
            return self._model_to_entity(user_model)
        except IntegrityError:
            await self._session.rollback()
            raise EntityAlreadyExistsError("User with this email or username already exists")

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self._session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        if result:
            return self._model_to_entity(result)
        raise EntityNotFoundError("User not found")

    async def find_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.scalar(
            select(UserModel).where(UserModel.id == user_id)
        )
        if result:
            return self._model_to_entity(result)
        raise EntityNotFoundError("User not found")

    async def find_all(self, offset: int = 0, limit: int = 10) -> List[User]:
        result = await self._session.scalars(
            select(UserModel).offset(offset).limit(limit)
        )
        return [self._model_to_entity(user_model) for user_model in result.all()]

    async def update(self, user: User) -> User:
        existing_model = await self._session.scalar(
            select(UserModel).where(UserModel.id == user.id)
        )

        if not existing_model:
            raise ValueError(f"User with id {user.id} not found")

        existing_model.username = user.username
        existing_model.email = user.email
        existing_model.password = user.password
        existing_model.first_name = user.first_name
        existing_model.last_name = user.last_name
        existing_model.is_admin = user.is_admin
        existing_model.is_active = user.is_active

        try:
            await self._session.commit()
            await self._session.refresh(existing_model)
            return self._model_to_entity(existing_model)
        except IntegrityError:
            await self._session.rollback()
            raise EntityAlreadyExistsError("User with this email or username already exists")
