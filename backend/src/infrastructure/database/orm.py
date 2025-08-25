from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class UserModel:
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    id: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(default='')
    last_name: Mapped[str] = mapped_column(default='')
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
