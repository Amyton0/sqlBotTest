# SQL Telegram Bot

Простой Telegram-бот, который преобразует текстовые запросы на русском языке в SQL-запросы и возвращает результаты из базы данных PostgreSQL.

---

## Что делает проект

- Принимает пользовательские вопросы о видео (например, просмотры, лайки, комментарии).
- Преобразует их в структурированный JSON-запрос.
- Генерирует SQL и получает данные из PostgreSQL.
- Поддерживает подсчёт уникальных видео, суммирование и прирост показателей (delta).
- Используется LLM (Qwen) для интерпретации текстовых вопросов и построения валидного JSON по строгой схеме.

---

## Архитектура

1. **Telegram Bot** (aiogram) — принимает сообщения и отправляет ответы.  
2. **SQL Parser** — преобразует JSON от LLM в SQLAlchemy-запрос.  
3. **PostgreSQL** — хранит таблицы `videos` и `video_snapshots`.  
4. **LLM (ChatGPT)** — на основе промпта преобразует естественный язык в строго валидный JSON.  
5. **JSON → SQL** — с помощью Python и SQLAlchemy строится SQL-запрос и выполняется в БД.

**Подход к JSON и SQL**:  

- Для подсчёта уникальных видео всегда `aggregation=count`, `entity=videos`, `field=id`.
- Для прироста показателей — `aggregation=delta`, `entity=video_snapshots`, `field=delta_*`.
- Фильтры применяются только к допустимым сущностям.
- Любое несоответствие → JSON с `{"error": "Invalid field for entity"}`.

**LLM и промпт**:

- Схема данных описана прямо в промпте: таблицы, поля, правила выбора полей и фильтров.  
- Промпт строго диктует: какие поля использовать для count, sum, delta, какие фильтры разрешены, как обрабатывать уникальные видео.  
- LLM возвращает только валидный JSON без текста и комментариев, который затем конвертируется в SQL.

Промпт:
```
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
```

---

## Установка и запуск локально

1. Склонировать репозиторий:

```bash
git clone <repo_url>
cd <repo_name>
```

2. Создать .env с переменными:
```
OPENROUTER_API_KEY=<ключ для OpenRouter>
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
DATABASE_URL=postgresql://user:password@db:5432/dbname
BOT_TOKEN=<ваш_токен_бота>
PGDATABASE=...
PGUSER=...
PGPASSWORD=...
PGHOST=...
PGPORT=...
```
Токен бота можно получить, создав бота в боте BotFather в телеграме.

3. Запустить контейнеры:
```
docker-compose up --build
```

4. Бот будет доступен в Telegram.


## Использование

- Отправляете вопрос боту в Telegram на русском языке, например:  
  *«Сколько видео набрало больше 100 000 просмотров?»*  
- Бот возвращает число на основе данных из базы.
