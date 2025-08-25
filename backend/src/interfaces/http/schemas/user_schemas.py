import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.domain.entities.user import User


class UserRegisterRequest(BaseModel):
    """Schema para requisição de registro de usuário"""

    username: str
    email: EmailStr
    password: str
    first_name: str = ''
    last_name: str = ''


class UserUpdateRequest(BaseModel):
    """Schema para requisição de atualização de usuário"""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema para resposta de usuário"""

    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, user: User) -> 'UserResponse':
        """Converte entidade de domínio para schema de resposta"""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=user.is_admin,
            is_active=user.is_active,
        )


class UserListResponse(BaseModel):
    """Schema para resposta de lista de usuários"""

    users: list[UserResponse]


class LoginRequest(BaseModel):
    """Schema para requisição de login"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema para resposta de token"""

    access_token: str
    token_type: str = 'bearer'
