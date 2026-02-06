import asyncio
import json
import logging
import os
import sys

import psycopg2
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from client import Client
from data import set_data
from models import Base, Video
from query import json_to_sql

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()

PGPASSWORD = os.getenv("PGPASSWORD")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")

conn = psycopg2.connect(
    host=PGHOST,
    database=PGDATABASE,
    user=PGUSER,
    password=PGPASSWORD,
    port=PGPORT
)

cur = conn.cursor()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


@dp.message()
async def echo_handler(message: Message):
    try:
        answer = await client.send_message(message.text)
        result_json = json.loads(answer)
        sql, params = await json_to_sql(result_json)
        cur.execute(sql, params)
        await message.answer(str(cur.fetchone()[0]))
    except Exception as e:
        await message.answer(str(e))


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        count = session.execute(select(Video).limit(1)).scalar()
        if count is None:
            set_data()
    client = Client()
    asyncio.run(main())
