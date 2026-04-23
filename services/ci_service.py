"""Port of Services/CIService.cs (ICIService)."""

from __future__ import annotations

import httpx

from config.github_options import GitHubOptions


class CIService:
    def __init__(self, options: GitHubOptions):
        self._options = options

    async def trigger_workflow(self, workflow_file: str, branch: str) -> str:
        if not self._options.actions_api or not self._options.token:
            raise RuntimeError("GITHUB_ACTIONS_API / GITHUB_TOKEN not configured")
        base = self._options.actions_api.rstrip("/") + "/"
        async with httpx.AsyncClient(
            base_url=base,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self._options.token}",
                "User-Agent": self._options.user_agent,
            },
        ) as http:
            r = await http.post(f"{workflow_file}/dispatches", json={"ref": branch})
            r.raise_for_status()
            return r.text
