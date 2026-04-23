"""Port of HealthChecks/KafkaHealthCheck.cs."""

from __future__ import annotations

import asyncio

from config.kafka_options import KafkaOptions

from .common import HealthCheckResult


class KafkaHealthCheck:
    def __init__(self, options: KafkaOptions):
        self._options = options

    async def check(self, timeout: float = 5.0) -> HealthCheckResult:
        if not self._options.bootstrap_servers or not self._options.topic:
            return HealthCheckResult.unhealthy("Kafka not configured")

        def _probe() -> HealthCheckResult:
            from confluent_kafka.admin import AdminClient  # type: ignore

            admin = AdminClient(
                {
                    "bootstrap.servers": self._options.bootstrap_servers,
                    "client.id": f"{self._options.client_id}-health",
                }
            )
            metadata = admin.list_topics(topic=self._options.topic, timeout=timeout)
            topic_meta = metadata.topics.get(self._options.topic)
            if topic_meta is None or topic_meta.error is not None:
                return HealthCheckResult.degraded(
                    f"Kafka topic '{self._options.topic}' not available"
                )
            return HealthCheckResult.healthy()

        try:
            return await asyncio.wait_for(asyncio.to_thread(_probe), timeout=timeout + 1)
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"Kafka unavailable: {exc}")
