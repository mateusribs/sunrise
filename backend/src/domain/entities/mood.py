import uuid
from enum import Enum

from pydantic import BaseModel, Field

from src.domain.entities.associated_emotion import AssociatedEmotion
from src.domain.entities.emotional_trigger import EmotionalTrigger


class VisualScale(Enum):
    VERY_SAD = 1
    SAD = 2
    NEUTRAL = 3
    HAPPY = 4
    VERY_HAPPY = 5


class RegistryType(Enum):
    DAILY = 'daily'
    EVENT = 'event'


class Mood(BaseModel):
    user_id: str
    registry_type: RegistryType
    visual_scale: VisualScale
    associated_emotions: list[AssociatedEmotion]

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    triggers: list[EmotionalTrigger] = Field(default_factory=list)
    description: str = ''
