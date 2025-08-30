from src.application.dto.mood_dto import RegisterMoodCommand
from src.application.ports.repositories.mood_repository import MoodRepository
from src.domain.entities.mood import Mood
from src.domain.entities.user import User


async def register_mood(
    mood_repository: MoodRepository, mood_command: RegisterMoodCommand, current_user: User
) -> Mood:
    mood = Mood(
        user_id=current_user.id,
        registry_type=mood_command.registry_type,
        visual_scale=mood_command.visual_scale,
        associated_emotions=mood_command.associated_emotions,
        triggers=mood_command.triggers,
        description=mood_command.description,
    )
    return await mood_repository.save(mood)
