## Быстрый старт

```bash
# 1. Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить первую миграцию (создать таблицы)
alembic upgrade head

# 4. Откатить миграцию (удалить таблицы)
alembic downgrade base

# 5. Посмотреть текущую версию
alembic current

# 6. Посмотреть историю миграций
alembic history --verbose
```

## Создание новой миграции (после изменения моделей)

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
