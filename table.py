import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from models.base import Base

load_dotenv()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

engine = create_engine(f'postgresql://postgres:{POSTGRES_PASSWORD}@db/sqlbot')

print(f"Модели в Base.metadata: {list(Base.metadata.tables.keys())}")

Base.metadata.create_all(engine)
