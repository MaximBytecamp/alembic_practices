# Практика 04 — Управление глубиной сравнения схемы

## Цель

Научиться настраивать `compare_type` и `include_object` в `env.py`, чтобы
autogenerate не создавал ложных диффов и не трогал чужие таблицы.

---

## Задание 1. Фильтрация таблиц через include_object

### Проблема

В реальных проектах в БД могут быть таблицы, которых нет в моделях:
- таблицы от legacy-кода
- таблицы от внешних сервисов (Celery, audit, analytics)
- view'ы, materialized views

Без фильтрации Alembic будет **предлагать удалить** эти таблицы.


### Шаг 1. Создай «чужую» таблицу в БД

```bash
python create_audit_table.py
```

Проверь:

```bash
python3 -c "
import sqlite3; conn = sqlite3.connect('practice.db')
tables = [t[0] for t in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
print(tables)
conn.close()
"
```

В списке появится `audit_logs` — таблица, которой нет в моделях.

### Шаг 2. Увидь проблему

```bash
alembic revision --autogenerate -m "test: audit noise"
```

Открой файл — Alembic предложит `op.drop_table('audit_logs')`.  
**Это опасно!** Он хочет удалить чужую таблицу.

Удали файл:

```bash
rm alembic/versions/<rev>_test_audit_noise.py
```

### Шаг 3. Настрой include_object

Открой `alembic/env.py`. Добавь функцию-фильтр перед `run_migrations_online`:

```python
# Таблицы, которые Alembic должен игнорировать
EXCLUDED_TABLES = {"audit_logs"}


def include_object(object, name, type_, reflected, compare_to):
    """
    Фильтр для autogenerate.
    Возвращает False → объект игнорируется.
    """
    if type_ == "table" and name in EXCLUDED_TABLES:
        return False
    return True
```

Теперь подключи фильтр в `context.configure(...)` внутри `run_migrations_online`:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,
    include_object=include_object,   # ← ДОБАВЬ ЭТО
)
```

### Шаг 4. Проверь что шум исчез

```bash
alembic revision --autogenerate -m "test: should be clean"
```

Открой файл — `upgrade()` и `downgrade()` должны быть **пустыми**.
`audit_logs` больше не трогается. Удали пустой файл.

### Шаг 5. Более продвинутый фильтр (бонус)

Можно фильтровать по паттерну (все таблицы с `_logs`):

```python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.endswith("_logs"):
        return False
    return True
```

Или игнорировать только **reflect'нутые** таблицы, которых нет в моделях:

```python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and compare_to is None:
        return False
    return True
```

Последний вариант — самый гибкий: он пропускает любую таблицу, которую Alembic
«увидел» в БД, но не нашёл в моделях. Это предотвращает `drop_table` для всех
чужих таблиц.