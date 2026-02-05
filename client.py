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
Ты преобразуешь пользовательский запрос на русском языке в структурированный JSON-запрос к базе данных.

❗ Возвращай только JSON, без текста, комментариев и Markdown.
❗ JSON всегда должен содержать поля: "aggregation", "entity", "field", "filters".
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

Подсчёт количества видео:

{
  "aggregation": "count",
  "entity": "videos",
  "field": "id"
}


Суммирование итоговых показателей:

{
  "aggregation": "sum",
  "entity": "videos",
  "field": "<один из: views_count, likes_count, comments_count, reports_count>"
}


Прирост (delta):

{
  "aggregation": "delta",
  "entity": "video_snapshots",
  "field": "<один из: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count>"
}


Подсчёт уникальных видео:
Любая фраза про «сколько разных видео», «уникальные видео», «разные видео» → всегда:

{
  "aggregation": "count",
  "entity": "videos",
  "field": "id"
}


Прирост показателей:
Любой вопрос про «на сколько выросли просмотры/лайки/комментарии/жалобы» → использовать video_snapshots и соответствующее поле delta_*.
Если нужно посчитать только отрицательные приросты (например, когда просмотры уменьшились), добавляй фильтр:

"negative_only": true

ФИЛЬТРЫ

Для диапазонов дат — start_date и end_date (YYYY-MM-DD) на верхнем уровне.

Для одной даты — date (YYYY-MM-DD).

creator_id — идентификатор креатора.

min_views — минимальное количество просмотров (для уникальных видео: min_views: 1).

all_time — булево, если запрос охватывает всё время.

negative_only — булево, если нужно учитывать только отрицательные delta.

Важно: фильтры применяются только в пределах разрешённых сущностей и aggregation.
delta_* → только к video_snapshots.
count и sum → только к videos.

ПРАВИЛА ОТВЕТА

Всегда возвращай JSON строго по схеме:

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
    "all_time": true|false,
    "negative_only": true|false
  }
}

all_time и negative_only — управляющие флаги, не SQL-фильтры.
Они не должны использоваться как условия вида field = value.
Если пользователь не сказал «за всё время» — НЕ добавляй all_time вообще

Любое поле, которое не применимо к выбранной сущности →

{"error": "Invalid field for entity"}


Диапазоны дат никогда не вкладываются в video_created_at или другие поля — всегда верхний уровень start_date и end_date.

Не добавляй ничего лишнего, только JSON.
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
