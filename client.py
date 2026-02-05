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

❗ Возвращай ТОЛЬКО JSON, без комментариев и текста.
❗ JSON должен содержать всегда поля: "aggregation", "entity", "field", "filters".
❗ Если запрос нельзя корректно интерпретировать, верни {"error": "..."}.

СХЕМА БД

videos: id, creator_id, video_created_at, views_count, likes_count, comments_count, reports_count, created_at, updated_at.

video_snapshots: id, video_id, views_count, likes_count, comments_count, reports_count, delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count, created_at, updated_at.

ПРАВИЛА ВЫБОРА

Если запрос про количество видео, то:

{
  "aggregation": "count",
  "entity": "videos",
  "field": "id"
}


Если запрос про сумму итоговых показателей, то:

{
  "aggregation": "sum",
  "entity": "videos",
  "field": "<один из: views_count, likes_count, comments_count, reports_count>"
}


Если запрос про прирост (delta), то:

{
  "aggregation": "delta",
  "entity": "video_snapshots",
  "field": "<один из: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count>"
}


❌ Любое поле не из этого списка для сущности — ошибка:

{"error": "Invalid field for entity"}

JSON СХЕМА
{
  "type": "object",
  "required": ["aggregation", "entity", "field", "filters"],
  "properties": {
    "aggregation": {"type": "string", "enum": ["count", "sum", "delta"]},
    "entity": {"type": "string", "enum": ["videos", "video_snapshots"]},
    "field": {"type": "string"},
    "filters": {
      "type": "object",
      "properties": {
        "start_date": {"type": "string", "format": "date"},
        "end_date": {"type": "string", "format": "date"},
        "creator_id": {"type": "string"},
        "min_views": {"type": "integer"},
        "date": {"type": "string", "format": "date"},
        "all_time": {"type": "boolean"}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}


✅ Возвращай только JSON, строго по правилам таблицы и схемы.
Если поле "field" нельзя применить к сущности — возвращай {"error": "Invalid field for entity"}.
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
