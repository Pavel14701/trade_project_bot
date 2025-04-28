from os import environ as env

from pydantic import BaseModel, Field


class SecretConfig(BaseModel):
    pepper: str = Field(alias="APP_PEPPER")
    config_secret_key: str = Field(alias="CONFIG_ENCRYPTION_KEY")


class RabbitMQConfig(BaseModel):
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASS')


class PostgresConfig(BaseModel):
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    login: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    database: str = Field(alias='POSTGRES_DB')


class RedisConfig(BaseModel):
    port: int = Field(alias='REDIS_PORT')
    host: str = Field(alias='REDIS_HOST')
    db: int = Field(alias='REDIS_ACCOUNT_EVENTS_DB')
    password: str = Field(alias='REDIS_PASSWORD')


class Config(BaseModel):
    secret: SecretConfig = Field(default_factory=lambda: SecretConfig(**env))
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig(**env))
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
    redis: RedisConfig = Field(default_factory=lambda: RedisConfig(**env))