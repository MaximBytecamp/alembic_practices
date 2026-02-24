from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

# users  ←→  user_project_roles  ←→  projects
#                       ↓
#                     roles


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[List["UserProjectRole"]] = relationship(
        "UserProjectRole", back_populates="role"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )


    memberships: Mapped[List["UserProjectRole"]] = relationship(
        "UserProjectRole", back_populates="project"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r}>"


class UserProjectRole(Base):
    """Один пользователь может иметь несколько ролей в одном проекте."""

    __tablename__ = "user_project_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", "role_id", name="uq_user_project_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    project: Mapped["Project"] = relationship("Project", back_populates="memberships")
    role: Mapped["Role"] = relationship("Role", back_populates="memberships")

    def __repr__(self) -> str:
        return (
            f"<UserProjectRole user={self.user_id} "
            f"project={self.project_id} role={self.role_id}>"
        )