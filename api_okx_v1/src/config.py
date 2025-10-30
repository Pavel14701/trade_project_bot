from os import environ as env
from typing import Type, TypeVar, get_type_hints

from pydantic import BaseModel, Field

ConfigModelType = TypeVar("ConfigModelType", bound="EnvModel")


class EnvModel(BaseModel):
    @classmethod
    def from_env(cls: Type[ConfigModelType]) -> ConfigModelType:
        """
        Load configuration values from environment variables and instantiate the model.

        This method is designed to automatically populate a Pydantic model with values
        sourced from the system's environment variables. It iterates over the model's
        declared fields and attempts to retrieve corresponding values from the environment
        using either the field's alias (if defined) or its name.

        For each field:
        - It checks if the corresponding environment variable exists.
        - If found, it attempts to cast the value to the expected type using type hints.
        - If casting fails, it falls back to using the raw string value.
        - Fields not present in the environment are left unset (and may use defaults if defined).

        This method is particularly useful for loading configuration settings (e.g., API keys,
        database URLs, feature flags) into a strongly typed model without manually parsing
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
    config_secret_key: str = Field(alias="APP_CONFIG_ENCRYPTION_KEY")

class AppConfig(EnvModel):
    name: str = Field(alias="OKX_API_APP_NAME")
    host: str = Field(alias="OKX_API_APP_HOST")
    port: int = Field(alias="OKX_API_APP_PORT")
    reloading: bool = Field(True, alias="OKX_API_APP_RELOADING")

class RabbitMQConfig(EnvModel):
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASSWORD')
    vhost: str = Field(alias='RABBITMQ_VHOST')


class RedisConfig(EnvModel):
    port: int = Field(alias='REDIS_PORT')
    host: str = Field(alias='REDIS_HOST')
    db: int = Field(alias='REDIS_ACCOUNT_EVENTS_DB')
    password: str = Field(alias='REDIS_PASSWORD')


class Config(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig.from_env)
    secret: SecretConfig = Field(default_factory=SecretConfig.from_env)
    redis: RedisConfig = Field(default_factory=RedisConfig.from_env)
    rabbit: RabbitMQConfig = Field(default_factory=RabbitMQConfig.from_env)