# Практика: подключение Alembic к проекту "Users + Projects + Roles"


## Шаг 1. Установи зависимости

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


---

## Шаг 2. Инициализируй Alembic

```bash
alembic init alembic
```

Появится папка `alembic/` и файл `alembic.ini`.

---

## Шаг 3. Настрой alembic.ini

Найди строку и замени её:

```ini
# было:
sqlalchemy.url = driver://user:pass@localhost/dbname

# стало:
sqlalchemy.url = sqlite:///./dev.db
```

---

## Шаг 4. Настрой alembic/env.py

Открой `alembic/env.py`.

**4a.** В самом начале файла, после стандартных импортов, добавь:

```python
# подключаем наши модели для autogenerate
from app.models import Base
import app.models  # noqa: F401 — нужен, чтобы все модели зарегистрировались в Base.metadata
```

**4b.** Найди строку:

```python
target_metadata = None
```

Замени на:

```python
target_metadata = Base.metadata
```

---

## Шаг 5. Создай первую миграцию (autogenerate)

```bash
alembic revision --autogenerate -m "initial: users, projects, roles"
```

Alembic проанализирует `Base.metadata` и создаст файл в `alembic/versions/`.  
Открой его и проверь: в `upgrade()` должны быть `op.create_table(...)` для всех 4 таблиц,  
в `downgrade()` — `op.drop_table(...)`.

---

## Шаг 6. Примени миграцию (upgrade)

```bash
alembic upgrade head
```

Alembic создаст `dev.db` и выполнит все миграции до последней (`head`).

Проверь, что таблицы появились:

```bash

## Шаг 7. Откати миграцию (downgrade)

```bash
alembic downgrade base
```

`base` — это состояние до первой миграции (пустая БД).  
Проверь снова: останется только `['alembic_version']`.

Верни обратно:

```bash
alembic upgrade head
```


---

## Шаг 8. Полезные команды Alembic

```bash
alembic current            # текущая версия БД
alembic history --verbose  # история всех миграций
alembic heads              # последние (непримёрненные) версии

# откат на одну миграцию назад:
alembic downgrade -1

# применить одну следующую миграцию:
alembic upgrade +1
```

---

## Шаг 9 (бонус). Добавь новую колонку — вторая миграция

Добавь в `app/models.py` в класс `User` поле:

```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

Не забудь импорт: `from sqlalchemy import Boolean`

Затем:

```bash
alembic revision --autogenerate -m "add users.is_active"
alembic upgrade head
```

Посмотри на сгенерированный файл — он должен содержать `op.add_column(...)`.

---