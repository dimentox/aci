"""Sanctifier daemon validates actions against the Constitutional Logic Document (CLD)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List


class Sanctifier:
    """Applies CLD policy gates to every proposed action."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger("sanctifier")
        self.allowed_actions: List[str] = self.config.get("allowed_actions", ["status"])

    def process(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action")
        if action not in self.allowed_actions:
            violation = {
                "component": "Sanctifier",
                "message": f"Action '{action}' rejected by CLD policy.",
            }
            context.setdefault("events", []).append(violation)
            self.logger.error(violation["message"])
            raise ValueError(violation["message"])
        context.setdefault("events", []).append(
            {
                "component": "Sanctifier",
                "message": f"Action '{action}' ratified.",
            }
        )
        self.logger.debug("Action %s ratified", action)
        return payload

    def describe(self) -> Dict[str, Any]:
        return {"allowed_actions": self.allowed_actions}
