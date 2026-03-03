# Практика 05 — Диагностика: пустые/шумные миграции, default vs server_default

## Цель

Понять, почему autogenerate иногда генерирует «пустые» или «шумные» миграции,
научиться различать `default` и `server_default` и настроить
`compare_server_default`.

---

## Задание 9. default vs server_default

### Ключевое отличие

```python
# default — Python-side. Alembic НЕ видит это.
is_active: Mapped[bool] = mapped_column(Boolean, default=True)

# server_default — SQL-side. Alembic ВИДИТ это.
is_active: Mapped[bool] = mapped_column(Boolean, server_default=sa.text("true"))
```


### Что запомнить

- Для Alembic используй `server_default`, если хочешь, чтобы DEFAULT попал в DML
- `default` — это только для ORM, в БД его не видно
- Можно использовать **оба**: `default` для Python-кода, `server_default` для SQL

---

