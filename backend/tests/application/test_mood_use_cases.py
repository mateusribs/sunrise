import pytest

from src.application.dto.mood_dto import (
    DeleteMoodCommand,
    GetMoodsCommand,
    RegisterMoodCommand,
    UpdateMoodCommand,
)
from src.application.exceptions.sql_database import IntegrityConstraintViolationError
from src.application.use_cases.mood import delete_mood, list_moods, register_mood, update_mood
from src.domain.entities.associated_emotion import AssociatedEmotion
from src.domain.entities.emotional_trigger import EmotionalTrigger
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
        command = GetMoodsCommand(user_id=user_with_moods.id)
        moods = await list_moods(mood_repository, command, current_user)
        assert len(moods) == 10

    @pytest.mark.asyncio
    async def test_list_moods_with_insufficient_permissions(self, mood_repository, user):
        command = GetMoodsCommand(user_id='some_other_user_id')
        with pytest.raises(InsufficientPermissionsError, match='Not enough permissions'):
            await list_moods(mood_repository, command, user)


class TestUpdateMood:
    @pytest.mark.asyncio
    async def test_update_mood_as_owner(self, mood_repository, user_with_moods):
        current_user = user_with_moods
        moods = current_user.moods
        mood_to_update = mood_repository._model_to_entity(moods[0])

        update_command = UpdateMoodCommand(
            user_id=current_user.id,
            mood_id=mood_to_update.id,
            visual_scale=(mood_to_update.visual_scale.value % 5) + 1,
            associated_emotions=[{'name': 'surprise', 'intensity': 5}],
            triggers=[{'name': 'unexpected event'}],
            description='Feeling surprised',
        )

        updated_mood = await update_mood(mood_repository, update_command, current_user)
        assert updated_mood.visual_scale.value != mood_to_update.visual_scale.value
        assert updated_mood.associated_emotions == [AssociatedEmotion(name='surprise', intensity=5)]
        assert updated_mood.triggers == [EmotionalTrigger(name='unexpected event')]
        assert updated_mood.description == 'Feeling surprised'

    @pytest.mark.asyncio
    async def test_update_mood_as_admin(self, mood_repository, admin_user, user_with_moods):
        current_user = admin_user
        moods = user_with_moods.moods
        mood_to_update = mood_repository._model_to_entity(moods[0])

        update_command = UpdateMoodCommand(
            user_id=user_with_moods.id,
            mood_id=mood_to_update.id,
            visual_scale=(mood_to_update.visual_scale.value % 5) + 1,
            associated_emotions=[{'name': 'anger', 'intensity': 7}],
            triggers=[{'name': 'frustrating event'}],
            description='Feeling angry',
        )

        updated_mood = await update_mood(mood_repository, update_command, current_user)
        assert updated_mood.visual_scale.value != mood_to_update.visual_scale.value
        assert updated_mood.associated_emotions == [AssociatedEmotion(name='anger', intensity=7)]
        assert updated_mood.triggers == [EmotionalTrigger(name='frustrating event')]
        assert updated_mood.description == 'Feeling angry'

    @pytest.mark.asyncio
    async def test_update_mood_with_insufficient_permissions(self, mood_repository, other_user):
        current_user = other_user
        # Assuming there's a mood with this ID for testing purposes
        mood_id = 'some_mood_id'

        update_command = UpdateMoodCommand(
            user_id='some_other_user_id',
            mood_id=mood_id,
            visual_scale=3,
            associated_emotions=[{'name': 'sadness', 'intensity': 6}],
            triggers=[{'name': 'bad news'}],
            description='Feeling sad',
        )

        with pytest.raises(InsufficientPermissionsError, match='Not enough permissions'):
            await update_mood(mood_repository, update_command, current_user)


class TestDeleteMood:
    @pytest.mark.asyncio
    async def test_delete_mood_as_owner(self, mood_repository, user_with_moods):
        current_user = user_with_moods
        moods = current_user.moods
        mood_to_delete = mood_repository._model_to_entity(moods[0])

        command = DeleteMoodCommand(user_id=current_user.id, mood_id=mood_to_delete.id)

        await delete_mood(mood_repository, command, current_user)

        with pytest.raises(
            Exception,
            match='Mood not found',  # Adjust exception type and message as needed
        ):
            await mood_repository.find_mood_by_id(mood_to_delete.id, current_user.id)

    @pytest.mark.asyncio
    async def test_delete_mood_as_admin(self, mood_repository, admin_user, user_with_moods):
        current_user = admin_user
        moods = user_with_moods.moods
        mood_to_delete = mood_repository._model_to_entity(moods[0])

        command = DeleteMoodCommand(user_id=user_with_moods.id, mood_id=mood_to_delete.id)

        await delete_mood(mood_repository, command, current_user)

        with pytest.raises(
            Exception,
            match='Mood not found',  # Adjust exception type and message as needed
        ):
            await mood_repository.find_mood_by_id(mood_to_delete.id, user_with_moods.id)

    @pytest.mark.asyncio
    async def test_delete_mood_with_insufficient_permissions(self, mood_repository, other_user):
        current_user = other_user
        # Assuming there's a mood with this ID for testing purposes
        mood_id = 'some_mood_id'
        user_id = 'some_other_user_id'

        command = DeleteMoodCommand(user_id=user_id, mood_id=mood_id)

        with pytest.raises(InsufficientPermissionsError, match='Not enough permissions'):
            await delete_mood(mood_repository, command, current_user)
