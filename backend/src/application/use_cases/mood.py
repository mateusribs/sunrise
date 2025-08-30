from src.application.dto.mood_dto import GetMoodsCommand, RegisterMoodCommand
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
        if not command.is_admin:
            raise InsufficientPermissionsError('Not enough permissions')

    return await mood_repository.list_moods(
        user_id=command.user_id, offset=command.offset, limit=command.limit
    )
