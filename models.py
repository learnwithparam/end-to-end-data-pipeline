"""Python port of sample_dotnet_backend/Models/*.cs.

BatchRequest / BatchResponse <- Models/BatchRequest.cs
StreamingRequest / StreamingResponse <- Models/StreamingRequest.cs
Plus helper response models for the ported controller endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BatchRequest(BaseModel):
    source_table: str = Field(..., pattern=r"^[A-Za-z0-9_]+$")
    destination_prefix: str | None = Field(default=None, max_length=200)
    limit: int | None = Field(default=None, ge=1, le=100000)
    trigger_airflow: bool = True
    run_great_expectations: bool = True


class BatchResponse(BaseModel):
    object_key: str = ""
    run_id: str | None = None
    ge_report: str | None = None
    status: str = "accepted"


class StreamingRequest(BaseModel):
    partition: int = Field(default=0, ge=0)
    payload: dict[str, Any] | None = None


class StreamingResponse(BaseModel):
    run_id: str
    status: str | None = None


class WarehouseHealth(BaseModel):
    status: str
    staging_db: str
    warehouse: str
    schema_: str | None = Field(default=None, alias="schema")
    snowflake: dict[str, Any] | None = None


class WarehouseTransformResponse(BaseModel):
    run_id: str = Field(alias="runId")
    message: str
    target: str


class SnowflakeStatus(BaseModel):
    configured: bool
    account: str | None = None
    warehouse_name: str
    database: str
    schema_name: str
    role: str
    tables: dict[str, list[str]]


class AggregationsResponse(BaseModel):
    source: str
    message: str | None = None
    snowflake_table: str | None = None
    postgres_table: str | None = None
