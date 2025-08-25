from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateUserCommand:
    """Comando para criar um usuário"""

    username: str
    email: str
    password: str
    first_name: str = ''
    last_name: str = ''


@dataclass
class UpdateUserCommand:
    """Comando para atualizar um usuário"""

    user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class LoginCommand:
    """Comando para login"""

    email: str
    password: str


@dataclass
class GetUsersCommand:
    """Comando para obter usuários"""

    is_active: bool
    is_admin: bool
    offset: int = 0
    limit: int = 10
