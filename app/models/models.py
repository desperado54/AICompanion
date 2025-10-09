from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.utils.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    companions: Mapped[list["Companion"]] = relationship("Companion", back_populates="owner", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Companion(Base):
    __tablename__ = "companions"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_companion_user_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(50))
    birth_country: Mapped[Optional[str]] = mapped_column(String(80))
    personality: Mapped[Optional[str]] = mapped_column(Text)
    education: Mapped[Optional[str]] = mapped_column(String(120))
    background: Mapped[Optional[str]] = mapped_column(Text)

    system_prompt: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner: Mapped[Optional[User]] = relationship("User", back_populates="companions")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="companion")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    companion_id: Mapped[int] = mapped_column(Integer, ForeignKey("companions.id", ondelete="CASCADE"), nullable=False)

    # Used by LangChain SQLChatMessageHistory to isolate memory per conversation
    session_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="conversations")
    companion: Mapped[Companion] = relationship("Companion", back_populates="conversations")
