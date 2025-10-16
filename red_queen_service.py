"""Red Queen Master Node Service for the ACI Mesh.

This script bootstraps the core agent (if necessary) and exposes a
FastAPI-powered coordination endpoint for additional nodes to join the mesh.

Usage example:
    python red_queen_service.py --model-path ./core_agent_model --port 9000
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

LOGGER = logging.getLogger("red_queen")
DEFAULT_MODEL_URL = "https://huggingface.co/dimentox/aci-core-model"
FALLBACK_MODEL_REPO = "sshleifer/tiny-gpt2"
MANIFEST_FILENAME = "core_agent_manifest.json"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Red Queen master node service")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("./core_agent_model"),
        help="Directory that stores the Core Agent model artefacts.",
    )
    parser.add_argument(
        "--bootstrap-mode",
        choices=["genesis", "endpoint"],
        help="Run the bootstrap workflow immediately in the selected mode.",
    )
    parser.add_argument(
        "--pretrained-model",
        help=(
            "When bootstrapping in endpoint mode, pull weights from this Hugging Face "
            "repo id or URL."
        ),
    )
    parser.add_argument(
        "--force-bootstrap",
        action="store_true",
        help="Re-run the bootstrap workflow even when a model already exists.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface for the Red Queen API server.",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for the Red Queen API server."
    )
    parser.add_argument(
        "--public-url",
        help=(
            "Optional public URL that new endpoints should use when joining the mesh. "
            "If omitted, instructions use the host/port combination."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity for the service.",
    )
    return parser.parse_args(argv)


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def manifest_path(model_path: Path) -> Path:
    return model_path / MANIFEST_FILENAME


def load_manifest(model_path: Path) -> Optional[Dict[str, Any]]:
    try:
        with manifest_path(model_path).open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None


def write_manifest(model_path: Path, manifest: Dict[str, Any]) -> None:
    model_path.mkdir(parents=True, exist_ok=True)
    with manifest_path(model_path).open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    LOGGER.info("Saved manifest to %s", manifest_path(model_path))


def model_exists(model_path: Path) -> bool:
    if manifest_path(model_path).exists():
        return True
    if (model_path / "config.json").exists() and (model_path / "pytorch_model.bin").exists():
        return True
    return False


def prompt_for_mode() -> str:
    while True:
        mode = input("Select bootstrap mode [genesis/endpoint]: ").strip().lower()
        if mode in {"genesis", "endpoint"}:
            return mode
        print("Invalid mode. Please enter 'genesis' or 'endpoint'.")


def ensure_transformers_import() -> None:
    try:
        import transformers  # noqa: F401
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise RuntimeError(
            "The transformers package is required for endpoint bootstrapping. "
            "Install it via 'pip install transformers'."
        ) from exc


def provision_via_endpoint(model_path: Path, repo_or_url: str) -> Dict[str, Any]:
    ensure_transformers_import()
    from transformers import AutoModelForCausalLM, AutoTokenizer

    repo_id = repo_or_url.strip()
    if repo_id.startswith("https://"):
        repo_id = repo_id.rstrip("/").split("/", maxsplit=3)[-1]

    LOGGER.info("Downloading pre-trained model from %s", repo_id)
    tokenizer = AutoTokenizer.from_pretrained(repo_id)
    model = AutoModelForCausalLM.from_pretrained(repo_id)

    model_path.mkdir(parents=True, exist_ok=True)
    tokenizer.save_pretrained(model_path)
    model.save_pretrained(model_path)

    manifest = {
        "bootstrap_mode": "endpoint",
        "source": repo_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "model_path": str(model_path.resolve()),
        "artefacts": ["config.json", "pytorch_model.bin", "tokenizer.json"],
    }
    write_manifest(model_path, manifest)
    LOGGER.info("Endpoint provisioning complete.")
    return manifest


def provision_via_genesis(model_path: Path) -> Dict[str, Any]:
    model_path.mkdir(parents=True, exist_ok=True)
    marker = model_path / "GENESIS_README.txt"
    marker.write_text(
        "This directory marks a Genesis bootstrap run for the ACI Core Agent.\n"
        "Replace this placeholder with trained weights once your training pipeline finishes.\n",
        encoding="utf-8",
    )

    manifest = {
        "bootstrap_mode": "genesis",
        "source": "local-training",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "model_path": str(model_path.resolve()),
        "artefacts": [marker.name],
        "note": (
            "Placeholder artefacts generated by the Red Queen bootstrapper. "
            "Integrate with your training pipeline to produce production weights."
        ),
    }
    write_manifest(model_path, manifest)
    LOGGER.info("Genesis provisioning placeholder created. Replace artefacts with trained weights as needed.")
    return manifest


def bootstrap_core_agent(
    model_path: Path,
    mode_hint: Optional[str] = None,
    pretrained_repo_hint: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    if model_exists(model_path) and not force:
        manifest = load_manifest(model_path)
        if manifest:
            LOGGER.info("Existing manifest found. Skipping bootstrap.")
            return manifest
        LOGGER.info("Model artefacts detected without manifest. Generating manifest stub.")
        manifest = {
            "bootstrap_mode": "unknown",
            "source": "existing",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "model_path": str(model_path.resolve()),
            "artefacts": [path.name for path in model_path.glob("*")],
        }
        write_manifest(model_path, manifest)
        return manifest

    mode = mode_hint or prompt_for_mode()
    if mode == "endpoint":
        repo_or_url = pretrained_repo_hint
        if not repo_or_url:
            repo_or_url = input(
                "Enter pre-trained model URL or repo id "
                f"[default: {DEFAULT_MODEL_URL}]: "
            ).strip()
            if not repo_or_url:
                repo_or_url = DEFAULT_MODEL_URL
        try:
            return provision_via_endpoint(model_path, repo_or_url)
        except Exception as exc:
            LOGGER.error("Failed to download model from %s: %s", repo_or_url, exc)
            fallback = input(
                "Bootstrap failed. Attempt download of lightweight reference model "
                f"({FALLBACK_MODEL_REPO}) instead? [Y/n]: "
            ).strip().lower()
            if fallback in {"", "y", "yes"}:
                return provision_via_endpoint(model_path, FALLBACK_MODEL_REPO)
            raise
    return provision_via_genesis(model_path)


class JoinRequest(BaseModel):
    node_id: str = Field(..., description="Unique identifier for the joining node")
    address: Optional[str] = Field(None, description="Reachable address for callbacks")
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JoinResponse(BaseModel):
    status: str
    registered_at: str
    join_endpoint: str


def create_app(manifest: Dict[str, Any]) -> FastAPI:
    app = FastAPI(
        title="Red Queen Master Node",
        description=(
            "Central coordination service for the ACI mesh. "
            "Provides status reporting and node registration endpoints."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.manifest = manifest
    app.state.mesh_registry: Dict[str, Dict[str, Any]] = {}

    @app.get("/")
    async def root() -> Dict[str, Any]:
        return {
            "message": "Red Queen master node operational.",
            "join_endpoint": "/join",
            "nodes_registered": len(app.state.mesh_registry),
        }

    @app.get("/status")
    async def status() -> Dict[str, Any]:
        return {
            "model_ready": True,
            "manifest": app.state.manifest,
            "registered_nodes": list(app.state.mesh_registry.values()),
        }

    @app.get("/nodes")
    async def list_nodes() -> Dict[str, Any]:
        return {"nodes": list(app.state.mesh_registry.values())}

    @app.post("/join", response_model=JoinResponse)
    async def join(request: JoinRequest) -> JoinResponse:
        if not request.node_id:
            raise HTTPException(status_code=400, detail="node_id is required")

        registration = app.state.mesh_registry.get(request.node_id, {}).copy()
        timestamp = datetime.utcnow().isoformat() + "Z"
        registration.update(
            {
                "node_id": request.node_id,
                "address": request.address,
                "capabilities": request.capabilities,
                "metadata": request.metadata,
                "registered_at": timestamp,
                "last_heartbeat": timestamp,
            }
        )
        app.state.mesh_registry[request.node_id] = registration
        LOGGER.info("Node registered: %s", request.node_id)
        return JoinResponse(
            status="accepted",
            registered_at=timestamp,
            join_endpoint="/join",
        )

    @app.post("/heartbeat")
    async def heartbeat(request: JoinRequest) -> Dict[str, Any]:
        existing = app.state.mesh_registry.get(request.node_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Node not registered")
        timestamp = datetime.utcnow().isoformat() + "Z"
        existing["last_heartbeat"] = timestamp
        LOGGER.debug("Heartbeat received from %s", request.node_id)
        return {"status": "ok", "timestamp": timestamp}

    return app


def print_join_instructions(host: str, port: int, public_url: Optional[str]) -> None:
    join_url = public_url.rstrip("/") if public_url else f"http://{host}:{port}/join"
    status_url = join_url.rsplit("/", 1)[0] + "/status"
    LOGGER.info("\n=== Red Queen Ready ===")
    LOGGER.info("Core Agent manifest loaded and mesh service online.")
    LOGGER.info("New endpoints can register via: %s", join_url)
    LOGGER.info("Status dashboard available at: %s", status_url)
    join_example = "\n".join(
        [
            f"curl -X POST {join_url}",
            "  -H 'Content-Type: application/json'",
            "  -d '{\"node_id\": \"endpoint-1\", \"address\": \"http://endpoint:9000\", \"capabilities\": [\"inference\"], \"metadata\": {\"region\": \"us-east\"}}'",
        ]
    )
    LOGGER.info("Example join command:\n%s", join_example)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(args.log_level)

    try:
        manifest = bootstrap_core_agent(
            model_path=args.model_path,
            mode_hint=args.bootstrap_mode,
            pretrained_repo_hint=args.pretrained_model,
            force=args.force_bootstrap,
        )
    except Exception as exc:
        LOGGER.error("Bootstrap failed: %s", exc)
        sys.exit(1)

    app = create_app(manifest)
    print_join_instructions(args.host, args.port, args.public_url)

    uvicorn.run(app, host=args.host, port=args.port, log_config=None)


if __name__ == "__main__":
    main()
