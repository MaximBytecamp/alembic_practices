from app.database import SessionLocal, engine
from app.models import Base, User

Base.metadata.create_all(engine)

with SessionLocal() as session:
    if not session.query(User).count():
        session.add_all([
            User(email="alice@example.com"),
            User(email="bob@example.com"),
            User(email="charlie@example.com"),
        ])
        session.commit()
        print("Seed: добавлено 3 пользователя")
    else:
        print("Данные уже есть, seed пропущен")
