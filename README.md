
Main App
```
└── src
    ├── application
    │   ├── dto.py
    │   ├── exceptions.py
    │   ├── __init__.py
    │   ├── interactors.py
    │   └── interfaces.py
    ├── config.py
    ├── controllers
    │   ├── amqp.py
    │   ├── __init__.py
    │   ├── routes.py
    │   └── schemas.py
    ├── domain
    │   └── entities.py
    ├── fastapi_app.py
    ├── faststream_app.py
    ├── infrastructure
    │   ├── factories
    │   │   ├── __init__.py
    │   │   ├── postgres.py
    │   │   ├── rabbit.py
    │   │   └── redis.py
    │   ├── __init__.py
    │   ├── middlewares.py
    │   ├── migrations
    │   │   ├── env.py
    │   │   ├── __init__.py
    │   │   ├── README
    │   │   └── script.py.mako
    │   ├── models.py
    │   ├── repositories
    │   │   ├── cookies.py
    │   │   ├── exc.py
    │   │   ├── __init__.py
    │   │   ├── security.py
    │   │   ├── sessions.py
    │   │   └── user.py
    │   └── types.py
    ├── ioc.py
    └── main.py
```


Account Events
```
└── src
    ├── application
    │   ├── dto.py
    │   ├── __init__.py
    │   ├── interactors.py
    │   └── interfaces.py
    ├── config.py
    ├── controllers
    │   ├── amqp.py
    │   └── __init__.py
    ├── domain
    │   ├── entities.py
    │   └── __init__.py
    ├── infrastructure
    │   ├── broker.py
    │   ├── cache.py
    │   ├── __init__.py
    │   ├── redis_storage.py
    │   ├── security.py
    │   └── websocket.py
    ├── ioc.py
    └── main.py
```