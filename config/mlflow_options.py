"""Port of Options/MLflowOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLflowOptions(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tracking_uri: str = Field(default="", alias="MLFLOW_TRACKING_URI")
    request_timeout_seconds: int = Field(default=30, ge=5, le=300, alias="MLFLOW_REQUEST_TIMEOUT_SECONDS")
