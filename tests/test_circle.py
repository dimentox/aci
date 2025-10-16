"""Minimal smoke test for the Circle of Daemons workflow."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp import MCPOrchestrator


def run_smoke() -> dict:
    orchestrator = MCPOrchestrator(PROJECT_ROOT / "mcp_config.json")
    orchestrator.load_config()
    orchestrator.register_components()

    payload = {
        "action": "status",
        "resource": "smoke",
        "hint": "integration-test",
        "node": {"id": "smoke-node"},
    }

    result = orchestrator.run_circle(payload)

    assert "metadata" in result["payload"], "Metadata must be populated by daemons"
    assert result["payload"]["metadata"].get("resource_token"), "Shade must issue tokens"
    assert any(event["component"] == "Sanctifier" for event in result["context"]["events"])
    return result


if __name__ == "__main__":
    output = run_smoke()
    print(json.dumps(output, indent=2, default=str))
