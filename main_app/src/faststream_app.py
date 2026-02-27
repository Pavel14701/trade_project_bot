from dishka import AsyncContainer # type: ignore
from dishka.integrations import faststream as faststream_integration # type: ignore
from faststream import FastStream # type: ignore
from faststream.rabbit import RabbitBroker # type: ignore

from controllers.amqp import controller


def create_faststream_app(
    container: AsyncContainer, 
    broker: RabbitBroker
) -> FastStream:
    faststream_app = FastStream(broker)
    faststream_integration.setup_dishka(  # type: ignore
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app