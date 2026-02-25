from app.database import SessionLocal, engine
from app.models import Base, User

Base.metadata.create_all(engine)

with SessionLocal() as session:
    if not session.query(User).count():
        session.add_all([
            User(login="alice@example.com", is_active=True),
            User(login="bob@example.com", is_active=True),
            User(login="charlie@example.com", is_active=True),
        ])
        session.commit()
        print("Seed: добавлено 3 пользователя")
    else:
        print("Данные уже есть, seed пропущен")