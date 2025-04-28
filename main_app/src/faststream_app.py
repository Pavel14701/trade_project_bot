from dishka import AsyncContainer
from dishka.integrations import faststream as faststream_integration
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from main_app.src.controllers.amqp import controller


def create_faststream_app(
    container: AsyncContainer, 
    broker: RabbitBroker
) -> FastStream:
    faststream_app = FastStream(broker)
    faststream_integration.setup_dishka(
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app