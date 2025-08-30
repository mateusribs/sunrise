import pytest
from pydantic_core import ValidationError

from src.domain.entities import AssociatedEmotion, Mood, RegistryType, VisualScale
from src.domain.exceptions.mood_exceptions import InvalidEmotionIntensityError


def test_create_valid_mood():
    mood = Mood(
        user_id='1',
        registry_type=RegistryType.DAILY,
        visual_scale=VisualScale.HAPPY,
        associated_emotions=[AssociatedEmotion.JOY],
        emotions_intensity={AssociatedEmotion.JOY: 5},
        triggers=['Had a great day!'],
        description='Feeling joyful and content.',
    )
    assert isinstance(mood.id, str)
    assert mood.registry_type == RegistryType.DAILY
    assert mood.visual_scale == VisualScale.HAPPY
    assert mood.associated_emotions == [AssociatedEmotion.JOY]
    assert mood.emotions_intensity == {AssociatedEmotion.JOY: 5}
    assert mood.triggers == ['Had a great day!']
    assert mood.description == 'Feeling joyful and content.'


def test_create_invalid_registry_type():
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type='invalid_type',
            visual_scale=VisualScale.HAPPY,
            associated_emotions=[AssociatedEmotion.JOY],
            emotions_intensity={AssociatedEmotion.JOY: 5},
        )


def test_create_invalid_visual_scale():
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type=RegistryType.DAILY,
            visual_scale='invalid_scale',
            associated_emotions=[AssociatedEmotion.JOY],
            emotions_intensity={AssociatedEmotion.JOY: 5},
        )


def test_create_invalid_associated_emotions():
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type=RegistryType.DAILY,
            visual_scale=VisualScale.HAPPY,
            associated_emotions=['invalid_emotion'],
            emotions_intensity={AssociatedEmotion.JOY: 5},
        )


def test_create_invalid_emotions_intensity_key():
    with pytest.raises(ValidationError):
        Mood(
            user_id='1',
            registry_type=RegistryType.DAILY,
            visual_scale=VisualScale.HAPPY,
            associated_emotions=[AssociatedEmotion.JOY],
            emotions_intensity={'invalid_emotion': 5},
        )


@pytest.mark.parametrize('intensity', [0, 11, -1, 100])
def test_create_invalid_emotions_intensity_value(intensity):
    with pytest.raises(InvalidEmotionIntensityError):
        Mood(
            user_id='1',
            registry_type=RegistryType.DAILY,
            visual_scale=VisualScale.HAPPY,
            associated_emotions=[AssociatedEmotion.JOY],
            emotions_intensity={AssociatedEmotion.JOY: intensity},
        )
