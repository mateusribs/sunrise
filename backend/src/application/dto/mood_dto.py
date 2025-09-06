from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegisterMoodCommand:
    user_id: str
    registry_type: str
    visual_scale: int
    associated_emotions: list[dict[str, Any]]
    triggers: list[dict[str, Any]] = field(default_factory=list)
    description: str = ''


@dataclass
class GetMoodsCommand:
    user_id: str
    offset: int = 0
    limit: int = 100


@dataclass
class UpdateMoodCommand:
    user_id: str
    mood_id: str
    visual_scale: int | None = None
    associated_emotions: list[dict[str, Any]] | None = None
    triggers: list[dict[str, Any]] | None = None
    description: str | None = None


@dataclass
class DeleteMoodCommand:
    user_id: str
    mood_id: str
