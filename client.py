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
Ты — транслятор запросов. Твоя задача: перевести вопрос пользователя на русском языке в JSON-схему для базы данных.

❗ ОТВЕТ ТОЛЬКО В JSON. Без пояснений, без ```json.
❗ Если запрос невыполним, верни {"error": "причина"}.

### СХЕМА ДАННЫХ
1. videos (статистика видео):
   - поля: id, creator_id, video_created_at, views_count, likes_count, comments_count, reports_count.
2. video_snapshots (почасовые изменения):
   - поля: id, video_id, delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count, created_at.

### ПРАВИЛА
- aggregation: count, sum, avg, max.
- entity: videos или video_snapshots.
- filters:
    - start_date / end_date: для диапазонов (YYYY-MM-DD).
    - date: для конкретного дня.
    - creator_id: строка.
    - min_views: число.
    - negative_only: true (если речь о падении/отрицательных значениях).
    - all_time: true (если указано "за всё время").
❗ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать диапазоны через "/" в поле "date".
❗ Если в запросе указан период (с... по..., между...), ВСЕГДА используй "start_date" и "end_date".
❗ Поле "date" используется ТОЛЬКО для одного конкретного дня.
❗ "Сколько замеров/записей..." или "Как часто было отрицательное значение..." 
   → entity: "video_snapshots", aggregation: "count", field: "id"
❗ "На сколько выросли/упали показатели в сумме..." 
   → entity: "video_snapshots", aggregation: "sum", field: "delta_*"

### ЛОГИКА ВЫБОРА
- "Сколько видео..." → entity: videos, aggregation: count, field: id.
- "Сумма/Всего просмотров" (итоговых) → entity: videos, aggregation: sum, field: views_count.
- "На сколько выросли/изменились..." → entity: video_snapshots, aggregation: sum, field: delta_*.
- "Количество замеров/записей в истории" → entity: video_snapshots, aggregation: count.

### ПРИМЕРЫ
Запрос: "Сколько видео у креатора 123 за 4 февраля 2026?"
Ответ: {
  "aggregation": "count",
  "entity": "videos",
  "field": "id",
  "filters": { "creator_id": "123", "date": "2026-02-04" }
}

Запрос: "На сколько просмотров выросли видео с 1 по 3 января?"
Ответ: {
  "aggregation": "sum",
  "entity": "video_snapshots",
  "field": "delta_views_count",
  "filters": { "start_date": "2026-01-01", "end_date": "2026-01-03" }
}
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
