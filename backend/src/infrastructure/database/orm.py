from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

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

    moods: Mapped[list['MoodModel']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


@table_registry.mapped_as_dataclass
class MoodModel:
    __tablename__ = 'moods'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    visual_scale: Mapped[int]
    registry_type: Mapped[str]
    description: Mapped[str]
    id: Mapped[str] = mapped_column(primary_key=True)

    associated_emotions: Mapped[list['AssociatedEmotionsModel']] = relationship(
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    triggers: Mapped[list['EmotionalTriggerModel']] = relationship(
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class AssociatedEmotionsModel:
    __tablename__ = 'associated_emotions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    mood_id: Mapped[str] = mapped_column(ForeignKey('moods.id'), nullable=False)
    name: Mapped[str]
    intensity: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class EmotionalTriggerModel:
    __tablename__ = 'emotional_triggers'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    mood_id: Mapped[str] = mapped_column(ForeignKey('moods.id'))
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )
