from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka  # type: ignore
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from api_okx_v1.src.config import Config
from api_okx_v1.src.controllers.amqp import controller
from api_okx_v1.src.infrastructure.broker import new_broker
from api_okx_v1.src.ioc import OkxApiProvider as AppProvider

config = Config()

def get_faststream_app(config: Config) -> FastStream:
    broker = new_broker(config.rabbit)
    container = make_async_container(
        AppProvider(),
        context={
            Config: config, 
            RabbitBroker: broker
        }
    )
    faststream_app = FastStream(broker)
    setup_dishka(
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app


if __name__ == "__main__":
    import uvicorn
    app = get_faststream_app(config)
    uvicorn.run(
        app=config.app.name, 
        host=config.app.host, 
        port=config.app.port, 
        reload=config.app.reloading
    )