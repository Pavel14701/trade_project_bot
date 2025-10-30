"""
Provides a factory function for creating a configured instance of `RabbitBroker` using application-level settings.

This module integrates FastStream's RabbitMQ broker with SASL/PLAIN authentication, based on values
defined in the `RabbitMQConfig` dataclass. It is typically used to initialize messaging infrastructure
for publishing and subscribing to queues in a microservice architecture.
"""

from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext

from api_okx_v1.src.config import RabbitMQConfig


def new_broker(rabbitmq_config: RabbitMQConfig) -> RabbitBroker:
    """
    Creates and returns a configured RabbitMQ broker instance using FastStream.

    This function sets up the broker with host, port, virtual host, and SASL/PLAIN authentication
based on the provided configuration object. It is intended to be used during application startup
to initialize message routing.

    Args:
        rabbitmq_config (RabbitMQConfig): Configuration object containing RabbitMQ connection details.

    Returns:
        RabbitBroker: A fully configured instance of FastStream's RabbitMQ broker.
    """
    return RabbitBroker(
        host=rabbitmq_config.host,
        port=rabbitmq_config.port,
        security=SASLPlaintext(
            username=rabbitmq_config.login,
            password=rabbitmq_config.password,
        ),
        virtualhost=rabbitmq_config.vhost,
    )