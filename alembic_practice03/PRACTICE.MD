# Практика 03 — Naming Convention: фундамент стабильных миграций

## Цель

Научиться подключать naming convention к MetaData, чтобы constraints и индексы
получали **детерминированные имена**. Понять, зачем это нужно и какие проблемы
решает.


---

## Задание 1. Включить naming convention в MetaData

### Проблема

Без naming convention SQLAlchemy/Alembic **назначает имена автоматически** и
часто — **по-разному в разных СУБД и окружениях**.

Например, FK constraint может получить:
- `fk_projects_owner_id_users` — в одном окружении
- `projects_owner_id_fkey` — в другом
- безымянный constraint — в третьем

Это приводит к **фантомным диффам** при autogenerate: Alembic думает, что
constraint изменился, и пытается его пересоздать.

### Что сделать

Открой `app/models.py` и замени `Base`:

```python
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
```

### Проверь

```bash
alembic revision --autogenerate -m "add naming convention"
```

Открой файл миграции. Alembic может предложить:
- пересоздать constraints с новыми именами
- или не заметить разницы (если SQLite и constraints не именовались)

> **На SQLite** эффект может быть неявным. На PostgreSQL ты бы сразу увидел
> rename constraints. Главное — **все новые** constraints с этого момента
> будут получать предсказуемые  по формулам выше.

Примени:

```bash
alembic upgrade head
```

### Что запомнить

- Naming convention задаётся **один раз** в MetaData
- Все новые PK, FK, UQ, IX автоматически получают имена по шаблону
- Это **не** переименовывает уже существующие constraints (для этого нужна
  отдельная миграция)

---


## Задание 2. Уникальность email (UNIQUE constraint)

### Что сделать

В `app/models.py` добавь `unique=True` к `email`:

```python
# было:
email: Mapped[str] = mapped_column(String(256), nullable=False)

# стало:
email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
```

### Сгенерируй миграцию

```bash
alembic revision --autogenerate -m "add unique email"
```

Открой файл. Найди имя constraint:

```python
# Ожидаемое (благодаря naming convention):
op.create_unique_constraint('uq_users_email', 'users', ['email'])
```

Если бы naming convention не было, имя было бы `None` или случайное.

### Примени и проверь

```bash
alembic upgrade head
```

## Задание 3. Внешний ключ с предсказуемым именем (FK constraint)

FK уже есть в модели `Project.owner_id → User.id`, но сейчас мы убедимся,
что naming convention дал ему правильное имя.

### Проверь

```bash
python3 -c "
import sqlite3; conn = sqlite3.connect('practice.db')
for fk in conn.execute('PRAGMA foreign_key_list(projects)').fetchall():
    print('FK:', fk)
conn.close()
"
```

В SQLite PRAGMA не показывает **имя** FK constraint (это ограничение SQLite).
Но в файле миграции (`initial: users + projects`) ты можешь найти, как он был
создан — посмотри `sa.ForeignKeyConstraint(...)`.


## Задание 4. Индексы — обычный и уникальный

### Что сделать

В `app/models.py` добавь индексы:

```python
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)  # ← добавил index
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    ...
```

`index=True` + naming convention → имя индекса: `ix_title`

Для `email` уже есть `unique=True` (задание 2), уникальный индекс уже создан.

### Сгенерируй и примени

```bash
alembic revision --autogenerate -m "add index on projects.title"
alembic upgrade head
```

### Проверь имена индексов

```bash
python3 -c "
import sqlite3; conn = sqlite3.connect('practice.db')
idxs = conn.execute(\"SELECT name, tbl_name FROM sqlite_master WHERE type='index'\").fetchall()
for i in idxs: print(i)
conn.close()
"
```

Ожидаемый вывод:

```
('ix_title', 'projects')
('uq_users_email', 'users')
```
