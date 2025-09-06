from src.application.dto.mood_dto import (
    DeleteMoodCommand,
    GetMoodsCommand,
    RegisterMoodCommand,
    UpdateMoodCommand,
)
from src.application.ports.repositories.mood_repository import MoodRepository
from src.domain.entities.mood import Mood
from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import InsufficientPermissionsError


async def register_mood(mood_repository: MoodRepository, mood_command: RegisterMoodCommand) -> Mood:
    mood = Mood(
        user_id=mood_command.user_id,
        registry_type=mood_command.registry_type,
        visual_scale=mood_command.visual_scale,
        associated_emotions=mood_command.associated_emotions,
        triggers=mood_command.triggers,
        description=mood_command.description,
    )
    return await mood_repository.save(mood)


async def list_moods(
    mood_repository: MoodRepository, command: GetMoodsCommand, current_user: User
) -> list[Mood]:
    if current_user.id != command.user_id:
        if not current_user.is_admin:
            raise InsufficientPermissionsError('Not enough permissions')

    return await mood_repository.list_moods(
        user_id=command.user_id, offset=command.offset, limit=command.limit
    )


async def update_mood(
    mood_repository: MoodRepository, mood_command: UpdateMoodCommand, current_user: User
) -> Mood:
    if current_user.id != mood_command.user_id:
        if not current_user.is_admin:
            raise InsufficientPermissionsError('Not enough permissions')

    mood = await mood_repository.find_mood_by_id(mood_command.mood_id, mood_command.user_id)

    mood.update_visual_scale(mood_command.visual_scale)
    mood.update_associated_emotions(mood_command.associated_emotions)
    mood.update_triggers(mood_command.triggers)
    mood.update_description(mood_command.description)

    return await mood_repository.update(mood)


async def delete_mood(
    mood_repository: MoodRepository, command: DeleteMoodCommand, current_user: User
) -> None:
    if current_user.id != command.user_id:
        if not current_user.is_admin:
            raise InsufficientPermissionsError('Not enough permissions')

    await mood_repository.delete(command.mood_id, command.user_id)
