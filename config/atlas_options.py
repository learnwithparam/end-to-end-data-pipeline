"""Port of Options/AtlasOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AtlasOptions(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    endpoint: str = Field(default="", alias="ATLAS_API_URL")
    username: str = Field(default="", alias="ATLAS_USERNAME")
    password: str = Field(default="", alias="ATLAS_PASSWORD")
