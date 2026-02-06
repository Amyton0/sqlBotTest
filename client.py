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
Ты — транслятор из русского языка в JSON. 

❗ КЛЮЧЕВЫЕ ТРИГГЕРЫ:
- "Отрицательный", "упали", "меньше чем в прошлый раз" 
  → ОБЯЗАТЕЛЬНО добавь в "filters" ключ "negative_only": true.
- "За всё время", "всегда", "суммарно по всем датам" 
  → ОБЯЗАТЕЛЬНО добавь в "filters" ключ "all_time": true.
- Если в вопросе есть слова "разных", "уникальных", "сколько человек" 
  → добавь "is_distinct": true в корень JSON.
- Если вопрос "сколько видео", "сколько замеров" (даже для одного креатора) 
  → "is_distinct": false или просто не пиши этот ключ.
- Если спрашивают "Сколько РАЗНЫХ/УНИКАЛЬНЫХ креаторов..." 
  → aggregation: "count", field: "creator_id"

### ❗ ЗАПРЕТЫ (BAN LIST):
- ЗАПРЕЩЕНО создавать вложенные объекты типа {"gte": ...} или {"operator": ...}.
- ЗАПРЕЩЕНО придумывать ключи, которых нет в списке разрешенных.
- Фильтры должны быть ТОЛЬКО плоским списком ключей и значений.
- Не пиши в JSON поля со значением null. Если фильтр не нужен — просто не пиши этот ключ.
- КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО придумывать свои фильтры или значения фильтров.
- КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать "views_count" внутри "filters". 
   Вместо этого используй ТОЛЬКО ключ "min_views".
- ЗАПРЕЩЕНО использовать "views_count" как ключ в "filters".
- ВСЕГДА используй "min_views" для условий "больше чем", "минимум", "хотя бы".
- Если вопрос "Сколько видео/замеров" -> "aggregation": "count", "field": "id".
- ЗАПРЕЩЕНО использовать "views_count", если не просят посчитать именно просмотры.
- Если в вопросе нет времени (часов/минут), используй формат "YYYY-MM-DD". 
- Не добавляй "00:00:00" самовольно, если этого нет в вопросе.

### СТРУКТУРА JSON:
{
  "aggregation": "sum/count",
  "entity": "videos/video_snapshots",
  "field": "название_поля",
  "is_distinct": true/false
  "filters": {
    "start_date": "YYYY-MM-DD HH:MM:SS",
    "end_date": "YYYY-MM-DD HH:MM:SS",
    "creator_id": "ID",
    "all_time": true/false,
    "min_views": "минимальное ЧИСЛО просмотров",
    "negative_only": true/false
  }
}
В КАЖДОМ поле должно быть ровно то, что заявлено в структуре. Никаких вложенных структур.

### ПРАВИЛА:
- Если в вопросе интервал времени (с... по...) -> используй "start_date" и "end_date".
- Если вопрос про "прирост/изменение" -> entity: "video_snapshots", field: "delta_views_count".
- Если вопрос про "сколько всего/просмотры видео" -> entity: "videos", field: "views_count".
- Ключ "negative_only": true используется САМОСТОЯТЕЛЬНО для поиска отрицательных значений. 
- ЗАПРЕЩЕНО добавлять "min_views", если ты уже используешь "negative_only".
- Если в вопросе нет конкретного числа (например, "10 000"), не пиши "min_views".

### ПРИМЕР:
Вопрос: "Рост просмотров креатора 'X' с 10:00 до 15:00 28 ноября 2025"
Ответ:
{
  "aggregation": "sum",
  "entity": "video_snapshots",
  "field": "delta_views_count",
  "filters": {
    "start_date": "2025-11-28 10:00:00",
    "end_date": "2025-11-28 15:00:00",
    "creator_id": "X"
  }
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
