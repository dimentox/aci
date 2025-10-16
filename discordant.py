"""Discordant daemon injects chaos, fuzzing, and anti-stagnation challenges."""
from __future__ import annotations

import logging
import random
from typing import Any, Dict


class Discordant:
    """Perturbs requests to ensure resilience under adversarial conditions."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger("discordant")
        self.chaos_level = float(self.config.get("chaos_level", 0.1))

    def process(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        request = payload.copy()
        chaos_trigger = random.random() < self.chaos_level
        if chaos_trigger:
            request.setdefault("metadata", {})["discordant"] = "perturbed"
            context.setdefault("events", []).append(
                {"component": "Discordant", "message": "Chaos injection applied."}
            )
            self.logger.warning("Chaos injection applied to request")
        else:
            self.logger.debug("No chaos triggered this cycle")
        return request

    def describe(self) -> Dict[str, Any]:
        return {"chaos_level": self.chaos_level}
