from abc import ABC, abstractmethod

from src.domain.entities.mood import Mood


class MoodRepository(ABC):
    @abstractmethod
    async def save(self, mood: Mood) -> Mood:
        pass

    @abstractmethod
    async def list_moods(self, user_id: str, offset: int, limit: int) -> list[Mood]:
        pass
