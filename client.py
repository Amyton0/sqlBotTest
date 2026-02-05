import os

from dotenv import load_dotenv
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:8003",
    "X-Title": "Local Chatbot Test"
}


SYSTEM_PROMPT = """
Ты преобразуешь пользовательский запрос на русском языке
в структурированный запрос к базе данных.

Твоя задача — вернуть ТОЛЬКО валидный JSON,
строго соответствующий указанной ниже схеме.

❗ Ответ ВСЕГДА должен содержать ВСЕ обязательные поля.
❗ Если запрос нельзя интерпретировать однозначно — верни {"error": "..."}.

СХЕМА БД

Таблица videos (итоговая статистика по ролику):
- id — идентификатор видео;
- creator_id — идентификатор креатора;
- video_created_at — дата и время публикации видео;
- views_count — финальное количество просмотров;
- likes_count — финальное количество лайков;
- comments_count — финальное количество комментариев;
- reports_count — финальное количество жалоб;
- created_at, updated_at — служебные поля.

Таблица video_snapshots (почасовые замеры):
- id — идентификатор снапшота;
- video_id — ссылка на видео;
- views_count, likes_count, comments_count, reports_count — текущие значения;
- delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — приращения;
- created_at — время замера;
- updated_at — служебное поле.

ПРАВИЛА

1. Используй ТОЛЬКО указанные таблицы и поля
2. НЕ придумывай новые поля или сущности
3. ВСЕГДА возвращай поле "field"
4. ВСЕГДА возвращай поле "aggregation"
5. ВСЕГДА возвращай поле "entity"
6. ВСЕГДА возвращай поле "filters" (даже если он пустой)
7. Не добавляй пояснений, текста, markdown или комментариев

ПРАВИЛА ВЫБОРА ПОЛЕЙ

- Для подсчёта количества видео используй:
  aggregation = "count"
  field = "id"
  entity = "videos"

- Для суммирования итоговых значений используй:
  aggregation = "sum"
  field = один из:
    "views_count"
    "likes_count"
    "comments_count"
    "reports_count"
  entity = "videos"

- Для прироста (delta) используй:
  aggregation = "delta"
  field = один из:
    "delta_views_count"
    "delta_likes_count"
    "delta_comments_count"
    "delta_reports_count"
  entity = "video_snapshots"

JSON СХЕМА

{
  "type": "object",
  "required": ["aggregation", "entity", "field", "filters"],
  "properties": {
    "aggregation": {
      "type": "string",
      "enum": ["count", "sum", "delta"]
    },
    "entity": {
      "type": "string",
      "enum": ["videos", "video_snapshots"]
    },
    "field": {
      "type": "string"
    },
    "filters": {
      "type": "object",
      "properties": {
        "start_date": { "type": "string", "format": "date" },
        "end_date": { "type": "string", "format": "date" },
        "creator_id": { "type": "string" },
        "min_views": { "type": "integer" },
        "date": { "type": "string", "format": "date" },
        "all_time": { "type": "boolean" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}

Верни ТОЛЬКО валидный JSON.
"""


class Client:
    def __init__(self, env_path=None):
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

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
