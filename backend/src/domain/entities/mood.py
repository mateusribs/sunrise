import uuid
from enum import Enum
from typing import Any

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

    def update_visual_scale(self, new_scale: VisualScale) -> None:
        self.visual_scale = VisualScale(new_scale)

    def update_associated_emotions(self, new_emotions: list[dict[str, Any]]) -> None:
        self.associated_emotions.clear()
        for emotion in new_emotions:
            self.associated_emotions.append(AssociatedEmotion(**emotion))

    def update_triggers(self, new_triggers: list[dict[str, Any]]) -> None:
        self.triggers.clear()
        for trigger in new_triggers:
            self.triggers.append(EmotionalTrigger(**trigger))

    def update_description(self, new_description: str) -> None:
        self.description = new_description if new_description is not None else self.description
