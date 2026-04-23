"""Port of Services/MinioService.cs (IStorageService)."""

from __future__ import annotations

import asyncio
import io
from urllib.parse import urlparse

from config.minio_options import MinioOptions


def _parse_endpoint(endpoint: str) -> tuple[str, bool]:
    parsed = urlparse(endpoint if "://" in endpoint else f"http://{endpoint}")
    host = parsed.netloc or parsed.path
    secure = parsed.scheme == "https"
    return host, secure


class MinioService:
    def __init__(self, options: MinioOptions):
        self._options = options
        self._b_raw = options.bucket_raw
        self._b_proc = options.bucket_processed
        self._buckets_ensured = False
        self._bucket_lock = asyncio.Lock()

    def _client(self):
        from minio import Minio  # type: ignore

        host, secure = _parse_endpoint(self._options.endpoint)
        return Minio(
            host,
            access_key=self._options.access_key,
            secret_key=self._options.secret_key,
            secure=secure,
        )

    async def _ensure_buckets(self) -> None:
        if self._buckets_ensured:
            return
        async with self._bucket_lock:
            if self._buckets_ensured:
                return
            client = self._client()
            for bucket in (self._b_raw, self._b_proc):
                if not await asyncio.to_thread(client.bucket_exists, bucket):
                    await asyncio.to_thread(client.make_bucket, bucket)
            self._buckets_ensured = True

    async def upload_raw(self, key: str, data: io.BytesIO) -> None:
        await self._put_with_retry(self._b_raw, key, data)

    async def upload_processed(self, key: str, data: io.BytesIO) -> None:
        await self._put_with_retry(self._b_proc, key, data)

    async def download_raw(self, key: str) -> io.BytesIO:
        await self._ensure_buckets()
        client = self._client()

        def _get() -> io.BytesIO:
            resp = client.get_object(self._b_raw, key)
            try:
                return io.BytesIO(resp.read())
            finally:
                resp.close()
                resp.release_conn()

        return await asyncio.to_thread(_get)

    async def _put_with_retry(self, bucket: str, key: str, data: io.BytesIO) -> None:
        await self._ensure_buckets()
        client = self._client()
        attempts = 0
        length = len(data.getvalue())
        while True:
            attempts += 1
            try:
                data.seek(0)
                await asyncio.to_thread(client.put_object, bucket, key, data, length)
                return
            except Exception:
                if attempts > self._options.max_upload_retries:
                    raise
                await asyncio.sleep(0.2 * attempts)
