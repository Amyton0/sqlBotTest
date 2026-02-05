import asyncio
import json
import logging
import os
import sys

import psycopg2
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dotenv import load_dotenv
from sqlalchemy import create_engine

from client import Client
from data import set_data
from models import Base
from query import json_to_sql

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host="db",
    database="sqlbot",
    user="postgres",
    password=POSTGRES_PASSWORD,
    port=5432
)

cur = conn.cursor()

engine = create_engine(f'postgresql://postgres:{POSTGRES_PASSWORD}@db/sqlbot')


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message):
    answer = await client.send_message(message.text)
    result_json = json.loads(answer)
    sql, params = await json_to_sql(result_json)
    cur.execute(sql, params)
    await message.answer(str(cur.fetchone()[0]))


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    Base.metadata.create_all(engine)
    set_data()
    client = Client()
    asyncio.run(main())
