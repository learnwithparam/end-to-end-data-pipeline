"""Port of Options/AirflowOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AirflowOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIRFLOW_", env_file=".env", extra="ignore")

    base_url: str = ""
    username: str = ""
    password: str = ""
    batch_dag_id: str = "batch_ingestion_dag"
    streaming_dag_id: str = "streaming_monitoring_dag"
    warehouse_dag_id: str = "warehouse_transform_dag"
    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
