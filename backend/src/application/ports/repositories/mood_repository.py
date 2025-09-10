from abc import ABC, abstractmethod

from src.domain.entities.mood import Mood


class MoodRepository(ABC):
    @abstractmethod
    async def save(self, mood: Mood) -> Mood:
        pass

    @abstractmethod
    async def list_moods(self, user_id: str, offset: int, limit: int) -> list[Mood]:
        pass

    @abstractmethod
    async def find_mood_by_id(self, mood_id: str, user_id: str) -> Mood:
        pass

    @abstractmethod
    async def update(self, mood: Mood) -> Mood:
        pass

    @abstractmethod
    async def delete(self, mood_id: str, user_id: str) -> None:
        pass
