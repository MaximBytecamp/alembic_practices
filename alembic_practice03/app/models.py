from __future__ import annotations

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",                            # обычный индекс
    "uq": "uq_%(table_name)s_%(column_0_name)s",              # unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",             # check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # FK
    "pk": "pk_%(table_name)s",                                 # PK
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r}>"



