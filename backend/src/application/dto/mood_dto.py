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
