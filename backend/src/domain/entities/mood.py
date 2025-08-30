import uuid
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from src.domain.exceptions.mood_exceptions import InvalidEmotionIntensityError


class VisualScale(Enum):
    VERY_SAD = 1
    SAD = 2
    NEUTRAL = 3
    HAPPY = 4
    VERY_HAPPY = 5


class RegistryType(Enum):
    DAILY = 'daily'
    EVENT = 'event'


class AssociatedEmotion(Enum):
    ANGER = 'anger'
    FEAR = 'fear'
    JOY = 'joy'
    SADNESS = 'sadness'
    SURPRISE = 'surprise'


class Mood(BaseModel):
    user_id: str
    registry_type: RegistryType
    visual_scale: VisualScale
    associated_emotions: list[AssociatedEmotion]
    emotions_intensity: dict[AssociatedEmotion, int]

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    triggers: list[str] = []
    description: str = ''

    @field_validator('emotions_intensity')
    def check_emotions_intensity(cls, value):
        lower_bound = 1
        upper_bound = 10
        for emotion, intensity in value.items():
            if not (lower_bound <= intensity <= upper_bound):
                raise InvalidEmotionIntensityError(
                    f'Intensity for {emotion} must be between {lower_bound} and {upper_bound}'
                )
        return value
