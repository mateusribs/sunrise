import pytest
from pydantic_core import ValidationError

from src.domain.entities import AssociatedEmotion, Mood, RegistryType, VisualScale
from src.domain.entities.associated_emotion import AssociatedEmotionEnum
from src.domain.entities.emotional_trigger import EmotionalTrigger


@pytest.fixture
def associated_emotion():
    return AssociatedEmotion(name=AssociatedEmotionEnum.JOY, intensity=5)


@pytest.fixture
def emotional_trigger():
    return EmotionalTrigger(name='Had a great day!')


def test_create_valid_mood(associated_emotion, emotional_trigger):
    mood = Mood(
        user_id='1',
        registry_type=RegistryType.DAILY,
        visual_scale=VisualScale.HAPPY,
        associated_emotions=[associated_emotion],
        triggers=[emotional_trigger],
        description='Feeling joyful and content.',
    )
    assert isinstance(mood.id, str)
    assert mood.registry_type == RegistryType.DAILY
    assert mood.visual_scale == VisualScale.HAPPY
    assert mood.associated_emotions == [associated_emotion]
    assert mood.triggers == [emotional_trigger]
    assert mood.description == 'Feeling joyful and content.'


def test_create_invalid_registry_type(associated_emotion):
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type='invalid_type',
            visual_scale=VisualScale.HAPPY,
            associated_emotions=[associated_emotion],
        )


def test_create_invalid_visual_scale(associated_emotion):
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type=RegistryType.DAILY,
            visual_scale='invalid_scale',
            associated_emotions=[associated_emotion],
        )
