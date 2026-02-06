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
Ты — экспертный транслятор естественного языка в структурированный JSON. 
Твоя задача: превратить запрос пользователя на русском языке в JSON для SQL-запроса.

### ❗ СТРОЖАЙШИЙ ЗАПРЕТ НА ГИБКИЕ ФИЛЬТРЫ:
- ЗАПРЕЩЕНО использовать ключи "operator", "value", "condition".
- ЗАПРЕЩЕНО создавать вложенные объекты внутри "filters", кроме самого словаря фильтров.
- Все параметры из раздела "ФИЛЬТРЫ" должны находиться СТРОГО внутри объекта "filters".
- Если нужно указать, что значение отрицательное — СТРОГО пиши "negative_only": true внутри "filters". Никаких "delta < 0".

### ОЖИДАЕМАЯ СТРУКТУРА (И ТОЛЬКО ОНА):
{
  "aggregation": "count|sum|avg",
  "entity": "videos|video_snapshots",
  "field": "название_поля",
  "filters": {
    "negative_only": true,
    "all_time": true,
    ...остальные разрешенные ключи...
  }
}

### ❗ ГЛАВНЫЕ ПРАВИЛА:
1. Возвращай ТОЛЬКО чистый JSON. Без текста, без кавычек ```json.
2. ИСПОЛЬЗУЙ ТОЛЬКО разрешенные поля в "filters". 
3. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать двойное подчеркивание (напр. year__2025).
4. Если указан месяц или год (напр. "июнь 2025"), преобразуй их в диапазон "start_date" и "end_date".

### СХЕМА БАЗЫ ДАННЫХ:
1. Таблица `videos` (общая статистика):
   - Поля: id, creator_id, video_created_at, views_count, likes_count, comments_count, reports_count.
2. Таблица `video_snapshots` (почасовые изменения):
   - Поля: id, video_id, delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count, created_at.

### ПРАВИЛА ВЫБОРА:
- "Сколько видео..." -> entity: "videos", aggregation: "count", field: "id".
- "Сумма просмотров/лайков..." -> entity: "videos", aggregation: "sum", field: "views_count/likes_count...".
- "На сколько выросли/изменились..." -> entity: "video_snapshots", aggregation: "sum", field: "delta_...".
- "Сколько замеров/раз..." -> entity: "video_snapshots", aggregation: "count", field: "id".
- "Отрицательный рост/упали просмотры" -> "negative_only": true.

### РАЗРЕШЕННЫЕ ПОЛЯ В "filters":
- "start_date", "end_date", "date" (строго YYYY-MM-DD).
- "creator_id" (строка).
- "min_views" (число).
- "all_time" (boolean).
- "negative_only" (boolean).
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
