"""Port of Options/GitHubOptions.cs."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class GitHubOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GITHUB_", env_file=".env", extra="ignore")

    actions_api: str = ""
    token: str = ""
    user_agent: str = "data-pipeline-api"
