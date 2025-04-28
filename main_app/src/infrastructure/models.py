from enum import Enum
from typing import Type

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    object_mapper,
    relationship,
)

from main_app.src.infrastructure.types import DomainModel


class Base(DeclarativeBase):
    def to_domain(
        self, 
        dataclass: Type[DomainModel]
    ) -> DomainModel:
        """Mapping ORM model to dataclass"""
        data = {
            attr.key: getattr(self, attr.key)
            for attr in object_mapper(self).attrs
        }
        return dataclass(**data)


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        sa.Integer, autoincrement=True, primary_key=True, index=True,
        comment="Unique user ID"
    )
    username: Mapped[str] = mapped_column(
        sa.String(length=255), unique=True, nullable=False, index=True, 
        comment="Unique username"
    )
    hashed_password: Mapped[str] = mapped_column(
        "hashed_password", sa.String(length=255), nullable=False,
        comment="Hashed user password"
    )
    salt: Mapped[str] = mapped_column(
        sa.String(length=16), nullable=False, 
        comment="Salt used for password hashing"
    )
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole), nullable=False, default=UserRole.USER, 
        comment="User role (USER or ADMIN)"
    )
    websocket_configs: Mapped[list["OkxListenerConfig"]] = relationship(
        "OkxListenerConfig", back_populates="user"
    )


class WebSocketConfig(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        sa.Integer, autoincrement=True, primary_key=True, index=True, 
        comment="Unique WebSocket config ID"
    )
    conn_name: Mapped[str] = mapped_column(
        sa.String(length=250), unique=True, index=True,
        comment="""Name of connection used to 
        distinguish WebSocket configurations."""
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id"), index=True, 
        comment="Reference to the user owning the WebSocket config"
    )
    instType: Mapped[str] = mapped_column(
        "instrument_type", sa.String(length=10), default="ANY", 
        comment="Instrument type for subscription"
    )
    account: Mapped[bool] = mapped_column(
        "account_updates", sa.Boolean, default=False, 
        comment="Receive account updates"
    )
    positions: Mapped[bool] = mapped_column(
        "position_updates", sa.Boolean, default=True, 
        comment="Receive position updates"
    )
    liq_warning: Mapped[bool] = mapped_column(
        "liquidation_warning", sa.Boolean, default=False, 
        comment="Receive liquidation warnings"
    )
    api_key: Mapped[str] = mapped_column(
        "encrypted_api_key", sa.String(length=255), nullable=False, 
        comment="Encrypted API key"
    )
    secret_key: Mapped[str] = mapped_column(
        "encrypted_secret_key", sa.String(length=255), nullable=False, 
        comment="Encrypted secret key"
    )
    passphrase: Mapped[str] = mapped_column(
        "encrypted_passphrase", sa.String(length=255), nullable=False, 
        comment="Encrypted passphrase"
    )


class OkxListenerConfig(WebSocketConfig):
    __tablename__ = "okx_listener_configs"
    __table_args__ = (
        sa.CheckConstraint("""
            (
                SELECT COUNT(*) 
                FROM okx_listener_configs 
                WHERE user_id = user_id
            ) <= 2
            """,
            name="check_max_connections"
        ),
    )
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="websocket_configs"
    )