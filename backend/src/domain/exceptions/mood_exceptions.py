class MoodDomainError(Exception):
    """Exceção base para erros do domínio de humor"""

    pass


class InvalidEmotionIntensityError(MoodDomainError):
    """Exceção para intensidades de emoções inválidas"""

    pass
