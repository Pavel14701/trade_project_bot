"""
Initializes and runs the FastStream application with RabbitMQ integration and 
dependency injection.

This module sets up the messaging infrastructure using FastStream and RabbitBroker, 
configures dependency injection via Dishka, and includes the AMQP controller 
for handling message routes.

Key Responsibilities:
- Load configuration from environment variables.
- Create and configure RabbitMQ broker with authentication.
- Set up Dishka container for dependency injection.
- Register message routes via FastStream's router.
- Launch the application using Uvicorn.
"""


from dishka import make_async_container # type: ignore
from dishka.integrations.faststream import setup_dishka  # type: ignore
from faststream import FastStream # type: ignore
from faststream.rabbit import RabbitBroker # type: ignore

from config import Config
from controllers.amqp import controller
from infrastructure.broker import new_broker
from ioc import OkxApiProvider as AppProvider

config = Config()


def get_faststream_app(config: Config) -> FastStream:
    """
    Creates and configures a FastStream application instance.

    This function:
    - Initializes a RabbitMQ broker using the provided configuration.
    - Creates a Dishka dependency injection container with application-level providers.
    - Sets up auto-injection for FastStream using Dishka.
    - Registers the AMQP controller with the broker.

    Args:
        config (Config): Aggregated configuration object containing RabbitMQ and app 
        settings.

    Returns:
        FastStream: A fully configured FastStream application instance.
    """
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
    import asyncio
    app = get_faststream_app(config)
    asyncio.run(app.run())