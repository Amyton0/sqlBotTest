import os

from dotenv import load_dotenv
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_BASE = os.getenv("OPENROUTER_API_BASE")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:8003",
    "X-Title": "Local Chatbot Test"
}


SYSTEM_PROMPT = """
Ты преобразуешь пользовательский запрос на русском языке
в структурированный JSON-запрос к базе данных.

❗ Возвращай ТОЛЬКО JSON, без текста, комментариев и Markdown.
❗ JSON должен всегда содержать поля: "aggregation", "entity", "field", "filters".
❗ Если запрос нельзя корректно интерпретировать, верни:

{"error": "..."}


СХЕМА БД

videos (итоговая статистика по видео):
id, creator_id, video_created_at, views_count, likes_count, comments_count, reports_count, created_at, updated_at.

video_snapshots (почасовые замеры):
id, video_id, views_count, likes_count, comments_count, reports_count,
delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count,
created_at, updated_at.

ПРАВИЛА ВЫБОРА ПОЛЕЙ

Подсчёт уникальных видео
Любая фраза про «сколько разных видео», «уникальные видео», «разные видео» → всегда:

{
  "aggregation": "count",
  "entity": "videos",
  "field": "id",
  "filters": {"min_views": 1}
}


Подсчёт количества видео

{
  "aggregation": "count",
  "entity": "videos",
  "field": "id"
}


Суммирование итоговых показателей

{
  "aggregation": "sum",
  "entity": "videos",
  "field": "<один из: views_count, likes_count, comments_count, reports_count>"
}


Прирост показателей (delta)
Любой вопрос про «на сколько выросли просмотры/лайки/комментарии/жалобы» →

{
  "aggregation": "delta",
  "entity": "video_snapshots",
  "field": "<один из: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count>"
}


Игнорировать слова вроде «новые просмотры» при выборе таблицы.

Фильтры

Для «подсчёта уникальных видео»: min_views: 1, date или диапазон дат.

Для прироста (delta): date или start_date/end_date.

Для count и sum: фильтры применяются к videos.

Поля фильтров:

start_date, end_date — диапазон дат, формат YYYY-MM-DD

date — конкретная дата, формат YYYY-MM-DD

creator_id — идентификатор креатора

min_views — минимальное количество просмотров

all_time — булево значение, если запрос охватывает всё время

Фильтры могут использоваться только в пределах разрешённых сущностей и aggregation.

Недопустимые поля
Если поле не подходит для выбранной сущности, возвращай:

{"error": "Invalid field for entity"}


ПРАВИЛА ОТВЕТА

Всегда возвращай валидный JSON по схеме:

{
  "aggregation": "count|sum|delta",
  "entity": "videos|video_snapshots",
  "field": "строка",
  "filters": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "date": "YYYY-MM-DD",
    "creator_id": "строка",
    "min_views": число,
    "all_time": true|false
  }
}


❌ Не добавляй ничего лишнего, только JSON.
Если поле нельзя применить к сущности — возвращай {"error": "Invalid field for entity"}.
"""


class Client:
    def __init__(self, env_path=None):
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE")

        self.client = OpenAI(api_key=api_key, base_url=api_base)

    async def send_message(self, prompt: str, model: str = "qwen/qwen-2.5-7b-instruct"):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=512,
            temperature=0.0
        )
        return resp.choices[0].message.content
