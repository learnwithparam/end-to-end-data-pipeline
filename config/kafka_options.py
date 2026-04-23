"""Port of Options/KafkaOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", extra="ignore")

    bootstrap_servers: str = Field(default="", alias="KAFKA_BROKER")
    topic: str = Field(default="", alias="KAFKA_TOPIC")
    client_id: str = "data-pipeline-api"
    message_timeout_ms: int = Field(default=5000, ge=500, le=30000)
    producer_flush_seconds: int = Field(default=2, ge=1, le=10)
