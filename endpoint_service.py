"""Minimal endpoint registration helper for the ACI mesh.

This script is a convenience wrapper that registers a node with the
Red Queen master node service and optionally sends a heartbeat.
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List

import requests


def parse_metadata(pairs: List[str]) -> Dict[str, str]:
    metadata: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Metadata '{pair}' must be in key=value format")
        key, value = pair.split("=", 1)
        metadata[key] = value
    return metadata


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register this endpoint with a Red Queen master node.",
    )
    parser.add_argument("--node-id", required=True, help="Unique identifier for this endpoint")
    parser.add_argument(
        "--master-url",
        required=True,
        help="Full join URL exposed by the Red Queen service (e.g. http://host:8000/join)",
    )
    parser.add_argument("--address", help="Optional callback address for this endpoint")
    parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Capabilities to advertise (repeat flag for multiple entries)",
    )
    parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Additional metadata entries expressed as key=value",
    )
    parser.add_argument(
        "--heartbeat",
        action="store_true",
        help="Send a follow-up heartbeat call after registration succeeds.",
    )
    return parser


def send_join_request(args: argparse.Namespace) -> Dict[str, str]:
    payload = {
        "node_id": args.node_id,
        "address": args.address,
        "capabilities": args.capability,
        "metadata": parse_metadata(args.metadata),
    }
    response = requests.post(args.master_url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def send_heartbeat(join_url: str, node_id: str) -> Dict[str, str]:
    if join_url.endswith("/join"):
        heartbeat_url = join_url.rsplit("/", 1)[0] + "/heartbeat"
    else:
        heartbeat_url = join_url.rstrip("/") + "/heartbeat"
    response = requests.post(heartbeat_url, json={"node_id": node_id}, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    join_result = send_join_request(args)
    print("✅ Join accepted")
    print(json.dumps(join_result, indent=2))

    if args.heartbeat:
        heartbeat_result = send_heartbeat(args.master_url, args.node_id)
        print("✅ Heartbeat acknowledged")
        print(json.dumps(heartbeat_result, indent=2))


if __name__ == "__main__":
    main()
