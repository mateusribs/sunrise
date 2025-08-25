"""Exceções específicas do domínio de usuários"""


class UserDomainError(Exception):
    """Exceção base para erros do domínio de usuários"""
    pass


class UserAlreadyExistsError(UserDomainError):
    """Exceção para quando um usuário já existe"""
    pass


class UsernameAlreadyExistsError(UserDomainError):
    """Exceção para quando um nome de usuário já existe"""
    pass


class UserNotFoundError(UserDomainError):
    """Exceção para quando um usuário não é encontrado"""
    pass


class InvalidCredentialsError(UserDomainError):
    """Exceção para credenciais inválidas"""
    pass


class InactiveUserError(UserDomainError):
    """Exceção para usuário inativo"""
    pass


class InsufficientPermissionsError(UserDomainError):
    """Exceção para permissões insuficientes"""
    pass


class InvalidPasswordError(UserDomainError):
    """Exceção para senha inválida"""
    pass


class InvalidUsernameError(UserDomainError):
    """Exceção para nome de usuário inválido"""
    pass
