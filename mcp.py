"""Master Control Program (MCP) orchestrator for the ACI Pantheon.

See Artificial_Collective_Intelligence__Beyond_AGI-published.pdf, Section 2.2.

The MCP bootstraps the core agent artefacts when required, loads all
Pantheon daemon components from a configuration file, and exposes a
FastAPI control plane for mesh coordination. Incoming requests can be
processed through the Circle of Daemons pipeline to exercise the
sanction, audit, and chaos feedback loops while respecting canonical
governance defaults.
"""
from __future__ import annotations

import argparse
import importlib
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:  # FastAPI is optional for non-server contexts (e.g., unit tests)
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:  # pragma: no cover - optional dependency guard
    FastAPI = None  # type: ignore
    HTTPException = None  # type: ignore
    CORSMiddleware = None  # type: ignore

try:  # Pydantic is only needed when serving the API
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency guard
    PYDANTIC_AVAILABLE = False

    class BaseModel:  # type: ignore
        """Fallback shim so unit tests can import the module without Pydantic."""

        def __init__(self, **data: Any) -> None:
            for key, value in data.items():
                setattr(self, key, value)

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return None

try:  # uvicorn is only required when running the API server
    import uvicorn
except ImportError:  # pragma: no cover - optional dependency guard
    uvicorn = None  # type: ignore

LOGGER = logging.getLogger("mcp")
DEFAULT_MODEL_URL = "https://huggingface.co/dimentox/aci-core-model"
FALLBACK_MODEL_REPO = "sshleifer/tiny-gpt2"
MANIFEST_FILENAME = "core_agent_manifest.json"


@dataclass
class ComponentDefinition:
    """Runtime description of a daemon component."""

    name: str
    module: str
    class_name: str
    enabled: bool = True
    config: Dict[str, Any] | None = None


class MCPOrchestrator:
    """Loads and coordinates Pantheon daemons for the mesh."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}
        self.workflow: List[str] = []

    def load_config(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with self.config_path.open("r", encoding="utf-8") as handle:
            self.config = json.load(handle)
        self.workflow = list(self.config.get("workflow", []))
        LOGGER.debug("Loaded MCP config with workflow: %s", self.workflow)

    def _iter_component_definitions(self) -> Iterable[ComponentDefinition]:
        for entry in self.config.get("components", []):
            definition = ComponentDefinition(
                name=entry["name"],
                module=entry["module"],
                class_name=entry["class"],
                enabled=entry.get("enabled", True),
                config=entry.get("config"),
            )
            yield definition

    def register_components(self) -> None:
        self.components.clear()
        for definition in self._iter_component_definitions():
            if not definition.enabled:
                LOGGER.info("Skipping disabled component: %s", definition.name)
                continue
            module = importlib.import_module(definition.module)
            cls = getattr(module, definition.class_name)
            instance = cls(config=definition.config or {})
            self.components[definition.name] = instance
            LOGGER.info(
                "Registered component %s from %s.%s",
                definition.name,
                definition.module,
                definition.class_name,
            )
        if not self.workflow:
            self.workflow = list(self.components.keys())
        LOGGER.debug("Active workflow order: %s", self.workflow)

    def run_circle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "events": [],
            "ledger": [],
        }
        request = payload.copy()
        for name in self.workflow:
            component = self.components.get(name)
            if component is None:
                raise RuntimeError(f"Workflow references unknown component: {name}")
            if not hasattr(component, "process"):
                raise AttributeError(
                    f"Component {name} does not expose a 'process' method"
                )
            LOGGER.debug("Invoking %s", name)
            result = component.process(request, context)
            if result is not None:
                request = result
        return {"payload": request, "context": context}

    def component_status(self) -> List[Dict[str, Any]]:
        status: List[Dict[str, Any]] = []
        for name, component in self.components.items():
            info = {
                "name": name,
                "module": component.__class__.__module__,
                "class": component.__class__.__name__,
            }
            if hasattr(component, "describe"):
                info.update(component.describe())
            status.append(info)
        return status

    def mesh_registration_settings(self) -> Dict[str, Any]:
        features = self.config.get("features", {})
        mesh = features.get("mesh_registration", {})
        return {
            "enabled": bool(mesh.get("enabled", False)),
            "note": mesh.get("note"),
        }


def print_colab_helper_instructions(model_path: Path) -> None:
    LOGGER.info("No Core Agent artefacts detected at %s", model_path)
    LOGGER.info(
        "To forge new weights, open Colab, load bootstrap/aci_bootstrap_notebook.py,"
        " set HF_TOKEN & HF_USERNAME, run all cells with genesis mode, and download"
        " the exported model into this path."
    )
    LOGGER.info(
        "Prefer a published agent? Choose endpoint mode to download"
        " https://huggingface.co/dimentox/aci-core-model or your own registry."
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Master Control Program orchestrator")
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
        help="Host interface for the MCP API server.",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for the MCP API server."
    )
    parser.add_argument(
        "--public-url",
        help=(
            "Optional public URL used when the evolutionary mesh federation join endpoint is enabled. "
            "If omitted, instructions use the host/port combination."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity for the service.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("mcp_config.json"),
        help="Configuration file that lists enabled MCP components.",
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
            "Placeholder artefacts generated by the MCP bootstrapper. "
            "Integrate with your training pipeline to produce production weights."
        ),
    }
    write_manifest(model_path, manifest)
    LOGGER.info("Genesis provisioning placeholder created. Replace artefacts with trained weights as needed.")
    LOGGER.info(
        "Next steps: run the Colab helper in genesis mode and copy the exported"
        " model artefacts into %s before restarting the MCP.",
        model_path,
    )
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

    if not model_exists(model_path) or force:
        print_colab_helper_instructions(model_path)

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


class CircleRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


def create_app(manifest: Dict[str, Any], orchestrator: MCPOrchestrator) -> FastAPI:
    if (
        FastAPI is None
        or CORSMiddleware is None
        or HTTPException is None
        or not PYDANTIC_AVAILABLE
    ):
        raise RuntimeError(
            "FastAPI and Pydantic are required to create the MCP control plane. Install them via 'pip install fastapi uvicorn pydantic'."
        )
    app = FastAPI(
        title="MCP Orchestrator",
        description=(
            "Central coordination service for the ACI mesh. "
            "Provides status reporting, node registration, and Circle of Daemons execution."
        ),
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    orchestrator.load_config()
    orchestrator.register_components()
    mesh_settings = orchestrator.mesh_registration_settings()

    app.state.manifest = manifest
    app.state.mesh_registry: Dict[str, Dict[str, Any]] = {}
    app.state.orchestrator = orchestrator
    app.state.mesh_settings = mesh_settings

    @app.get("/")
    async def root() -> Dict[str, Any]:
        response: Dict[str, Any] = {
            "message": "Master Control Program online.",
            "components": app.state.orchestrator.workflow,
            "mesh_registration": dict(mesh_settings),
        }
        if mesh_settings["enabled"]:
            response.update(
                {
                    "join_endpoint": "/join",
                    "nodes_registered": len(app.state.mesh_registry),
                }
            )
        return response

    @app.get("/status")
    async def status() -> Dict[str, Any]:
        status_payload: Dict[str, Any] = {
            "model_ready": True,
            "manifest": app.state.manifest,
            "components": app.state.orchestrator.component_status(),
            "workflow": app.state.orchestrator.workflow,
            "mesh_registration": dict(mesh_settings),
        }
        if mesh_settings["enabled"]:
            status_payload["registered_nodes"] = list(
                app.state.mesh_registry.values()
            )
        return status_payload

    if mesh_settings["enabled"]:
        # Evolutionary Extension: Mesh Federation & Endpoint Registration
        # See: From ACI to CCI... Section "Fractal Evolution"

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

    @app.post("/circle")
    async def circle(request: CircleRequest) -> Dict[str, Any]:
        result = app.state.orchestrator.run_circle(request.payload)
        return {
            "result": result,
            "workflow": app.state.orchestrator.workflow,
        }

    return app


def print_join_instructions(
    host: str, port: int, public_url: Optional[str], mesh_settings: Dict[str, Any]
) -> None:
    if not mesh_settings.get("enabled"):
        LOGGER.info(
            "Mesh federation join endpoints are disabled by default (evolutionary extension)."
        )
        note = mesh_settings.get("note")
        if note:
            LOGGER.info(note)
        return

    join_url = public_url.rstrip("/") if public_url else f"http://{host}:{port}/join"
    status_url = join_url.rsplit("/", 1)[0] + "/status"
    LOGGER.info("\n=== MCP Ready ===")
    LOGGER.info("Core Agent manifest loaded and orchestrator online.")
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
    LOGGER.info(
        "Helper script available: python endpoint_service.py --node-id NODE --master-url %s",
        join_url,
    )


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

    orchestrator = MCPOrchestrator(config_path=args.config)
    try:
        app = create_app(manifest, orchestrator)
    except Exception as exc:
        LOGGER.error("Failed to initialise MCP components: %s", exc)
        sys.exit(1)

    mesh_settings = orchestrator.mesh_registration_settings()
    print_join_instructions(args.host, args.port, args.public_url, mesh_settings)

    if uvicorn is None:
        LOGGER.error("uvicorn is required to run the MCP API server. Install it via 'pip install uvicorn'.")
        sys.exit(1)

    uvicorn.run(app, host=args.host, port=args.port, log_config=None)


if __name__ == "__main__":
    main()
