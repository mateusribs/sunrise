from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions.sql_database import (
    EntityNotFoundError,
    IntegrityConstraintViolationError,
)
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
        associated_emotions = SQLAlchemyMoodRepository._convert_associated_emotions_to_model(
            mood.associated_emotions, mood.id
        )
        triggers = SQLAlchemyMoodRepository._convert_triggers_to_model(mood.triggers, mood.id)

        return MoodModel(
            id=mood.id,
            user_id=mood.user_id,
            visual_scale=mood.visual_scale.value,
            registry_type=mood.registry_type.value,
            description=mood.description,
            associated_emotions=associated_emotions,
            triggers=triggers,
        )

    @staticmethod
    def _convert_associated_emotions_to_model(
        associated_emotions: list[AssociatedEmotion], mood_id: str
    ) -> list[AssociatedEmotionsModel]:
        return [
            AssociatedEmotionsModel(
                mood_id=mood_id,
                name=emotion.name.value,
                intensity=emotion.intensity,
            )
            for emotion in associated_emotions
        ]

    @staticmethod
    def _convert_triggers_to_model(
        triggers: list[EmotionalTrigger], mood_id: str
    ) -> list[EmotionalTriggerModel]:
        return [
            EmotionalTriggerModel(
                mood_id=mood_id,
                name=trigger.name,
            )
            for trigger in triggers
        ]

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

    async def find_mood_by_id(self, mood_id: str, user_id: str) -> Mood | None:
        result = await self.session.scalar(
            select(MoodModel).where(MoodModel.id == mood_id, MoodModel.user_id == user_id)
        )
        if result:
            return self._model_to_entity(result)
        raise EntityNotFoundError('Mood not found')

    async def update(self, mood: Mood) -> Mood:
        mood_db = await self.session.scalar(
            select(MoodModel).where(MoodModel.id == mood.id, MoodModel.user_id == mood.user_id)
        )
        if not mood_db:
            raise EntityNotFoundError('Mood not found')

        mood_db.visual_scale = mood.visual_scale.value
        mood_db.associated_emotions = (
            SQLAlchemyMoodRepository._convert_associated_emotions_to_model(
                mood.associated_emotions, mood.id
            )
        )
        mood_db.triggers = SQLAlchemyMoodRepository._convert_triggers_to_model(
            mood.triggers, mood.id
        )
        mood_db.description = mood.description

        try:
            await self.session.commit()
            await self.session.refresh(mood_db)
            return self._model_to_entity(mood_db)
        except IntegrityError as e:
            await self.session.rollback()
            raise IntegrityConstraintViolationError(f'Integrity constraint violated: {e}')

    async def delete(self, mood_id: str, user_id: str) -> None:
        mood_db = await self.session.scalar(
            select(MoodModel).where(MoodModel.id == mood_id, MoodModel.user_id == user_id)
        )
        if not mood_db:
            raise EntityNotFoundError('Mood not found')

        try:
            await self.session.delete(mood_db)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise IntegrityConstraintViolationError(f'Integrity constraint violated: {e}')
