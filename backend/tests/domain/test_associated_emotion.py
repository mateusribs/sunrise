import pytest
from pydantic_core import ValidationError

from src.domain.entities.associated_emotion import AssociatedEmotion, AssociatedEmotionEnum


def test_create_valid_associated_emotion():
    emotion = AssociatedEmotion(name=AssociatedEmotionEnum.JOY, intensity=5)
    assert emotion.name == AssociatedEmotionEnum.JOY
    assert emotion.intensity == 5


def test_create_invalid_name_associated_emotion():
    with pytest.raises(ValidationError):
        AssociatedEmotion(name='another', intensity=6)


@pytest.mark.parametrize('intensity', [0, 11, -1, 15])
def test_create_invalid_intensity_associated_emotion(intensity):
    with pytest.raises(ValidationError):
        AssociatedEmotion(name=AssociatedEmotionEnum.JOY, intensity=intensity)
