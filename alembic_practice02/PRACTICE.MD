## Задание 1 — Полный жизненный цикл миграции

**Сюжет:** добавить поле `is_active: bool` в модель `User`.

### Шаг 1. Измени модель

Открой `app/models.py`, добавь в класс `User`:

```python
from sqlalchemy import Boolean   # добавь в импорты

is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

### Шаг 2. Сгенерируй миграцию

```bash
alembic revision --autogenerate -m "add is_active to user"
```

### Шаг 3. Примени и проверь

```bash
alembic upgrade head
```


## Задание 2 — Переименование поля: поймать ошибку autogenerate

**Сюжет:** переименовать `email` → `login`.

### Шаг 1. Переименуй поле в модели

В `app/models.py` замени:

```python
# было:
email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

# стало:
login: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
```

### Шаг 2. Сгенерируй миграцию

```bash
alembic revision --autogenerate -m "rename email to login"
```

### Шаг 3. Открой файл и посмотри, что предлагает Alembic

> **Ожидаемое (неверное!) поведение autogenerate:**
> ```python
> def upgrade():
>     op.add_column('users', sa.Column('login', sa.String(256), ...))
>     op.create_unique_constraint(None, 'users', ['login'])
>     op.drop_column('users', 'email')
>
> def downgrade():
>     op.add_column('users', sa.Column('email', sa.String(256), ...))
>     op.drop_column('users', 'login')
> ```

### Почему это опасно

Alembic не умеет отличить переименование от «удалить + добавить»:
он видит только разницу между метаданными и схемой БД.

При применении такой миграции:
- сначала создаётся пустая колонка `login`
- потом удаляется `email` **со всеми данными**

Все email'ы пользователей будут **безвозвратно потеряны**.

### Шаг 4. Исправь миграцию вручную

Замени содержимое `upgrade()` и `downgrade()` на:

```python
def upgrade() -> None:
    op.alter_column('users', 'email', new_column_name='login')

def downgrade() -> None:
    op.alter_column('users', 'login', new_column_name='email')
```

### Шаг 5. Примени исправленную миграцию

```bash
alembic upgrade +1
```

## Задание 3 — NOT NULL на таблице с данными

**Сюжет:** добавить поле `age: int NOT NULL`.

### Шаг 1. Залей тестовые данные

```bash
python seed.py
```

Убедись, что в БД есть 3 пользователя — они не будут иметь поля `age`.

### Шаг 2. Добавь поле в модель

В `app/models.py` добавь в `User`:

```python
age: Mapped[int] = mapped_column(Integer, nullable=False)
```

### Шаг 3. Сгенерируй миграцию

```bash
alembic revision --autogenerate -m "add age to user"
```

Посмотри, что сгенерировал Alembic:

```python
# autogenerate предложит примерно это:
op.add_column('users', sa.Column('age', sa.Integer(), nullable=False))
```

### Шаг 4. Попробуй применить — увидишь ошибку

```bash
alembic upgrade +1
```

> **Ошибка:** `IntegrityError: NOT NULL constraint failed` — в уже существующих
> строках нет значения для `age`, и SQLite не может добавить `NOT NULL` колонку.

### Шаг 5. Исправь миграцию — три шага вместо одного

Открой файл миграции и замени `upgrade()` / `downgrade()`:

```python
def upgrade() -> None:
    # Шаг 1: добавляем колонку как nullable
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))

    # Шаг 2: заполняем дефолтным значением для существующих строк
    op.execute("UPDATE users SET age = 0 WHERE age IS NULL")

    # Шаг 3: делаем колонку NOT NULL
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('age', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'age')
```

> **Почему `batch_alter_table`?**
> SQLite не поддерживает `ALTER COLUMN` напрямую. `batch_alter_table` создаёт
> новую таблицу с нужной схемой, копирует данные и переименовывает — это
> стандартный способ изменения колонок в SQLite.

### Шаг 6. Примени исправленную миграцию

```bash
alembic upgrade +1
```

### Часть A. Создай «толстую» миграцию (специально плохой вариант)

#### Контекст

После заданий 1–4 в `app/models.py` у тебя есть `User` с колонками:
`id`, `login` (бывший email), `is_active`, `age`.

Теперь нужно добавить сразу несколько изменений, которые **логически не связаны**:

1. Добавить новую таблицу `Tag` (теги для будущего функционала)
2. Добавить колонку `bio` (текстовое поле профиля пользователя)
3. Добавить колонку `last_login_at` (техническое поле для аудита)

#### Шаг 1. Добавь всё в модели одним блоком

В `app/models.py` добавь новый класс и три поля сразу:

```python
from sqlalchemy import DateTime, Text   # добавь в импорты

# Новая таблица
class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex, например #FF5733

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"

# В класс User добавь:
bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
```

Не забудь добавить импорт `datetime` и `Optional`:
```python
from __future__ import annotations
from datetime import datetime
from typing import Optional
```

#### Шаг 2. Сгенерируй одну «толстую» миграцию

```bash
alembic revision --autogenerate -m "fat: add tags table, bio, last_login_at"
```

Открой файл миграции. В `upgrade()` ты увидишь всё вместе:
- `op.create_table('tags', ...)`
- `op.add_column('users', Column('bio', ...))`
- `op.add_column('users', Column('last_login_at', ...))`

**Запомни эту картину — это антипаттерн.**

#### Шаг 3. Применяем и проверяем что работает

```bash
alembic upgrade +1
```

### Часть B. Откатить и разбить на атомарные миграции

#### Почему «толстая» миграция — проблема

Представь, что при деплое на production:
- `create_table('tags')` — выполнилась ✅
- `add_column('bio')` — выполнилась ✅
- `add_column('last_login_at')` — **упала с ошибкой** ❌

Alembic откатит всю транзакцию (или не откатит, если DDL non-transactional).
Ты получаешь **частично применённую** миграцию: таблица `tags` есть, `bio` есть, `last_login_at` нет.
Понять что пошло не так и где остановиться — сложно.

Атомарная миграция = можно точно знать, что либо всё применилось, либо ничего.

#### Шаг 4. Откати «толстую» миграцию

```bash
alembic downgrade -1
```

#### Шаг 5. Удали «толстый» файл миграции

```bash
# Найди файл в alembic/versions/ с именем, содержащим "fat"
ls alembic/versions/

# Удали его
rm alembic/versions/<rev>_fat_add_tags_table_bio_last_login_at.py
```

> Модель в `app/models.py` **не трогай** — все три изменения там остаются.

#### Шаг 6. Создай 3 атомарные миграции

Создавай по одной — каждый раз генерируй пустую миграцию и пиши код вручную:

**Миграция 1 — только новая таблица:**

```bash
alembic revision -m "add tags table"
```

В `upgrade()` / `downgrade()` пиши:

```python
def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(64), unique=True, nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('tags')
```

Применяй и проверяй:

```bash
alembic upgrade +1
# убедись что таблица tags появилась, users — без изменений
```

---

**Миграция 2 — только поле профиля:**

```bash
alembic revision -m "add users.bio"
```

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'bio')
```

```bash
alembic upgrade +1
```

---

**Миграция 3 — только техническое поле аудита:**

```bash
alembic revision -m "add users.last_login_at"
```

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'last_login_at')
```

```bash
alembic upgrade +1
```

---

#### Шаг 7. Проверь итоговую историю

```bash
alembic history --verbose
```

Ты должен увидеть аккуратную цепочку:

```
<rev> -> <rev>  add users.last_login_at
<rev> -> <rev>  add users.bio
<rev> -> <rev>  add tags table
...             (предыдущие миграции)
```

#### Шаг 8. Проверь откат по одной

```bash
alembic downgrade -1   # убрали last_login_at
alembic downgrade -1   # убрали bio
alembic downgrade -1   # удалили таблицу tags
alembic upgrade head   # всё вернули
```

---