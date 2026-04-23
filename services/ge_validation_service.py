"""Port of Services/GEValidationService.cs (IGEValidationService)."""

from __future__ import annotations

import asyncio
import os

from config.ge_options import GEOptions


class GEValidationService:
    def __init__(self, options: GEOptions):
        self._cli = options.cli_path
        self._timeout_seconds = options.timeout_seconds

    async def validate(self, suite: str) -> str:
        if not self._cli or not os.path.isfile(self._cli):
            raise FileNotFoundError(f"Great Expectations CLI not found at {self._cli}")

        proc = await asyncio.create_subprocess_exec(
            self._cli,
            "checkpoint",
            "run",
            suite,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self._timeout_seconds
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise RuntimeError("Great Expectations validation timed out")

        if proc.returncode != 0:
            raise RuntimeError(
                f"Great Expectations validation failed: {stderr.decode('utf-8', errors='ignore')}"
            )
        return stdout.decode("utf-8", errors="ignore")
