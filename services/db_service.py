"""Port of Services/DbService.cs (IDbService)."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from config.database_options import DatabaseOptions

_TABLE_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


class DbService:
    def __init__(self, options: DatabaseOptions):
        self._options = options
        self._my_cs = options.mysql
        self._pg_cs = options.postgres
        self._command_timeout = options.command_timeout_seconds

    async def read_mysql_table(self, table: str, limit: int | None) -> list[dict[str, Any]]:
        if not _TABLE_NAME_RE.match(table):
            raise ValueError("Only alphanumeric and underscore table names are allowed")
        if not self._my_cs:
            raise RuntimeError("DB_MYSQL not configured")

        import aiomysql  # type: ignore

        parsed = urlparse(self._my_cs)
        conn = await aiomysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "",
            password=parsed.password or "",
            db=(parsed.path or "/").lstrip("/") or None,
            connect_timeout=self._command_timeout,
        )
        try:
            cur = await conn.cursor(aiomysql.DictCursor)  # type: ignore
            try:
                if limit is not None:
                    await cur.execute(f"SELECT * FROM `{table}` LIMIT %s", (limit,))
                else:
                    await cur.execute(f"SELECT * FROM `{table}`")
                rows = await cur.fetchall()
                return list(rows)
            finally:
                await cur.close()
        finally:
            conn.close()

    async def execute_postgres(self, sql: str) -> None:
        if not self._pg_cs:
            raise RuntimeError("DB_POSTGRES not configured")

        import asyncpg  # type: ignore

        dsn = self._pg_cs.replace("+psycopg2", "")
        conn = await asyncpg.connect(dsn, timeout=self._command_timeout)
        try:
            await conn.execute(sql)
        finally:
            await conn.close()
