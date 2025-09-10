from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.mood import Mood


class MoodResponse(BaseModel):
    id: str
    user_id: str
    registry_type: str
    visual_scale: int
    associated_emotions: list[dict]
    triggers: list[dict]
    description: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, mood: Mood) -> 'MoodResponse':
        """Converte entidade de domínio para schema de resposta"""
        associated_emotions = [
            associated_emotion.model_dump() for associated_emotion in mood.associated_emotions
        ]
        triggers = [trigger.model_dump() for trigger in mood.triggers]
        return cls(
            id=mood.id,
            user_id=mood.user_id,
            registry_type=mood.registry_type,
            visual_scale=mood.visual_scale,
            associated_emotions=associated_emotions,
            triggers=triggers,
            description=mood.description,
        )


class ListMoodsResponse(BaseModel):
    moods: list[MoodResponse]


class RegisterMoodRequest(BaseModel):
    registry_type: str
    visual_scale: int
    associated_emotions: list[dict]
    triggers: list[dict]
    description: str


class FilterQueryMoods(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, gt=0, le=100)
