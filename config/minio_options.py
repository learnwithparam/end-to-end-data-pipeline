"""Port of Options/MinioOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_", env_file=".env", extra="ignore")

    endpoint: str = ""
    access_key: str = Field(default="", alias="MINIO_ROOT_USER")
    secret_key: str = Field(default="", alias="MINIO_ROOT_PASSWORD")
    bucket_raw: str = "raw-data"
    bucket_processed: str = "processed-data"
    max_upload_retries: int = Field(default=2, ge=1, le=4)
