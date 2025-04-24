Установка pandas_ta с ветки deveploment с github
```pip install -U git+https://github.com/twopirllc/pandas-ta.git@development```
Переписать индикаторы и стратегию  не забыть про выгрузку сигналов в кэш


trade_project_bot/
│── src/                # Основной код проекта
│   ├── app/            # Бизнес-логика приложения
│   │   ├── models/     # SQLAlchemy модели
│   │   ├── schemas/    # Pydantic модели
│   │   ├── services/   # Сервисы (логика работы, API)
│   │   ├── routers/    # FastAPI маршруты (эндпоинты)
│   │   └── dependencies.py  # Зависимости для FastAPI
│   ├── database/       # Работа с базой данных
│   │   ├── migrations/ # Миграции Alembic
│   │   ├── session.py  # Подключение к базе данных
│   │   ├── crud.py     # Операции с БД (CRUD)
│   ├── utils/          # Вспомогательные функции
│   ├── security/       # Авторизация и хеширование
│   ├── websocket/      # Логика работы с WebSocket
│   ├── tests/          # Тесты
│   ├── config.py       # Конфигурация приложения
│   └── main.py         # Точка входа (FastAPI, Gunicorn, etc.)
│── .env                # Переменные окружения
│── requirements.txt    # Зависимости проекта
│── alembic.ini         # Конфигурация миграций
│── README.md           # Описание проекта
