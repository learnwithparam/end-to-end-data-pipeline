"""Port of Services/AtlasService.cs (IAtlasService)."""

from __future__ import annotations

import httpx

from config.atlas_options import AtlasOptions


class AtlasService:
    def __init__(self, options: AtlasOptions):
        self._options = options

    async def register_lineage(self, payload: str) -> str:
        if not self._options.endpoint:
            raise RuntimeError("ATLAS_API_URL not configured")
        auth = None
        if self._options.username and self._options.password:
            auth = (self._options.username, self._options.password)
        async with httpx.AsyncClient(
            base_url=self._options.endpoint, timeout=30.0, auth=auth
        ) as http:
            r = await http.post(
                "/lineage", content=payload, headers={"Content-Type": "application/json"}
            )
            r.raise_for_status()
            return r.text
