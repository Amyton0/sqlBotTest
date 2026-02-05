from sqlalchemy import create_engine, text

from models.base import Base

engine = create_engine('postgresql://postgres:postgres@localhost/sqlbot', echo=True)

try:
    with engine.connect() as conn:
        print("✅ Подключение успешно")
        result = conn.execute(text("SELECT current_database();"))  # ← text()!
        db_name = result.scalar()
        print(f"Текущая БД: {db_name}")
        result = conn.execute(text("SELECT current_user;"))
        user = result.scalar()
        print(f"Текущий пользователь: {user}")
        result = conn.execute(text("SELECT current_schema();"))
        schema = result.scalar()
        print(f"Текущая схема: {schema}")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")

print(f"Модели в Base.metadata: {list(Base.metadata.tables.keys())}")

Base.metadata.create_all(engine)
