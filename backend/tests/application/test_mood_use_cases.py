import pytest

from src.application.dto.mood_dto import GetMoodsCommand, RegisterMoodCommand
from src.application.exceptions.sql_database import IntegrityConstraintViolationError
from src.application.use_cases.mood import list_moods, register_mood
from src.domain.exceptions.user_exceptions import InsufficientPermissionsError


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
        mood = await register_mood(mood_repository, command)
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
        with pytest.raises(
            IntegrityConstraintViolationError, match='Integrity constraint violated'
        ):
            await register_mood(mood_repository, command)


class TestListMoods:
    @pytest.mark.asyncio
    async def test_list_moods_as_owner(self, mood_repository, user_with_moods):
        command = GetMoodsCommand(user_id=user_with_moods.id)
        moods = await list_moods(mood_repository, command, user_with_moods)
        assert len(moods) == 10

    @pytest.mark.asyncio
    async def test_list_moods_as_admin(self, mood_repository, admin_user, user_with_moods):
        current_user = admin_user
        command = GetMoodsCommand(user_id=user_with_moods.id, is_admin=current_user.is_admin)
        moods = await list_moods(mood_repository, command, current_user)
        assert len(moods) == 10

    @pytest.mark.asyncio
    async def test_list_moods_with_insufficient_permissions(self, mood_repository, user):
        command = GetMoodsCommand(user_id='some_other_user_id')
        with pytest.raises(InsufficientPermissionsError, match='Not enough permissions'):
            await list_moods(mood_repository, command, user)
