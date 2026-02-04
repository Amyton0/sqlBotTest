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

Схема БД:

Таблица videos (итоговая статистика по ролику)
- id — идентификатор видео;
- creator_id — идентификатор креатора;
- video_created_at — дата и время публикации видео;
- views_count — финальное количество просмотров;
- likes_count — финальное количество лайков;
- comments_count — финальное количество комментариев;
- reports_count — финальное количество жалоб;
- служебные поля created_at, updated_at.


Таблица video_snapshots (почасовые замеры по ролику)
Каждый снапшот относится к одному видео и содержит:
- id — идентификатор снапшота;
- video_id — ссылка на соответствующее видео;
- текущие значения: views_count, likes_count, comments_count, reports_count на момент замера;
- приращения: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — насколько изменилось значение с прошлого замера;
- created_at — время замера (раз в час);
- updated_at — служебное поле.

Правила:
- Используй только указанные таблицы и поля
- Не придумывай новых сущностей
- Верни ТОЛЬКО JSON
- Если запрос нельзя интерпретировать — верни error

Верни ТОЛЬКО валидный JSON.
Не добавляй пояснений, текста, markdown или комментариев. Ответ ДОЛЖЕН соответствовать данной JSON Schema.

Схема JSON: 
{
  "title": "Video Aggregation Query",
  "type": "object",
  "required": ["aggregation", "entity", "filters"],
  "properties": {
    "aggregation": {
      "type": "string",
      "enum": ["count", "sum", "delta"],
      "description": "Тип агрегации: count - количество, sum - сумма, delta - прирост"
    },
    "entity": {
      "type": "string",
      "enum": ["videos"],
      "description": "Объект данных, с которым работаем"
    },
    "filters": {
      "type": "object",
      "properties": {
        "start_date": {
          "type": "string",
          "format": "date",
          "description": "Дата начала периода (включительно)"
        },
        "end_date": {
          "type": "string",
          "format": "date",
          "description": "Дата конца периода (включительно)"
        },
        "creator_id": {
          "type": "string",
          "description": "ID креатора"
        },
        "min_views": {
          "type": "integer",
          "description": "Минимальное количество просмотров"
        },
        "views_delta_min": {
          "type": "integer",
          "description": "Минимальный прирост просмотров за день"
        },
        "date": {
          "type": "string",
          "format": "date",
          "description": "Конкретная дата для запроса"
        },
        "all_time": {
          "type": "boolean",
          "description": "Если true, учитывать все время"
        }
      },
      "additionalProperties": false
    }
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

