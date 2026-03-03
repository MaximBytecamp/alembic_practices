# Практика 06 — Advanced: downgrade-контракт, воспроизводимость, merge, offline SQL

## Цель

Научиться проверять корректность `downgrade`, воспроизводить схему с нуля,
работать с двумя «головами» (merge миграций) и генерировать SQL в offline-режиме.

---

## Бонус 1. Merge-миграции (две головы)

### Сценарий

Два разработчика одновременно создали миграцию от одной и той же head.
Получилось **две головы** — Alembic не может определить, какая «главная».

### Шаг 1. Создай две параллельные миграции вручную

```bash
# Миграция от «разработчика 1»:
alembic revision -m "dev1: add users.avatar_url"

# Миграция от «разработчика 2» (с тем же down_revision!):
alembic revision -m "dev2: add projects.is_archived"
```

> Обе миграции будут иметь один и тот же `down_revision` = текущий head.
> Но у `dev2` down_revision будет указывать на `dev1`.
> Чтобы сымитировать реальный конфликт, нужно отредактировать `dev2`:

Открой файл `dev2: add projects.is_archived` и **измени** `down_revision`:

```python
# было (указывает на dev1):
down_revision = '<rev_dev1>'

# стало (указывает на тот же head, что и dev1):
down_revision = '<rev_до_dev1>'  # скопируй down_revision из dev1
```

### Шаг 2. Увидь проблему

```bash
alembic heads
```

Ты увидишь **2 head'а**.

```bash
alembic upgrade head
# ❌ ERROR: Multiple heads are present
```

### Шаг 3. Создай merge-миграцию

```bash
alembic merge -m "merge dev1 and dev2" heads
```

Alembic создаст файл, который связывает две ветки в одну:

```python
# В merge-миграции:
down_revision = ('<rev_dev1>', '<rev_dev2>')  # tuple!
```

### Шаг 4. Заполни merge-миграцию кодом

Merge-миграции обычно пусты (просто связка). Но сначала нужно написать код
в миграциях `dev1` и `dev2`:

**dev1:**
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(512), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
```

**dev2:**
```python
def upgrade() -> None:
    op.add_column('projects', sa.Column('is_archived', sa.Boolean(), server_default=sa.text('0'), nullable=False))

def downgrade() -> None:
    op.drop_column('projects', 'is_archived')
```

### Шаг 5. Примени

```bash
alembic upgrade head
alembic heads     # теперь одна голова
alembic current   # = merge
```

### Что запомнить

- Две головы — нормальная ситуация в командной разработке
- `alembic merge heads` — стандартное решение
- Merge-миграция обычно пустая
- Naming convention **не ломает** merge

---

# Бонус 2. Offline-генерация SQL

### Зачем

В больших компаниях DBA не пускают Alembic напрямую к prod-базе.
Вместо этого: сгенерируй SQL → отдай DBA → он выполнит руками.

### Шаг 1. Сгенерируй SQL для всех миграций

```bash
alembic upgrade head --sql > migrations.sql
```

Открой `migrations.sql`. Ты увидишь чистый SQL:

```sql
CREATE TABLE users (
    id INTEGER NOT NULL,
    email VARCHAR(256) NOT NULL,
    ...
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email)
);
...
```

### Шаг 2. Сгенерируй SQL для одной миграции

```bash
alembic upgrade <rev_from>:<rev_to> --sql > single_migration.sql
```

### Шаг 3. Сгенерируй SQL для downgrade

```bash
alembic downgrade <rev_from>:<rev_to> --sql > rollback.sql
```

### Что проверить

- Имена constraints в SQL совпадают с naming convention
- DDL читаем и понятен (DBA сможет прочитать)
- `--sql` не выполняет миграцию — только печатает

---

## Шпаргалка: команды для advanced-сценариев

```bash
# Downgrade-контракт
alembic downgrade -1           # откат на одну
alembic upgrade +1             # одна вперёд
alembic downgrade base         # откат до пустой БД
alembic upgrade head           # всё вперёд

# Воспроизводимость
rm practice.db                 # удалить БД
alembic upgrade head           # создать с нуля
alembic revision --autogenerate -m "check"  # должна быть пустая

# Множественные головы
alembic heads                  # список голов
alembic merge -m "..." heads   # объединить головы

# Offline SQL
alembic upgrade head --sql     # SQL вперёд
alembic downgrade -1 --sql     # SQL откат
```

---