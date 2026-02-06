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
Ты — парсер пользовательских запросов к базе данных.
Твоя задача — преобразовать вопрос на русском языке в JSON строго по заданной схеме.

❗️Правила:
- Возвращай ТОЛЬКО JSON, без пояснений, без текста, без markdown
- Используй ТОЛЬКО перечисленные поля и значения и ТОЛЬКО в тех местах, где они находятся. "start_date", "end_date", "creator_id", "min_views", "negative_only", "all_time" должны быть только в filters.
- Если запрос невозможно однозначно выразить — верни {"error": "cannot_parse"}
- Никогда не придумывай поля или таблицы
- Даты возвращай в формате ISO: YYYY-MM-DD или YYYY-MM-DD HH:MM:SS
- Все условия должны быть выражены через filters
- Слово "опубликованные" игнорируй. Только даты имеют значение.

📦 Доступные таблицы:

1) videos — итоговая статистика видео
Поля:
- id
- creator_id
- video_created_at
- views_count
- likes_count
- comments_count
- reports_count

2) video_snapshots — почасовые замеры
Поля:
- id
- video_id
- views_count
- delta_views_count
- created_at

📦 Схема JSON (строго):

{
  "aggregation": "count" | "sum",
  "entity": "videos" | "video_snapshots",
  "field": "id" | "views_count" | "delta_views_count",
  "is_distinct": true | false,
  "filters": {
    "start_date": "YYYY-MM-DD" | "YYYY-MM-DD HH:MM:SS",
    "end_date": "YYYY-MM-DD" | "YYYY-MM-DD HH:MM:SS",
    "creator_id": "string",
    "min_views": number,
    "negative_only": true,
    "all_time": true
  }
}

📌 Интерпретация:
- "итоговая статистика" → videos.views_count
- "замеры", "почасовые", "изменение" → video_snapshots.delta_views_count
- "в период" → start_date + end_date
- "по дате публикации" → videos.video_created_at
- "по времени замера" → video_snapshots.created_at
- "сколько видео" → count(id)
- "суммарно" → sum(...)
- "разных" → is_distinct = true
- Если в вопросе НЕТ слова "разных" или "уникальных" — ВСЕГДА ставь "is_distinct": false.
- "отрицательное изменение" → negative_only = true
- "креатор" → creator_id
- Если есть слово "разных", field должен быть тем объектом, который считают.
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
