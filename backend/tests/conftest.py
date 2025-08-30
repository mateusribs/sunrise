import random
import uuid
from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.api import app
from src.domain.services.password import PasswordService
from src.infrastructure.database.orm import (
    AssociatedEmotionsModel,
    EmotionalTriggerModel,
    MoodModel,
    UserModel,
    table_registry,
)
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.mood_repository import SQLAlchemyMoodRepository
from src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def password_service():
    return PasswordService()


@pytest.fixture
def user_repository(session):
    return SQLAlchemyUserRepository(session)


@pytest.fixture
def mood_repository(session):
    return SQLAlchemyMoodRepository(session)


@pytest_asyncio.fixture(scope='function')
async def user(session, password_service):
    password = 'testuser'
    user = UserFactory(password=password_service.hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture(scope='function')
async def other_user(session, password_service):
    password = 'testuser'
    user = UserFactory(password=password_service.hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def user_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


class UserFactory(factory.Factory):
    class Meta:
        model = UserModel

    id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))
    username = factory.LazyFunction(lambda: f'user{random.randint(1, 10000)}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}_secret')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_admin = False
    is_active = True


class MoodFactory(factory.Factory):
    class Meta:
        model = MoodModel

    user_id: str
    id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))
    visual_scale = factory.Faker('random_int', min=1, max=10)
    registry_type = factory.Iterator(['happy', 'sad', 'angry', 'anxious'])
    description = factory.Faker('sentence')
    associated_emotions = factory.List([
        AssociatedEmotionsModel(
            mood_id=factory.LazyAttribute(lambda o: o.id),
            name=factory.Iterator(['joy', 'sadness', 'anger', 'fear', 'surprise']),
            intensity=factory.Faker('random_int', min=1, max=10),
        )
        for _ in range(2)
    ])
    triggers = factory.List([
        EmotionalTriggerModel(
            mood_id=factory.LazyAttribute(lambda o: o.id), name=factory.Faker('word')
        )
        for _ in range(2)
    ])
