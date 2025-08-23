from os import environ as env
from typing import Type, TypeVar, get_type_hints

from pydantic import BaseModel, Field

ConfigModelType = TypeVar("ConfigModelType", bound="EnvModel")


class EnvModel(BaseModel):
    @classmethod
    def from_env(cls: Type[ConfigModelType]) -> ConfigModelType:
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
    secret: SecretConfig = Field(default_factory=SecretConfig.from_env)
    redis: RedisConfig = Field(default_factory=RedisConfig.from_env)
    rabbit: RabbitMQConfig = Field(default_factory=RabbitMQConfig.from_env)