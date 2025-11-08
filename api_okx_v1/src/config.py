"""
Defines environment-driven configuration models for application setup using Pydantic.

This module provides a base class `EnvModel` that allows automatic loading of 
configuration values from environment variables. Subclasses represent specific 
configuration domains such as application settings, RabbitMQ, Redis, and 
encryption secrets.

Key Features:
- Uses Pydantic for type-safe configuration modeling.
- Automatically loads values from environment variables via `from_env()` class method.
- Supports field aliasing to map environment variable names to Pythonic field names.
- Centralizes configuration access through the `Config` aggregate model.

Typical Usage:
    config = Config()
    print(config.app.host)
    print(config.redis.db)
"""


from os import environ as env
from typing import Type, TypeVar, get_type_hints

from pydantic import BaseModel, Field

ConfigModelType = TypeVar("ConfigModelType", bound="EnvModel")


class EnvModel(BaseModel):
    """
    Base class for environment-driven configuration models.

    Provides a `from_env()` class method that reads environment variables and
    populates the model fields accordingly. Supports type casting and field aliasing.

    Intended to be subclassed by specific configuration domains.
    """
    @classmethod
    def from_env(cls: Type[ConfigModelType]) -> ConfigModelType:
        """
        Load configuration values from environment variables and instantiate the model.

        This method is designed to automatically populate a Pydantic model with values
        sourced from the system's environment variables. It iterates over the model's
        declared fields and attempts to retrieve corresponding values from the 
            environment
        using either the field's alias (if defined) or its name.

        For each field:
        - It checks if the corresponding environment variable exists.
        - If found, it attempts to cast the value to the expected type using type hints.
        - If casting fails, it falls back to using the raw string value.
        - Fields not present in the environment are left 
            unset (and may use defaults if defined).

        This method is particularly useful for loading configuration
        settings (e.g., API keys, database URLs, feature flags) into a 
        strongly typed model without manually parsing
        or validating environment variables.

        Returns:
            An instance of the model populated with values from the environment.

        Example:
            class AppConfig(EnvModel):
                api_key: str = Field(..., alias="API_KEY")
                debug: bool = Field(False, alias="DEBUG")

            config = AppConfig.from_env()
        """
        raw_data = {}
        hints = get_type_hints(cls)
        for field_name, field in cls.model_fields.items():
            env_key = field.alias or field_name
            if env_key in env:
                value = env[env_key]
                target_type = hints.get(field_name, str)
                try:
                    raw_data[field_name] = target_type(value)
                except Exception:
                    raw_data[field_name] = value  # fallback
        return cls(**raw_data)


class SecretConfig(EnvModel):
    """
    Configuration model for application-level encryption secrets.

    Attributes:
        config_secret_key (str): Secret key used for encrypting sensitive 
        configuration data.
    """
    config_secret_key: str = Field(alias="APP_CONFIG_ENCRYPTION_KEY")


class AppConfig(EnvModel):
    pool_size: int = Field(5, alias='OKX_API_MARKET_POOL_SIZE')
    rate_limit: int = Field(20, alias='OKX_API_MARKET_RATE_LIMIT')


class RabbitMQConfig(EnvModel):
    """
    Configuration model for RabbitMQ connection settings.

    Attributes:
        host (str): RabbitMQ server hostname.
        port (int): RabbitMQ server port.
        login (str): Username for RabbitMQ authentication.
        password (str): Password for RabbitMQ authentication.
        vhost (str): Virtual host to connect to within RabbitMQ.
    """
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASSWORD')
    vhost: str = Field(alias='RABBITMQ_VHOST')


class RedisConfig(EnvModel):
    """
    Configuration model for Redis connection settings.

    Attributes:
        host (str): Redis server hostname.
        port (int): Redis server port.
        db (int): Redis database index for account events.
        password (str): Password for Redis authentication.
    """
    port: int = Field(alias='REDIS_PORT')
    host: str = Field(alias='REDIS_HOST')
    db: int = Field(alias='REDIS_ACCOUNT_EVENTS_DB')
    password: str = Field(alias='REDIS_PASSWORD')


class Config(BaseModel):
    """
    Aggregated configuration model combining all domain-specific settings.

    Attributes:
        app (AppConfig): Application-level settings.
        secret (SecretConfig): Encryption secret configuration.
        redis (RedisConfig): Redis connection settings.
        rabbit (RabbitMQConfig): RabbitMQ connection settings.
    """
    app: AppConfig = Field(default_factory=AppConfig.from_env)
    secret: SecretConfig = Field(default_factory=SecretConfig.from_env)
    redis: RedisConfig = Field(default_factory=RedisConfig.from_env)
    rabbit: RabbitMQConfig = Field(default_factory=RabbitMQConfig.from_env)