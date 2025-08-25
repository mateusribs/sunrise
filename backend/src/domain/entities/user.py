import re
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.domain.exceptions.user_exceptions import InvalidPasswordError, InvalidUsernameError


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: Optional[str] = Field(default='')
    last_name: Optional[str] = Field(default='')
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)

    @field_validator('username')
    @classmethod
    def validate_username(cls, username: str) -> str:
        """
        Validates the username to ensure it is not empty or just whitespace.
        Raises:
            InvalidUsernameError: If the username is empty or just whitespace.
        """
        if not username or not username.strip():
            raise InvalidUsernameError("Username cannot be empty")
        return username

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Validates the password according to the following rules:
        - Must be at least 8 characters long.
        - Must contain at least one digit.
        - Must contain at least one uppercase letter.
        - Must contain at least one lowercase letter.
        Raises:
            InvalidPasswordError: If the password does not meet any of the above criteria.
        """
        if len(password) < 8:
            raise InvalidPasswordError("Password must be at least 8 characters long")
        if not re.search(r'\d', password):
            raise InvalidPasswordError("Password must contain at least one digit")
        if not re.search(r'[A-Z]', password):
            raise InvalidPasswordError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise InvalidPasswordError("Password must contain at least one lowercase letter")
        return password

    def update_username(self, new_username: str) -> None:
        self.validate_username(new_username)
        self.username = new_username

    def update_profile(self, first_name: str = None, last_name: str = None) -> None:
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def make_admin(self) -> None:
        self.is_admin = True

    def remove_admin(self) -> None:
        self.is_admin = False

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
