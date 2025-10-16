"""Shade daemon manages ephemeral resources and secure operations."""
from __future__ import annotations

import logging
from typing import Any, Dict


class Shade:
    """Allocates temporary resources and ensures secrets remain obfuscated."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger("shade")
        self.active_resources: Dict[str, str] = {}

    def process(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        request = payload.copy()
        resource_key = request.get("resource", "default")
        token = self._issue_token(resource_key)
        self.active_resources[resource_key] = token
        context.setdefault("resources", {})[resource_key] = token
        context.setdefault("events", []).append(
            {"component": "Shade", "message": f"Resource token issued for {resource_key}."}
        )
        self.logger.info("Issued resource token for %s", resource_key)
        request.setdefault("metadata", {})["resource_token"] = token
        return request

    def describe(self) -> Dict[str, Any]:
        return {"active_resources": len(self.active_resources)}

    def _issue_token(self, key: str) -> str:
        from secrets import token_hex

        length = int(self.config.get("token_bytes", 8))
        return token_hex(length)
