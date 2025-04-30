from os import environ as env

from pydantic import BaseModel, Field, field_validator


class SecretConfig(BaseModel):
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
    def split_allowed_hosts(cls, value):
        if isinstance(value, str):
            return [] if value == "" else value.split(",")
        return value


class RabbitMQConfig(BaseModel):
    host: str = Field(alias="RABBITMQ_HOST")
    port: int = Field(alias="RABBITMQ_PORT")
    login: str = Field(alias="RABBITMQ_USER")
    password: str = Field(alias="RABBITMQ_PASSWORD")
    vhost: str = Field(alias="RABBITMQ_VHOST")


class PostgresConfig(BaseModel):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    login: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    database: str = Field(alias="POSTGRES_DB")


class RedisConfig(BaseModel):
    port: int = Field(alias="REDIS_PORT")
    host: str = Field(alias="REDIS_HOST")
    db: int = Field(alias="REDIS_SESSIONS_DB")
    password: str = Field(alias="REDIS_PASSWORD")


class Config(BaseModel):
    secret: SecretConfig = Field(
        default_factory=lambda: SecretConfig(**env)
    )
    rabbitmq: RabbitMQConfig = Field(
        default_factory=lambda: RabbitMQConfig(**env)
    )
    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**env)
    )
    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(**env)
    )