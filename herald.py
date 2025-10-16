"""Herald daemon responsible for network discovery and onboarding (White Rabbit)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List


class Herald:
    """Discovers, scores, and announces new mesh endpoints."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger("herald")
        self.discovery_interval = self.config.get("discovery_interval", 30)
        self.discovered_nodes: List[Dict[str, Any]] = []

    def process(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        request = payload.copy()
        node_hint = request.get("node") or {}
        if node_hint:
            self.discovered_nodes.append(node_hint)
            context.setdefault("events", []).append(
                {
                    "component": "Herald",
                    "message": f"Discovered node {node_hint.get('id', 'unknown')}",
                }
            )
            self.logger.info("Discovered node: %s", node_hint)
        else:
            self.logger.debug("No node hint supplied for discovery.")
        request.setdefault("metadata", {})["discovery_interval"] = self.discovery_interval
        return request

    def describe(self) -> Dict[str, Any]:
        return {
            "discovery_interval": self.discovery_interval,
            "discovered": len(self.discovered_nodes),
        }
