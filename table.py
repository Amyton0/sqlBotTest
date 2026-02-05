import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from models.base import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

print(f"Модели в Base.metadata: {list(Base.metadata.tables.keys())}")

Base.metadata.create_all(engine)
