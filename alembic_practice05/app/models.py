from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, MetaData, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r}>"


#default=5 -> на уровне ORM -> если мы передаем значения в Pydantic-модели, то
#если значение поля не передалось, то мы используем дефолтное значение, но это дефолтное
#значение не связано с дефолнтым значением для этого поля на уровне базы данных 
#то есть age = default=14 не будет в базе данных рассматривается как значение по умолчанию,
#если в поле ничего не передали. значение 14 в таком случае в базе данных не сохранится 
#чтобы было на уровне бд мы испоьзуем server_default -> которое age=server_default(14)->
#будет автоматически для этого поля подставлять значение уже в базе данных если никакое
#значение не было передано. И при командах DML (SELECT, INSERT, DELETE, UPDATE) ->
#это значение по умолчанию будет браться автоматически и использоваться

#НО server_default не является частью DDL (схемы-структуры в базе данных) а значит
#не будет рассматриваться алембиком при изменении в миграциях, чтобы рассматривался server_default мы подключаем свойство compare_server_default
#которое включает server_default в механизм DDL, а значит любое изменение будет отображаться и в миграциях 