from enum import Enum

from pydantic import BaseModel, Field


class AssociatedEmotionEnum(Enum):
    ANGER = 'anger'
    FEAR = 'fear'
    JOY = 'joy'
    SADNESS = 'sadness'
    SURPRISE = 'surprise'


class AssociatedEmotion(BaseModel):
    name: AssociatedEmotionEnum
    intensity: int = Field(..., ge=1, le=10)  # Intensity between 1 and 10
