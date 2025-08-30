import pytest

from src.application.dto.mood_dto import RegisterMoodCommand
from src.application.exceptions.sql_database import IntegrityConstraintViolationError
from src.application.use_cases.mood import register_mood
from src.domain.entities.user import User


class TestRegisterMood:
    @pytest.mark.asyncio
    async def test_register_valid_mood(self, mood_repository, user):
        command = RegisterMoodCommand(
            user_id=user.id,
            visual_scale=5,
            registry_type='daily',
            description='Feeling great!',
            associated_emotions=[{'name': 'joy', 'intensity': 8}],
            triggers=[{'name': 'saw a rainbow'}],
        )
        mood = await register_mood(mood_repository, command, user)
        assert mood.id is not None

    @pytest.mark.asyncio
    async def test_register_mood_with_invalid_user(self, mood_repository):
        command = RegisterMoodCommand(
            user_id='invalid_user_id',
            visual_scale=5,
            registry_type='daily',
            description='Feeling great!',
            associated_emotions=[{'name': 'joy', 'intensity': 8}],
            triggers=[{'name': 'saw a rainbow'}],
        )

        user = User(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123',
            first_name='Test',
            last_name='User',
            is_admin=False,
            is_active=True,
        )

        with pytest.raises(
            IntegrityConstraintViolationError, match='Integrity constraint violated'
        ):
            await register_mood(mood_repository, command, user)
