"""Port of Services/KafkaService.cs (IKafkaService)."""

from __future__ import annotations

import asyncio

from config.kafka_options import KafkaOptions


class KafkaService:
    def __init__(self, options: KafkaOptions):
        self._options = options
        self._producer = None

    def _build_producer(self):
        from confluent_kafka import Producer  # type: ignore

        return Producer(
            {
                "bootstrap.servers": self._options.bootstrap_servers,
                "client.id": self._options.client_id,
                "acks": "all",
                "enable.idempotence": True,
                "message.send.max.retries": 3,
                "message.timeout.ms": self._options.message_timeout_ms,
            }
        )

    async def produce(self, message: str) -> None:
        if not self._options.bootstrap_servers or not self._options.topic:
            raise RuntimeError("Kafka not configured")

        if self._producer is None:
            self._producer = await asyncio.to_thread(self._build_producer)

        def _send():
            assert self._producer is not None
            self._producer.produce(self._options.topic, message)
            self._producer.flush(self._options.producer_flush_seconds)

        await asyncio.to_thread(_send)

    async def dispose(self) -> None:
        if self._producer is not None:
            producer = self._producer
            self._producer = None
            await asyncio.to_thread(producer.flush, self._options.producer_flush_seconds)
