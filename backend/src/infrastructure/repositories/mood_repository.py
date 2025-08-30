from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions.sql_database import IntegrityConstraintViolationError
from src.application.ports.repositories.mood_repository import MoodRepository
from src.domain.entities.associated_emotion import AssociatedEmotion
from src.domain.entities.emotional_trigger import EmotionalTrigger
from src.domain.entities.mood import Mood
from src.infrastructure.database.orm import (
    AssociatedEmotionsModel,
    EmotionalTriggerModel,
    MoodModel,
    UserModel,
)


class SQLAlchemyMoodRepository(MoodRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _model_to_entity(mood_model: MoodModel) -> Mood:
        associated_emotions = [
            AssociatedEmotion(name=emotion.name, intensity=emotion.intensity)
            for emotion in mood_model.associated_emotions
        ]

        triggers = [EmotionalTrigger(name=trigger.name) for trigger in mood_model.triggers]

        return Mood(
            id=mood_model.id,
            user_id=mood_model.user_id,
            registry_type=mood_model.registry_type,
            visual_scale=mood_model.visual_scale,
            associated_emotions=associated_emotions,
            triggers=triggers,
            description=mood_model.description,
        )

    @staticmethod
    def _entity_to_model(mood: Mood) -> MoodModel:
        associated_emotions = [
            AssociatedEmotionsModel(
                mood_id=mood.id,
                name=emotion.name.value,
                intensity=emotion.intensity,
            )
            for emotion in mood.associated_emotions
        ]

        triggers = [
            EmotionalTriggerModel(
                mood_id=mood.id,
                name=trigger.name,
            )
            for trigger in mood.triggers
        ]

        return MoodModel(
            id=mood.id,
            user_id=mood.user_id,
            visual_scale=mood.visual_scale.value,
            registry_type=mood.registry_type.value,
            description=mood.description,
            associated_emotions=associated_emotions,
            triggers=triggers,
        )

    async def save(self, mood: Mood) -> Mood:
        mood_db = self._entity_to_model(mood)
        try:
            self.session.add(mood_db)
            await self.session.commit()
            await self.session.refresh(mood_db)
            return self._model_to_entity(mood_db)
        except IntegrityError as e:
            await self.session.rollback()
            raise IntegrityConstraintViolationError(f'Integrity constraint violated: {e}')

    async def list_moods(self, user_id: str, offset: int, limit: int) -> list[Mood]:
        result = await self.session.scalars(
            select(MoodModel).where(UserModel.id == user_id).offset(offset).limit(limit)
        )
        return [self._model_to_entity(mood) for mood in result.all()]
