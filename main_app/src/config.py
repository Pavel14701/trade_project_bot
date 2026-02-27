from os import environ as env
from typing import Type, TypeVar, get_type_hints

from pydantic import BaseModel, Field, field_validator

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
    allowed_hosts: list[str] = Field(
        default_factory=list, 
        alias="APP_ALLOWED_HOSTS"
    )
    config_secret_key: str = Field(
        alias="APP_CONFIG_ENCRYPTION_KEY"
    )
    log_level: str = Field(
        default="info", 
        alias='APP_LOG_LEVEL'
    )
    pepper: str = Field(alias="APP_PEPPER")

    @field_validator("allowed_hosts", mode="before")
    def split_allowed_hosts(cls, value: str) -> list[str]:
        return value.split(",") if value else []


class RabbitMQConfig(EnvModel):
    host: str = Field(alias="RABBITMQ_HOST")
    port: int = Field(alias="RABBITMQ_PORT")
    login: str = Field(alias="RABBITMQ_USER")
    password: str = Field(alias="RABBITMQ_PASSWORD")
    vhost: str = Field(alias="RABBITMQ_VHOST")


class PostgresConfig(EnvModel):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    login: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    database: str = Field(alias="POSTGRES_DB")


class RedisConfig(EnvModel):
    port: int = Field(alias="REDIS_PORT")
    host: str = Field(alias="REDIS_HOST")
    db: int = Field(alias="REDIS_SESSIONS_DB")
    password: str = Field(alias="REDIS_PASSWORD")


class Config(BaseModel):
    secret: SecretConfig = Field(default_factory=SecretConfig.from_env)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig.from_env)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig.from_env)
    redis: RedisConfig = Field(default_factory=RedisConfig.from_env)