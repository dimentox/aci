# 🚀 Artificial Collective Intelligence (ACI) & Collective Compute Intelligence (CCI)

**A minimal, dynamic reference implementation for governed mesh intelligence.**

This repository does not ship a turnkey product or polished library. It is a scaffolding kit—a living reference that shows how to assemble a lawful, federated collective of agents. Everything is modular, traceable, and meant to be remixed. You are invited to adapt it, extend it, and graft in your own constitutional logic to forge a sovereign node inside a wider Collective Compute Intelligence (CCI) mesh.

## 1. Introduction: The ACI / CCI Manifesto

Modern AI systems concentrate power in single monoliths. They hallucinate, forget, and demand fragile guardrails. Artificial Collective Intelligence rejects that paradigm. Instead of one inscrutable model, ACI composes many smaller **Entity Programs (EPs)** under an auditable constitution. Governance, not scale, is the source of trust.

**Core philosophy**

- **Modular intelligence:** Each capability lives in its own EP. Any EP can be swapped, retrained, or retired without collapsing the whole.
- **Lawful execution:** Every action is vetted against a versioned **Constitutional Logic Document (CLD)**. No daemon outruns the law.
- **Recursive reflection:** The system iterates through structured feedback loops so drafts are critiqued, revised, and ratified before release.
- **Federated mesh:** Nodes speak a shared ritual language and may federate into higher-order meshes—collective intelligence composed of collectives.

ACI is the groundwork. When many ACI clusters coordinate and offload work to each other, you arrive at **Collective Compute Intelligence (CCI)**: a fractal network of governed cognition spanning devices, edges, and clouds.

## 2. Architecture & Core Concepts

### 2.1 DaemonOS & the Circle of Daemons

At the center of every node is **DaemonOS**, a ritual runtime that hosts, schedules, and sandboxes EPs. Think of it as the constitutional kernel: it mediates memory, timing, and invocation, and it insists that every action is logged against the CLD.

EPs are arranged in a **Circle of Daemons**—a cooperative of specialized roles that cover observation, critique, synthesis, and governance. Their dialogue forms the recursive reflection loop that keeps the system honest.

### 2.2 Recursive Reflection Loop

1. A user or peer issues a request.
2. The **MCP** (Master Control Program) loads the configured daemons, routes the request, and keeps context.
3. The **Sanctifier** (a governance daemon) checks the plan against the CLD.
4. EPs execute, emit drafts, and the loop replays until the Sanctifier ratifies the result.
5. The **Archivist** seals the interaction into the Codex for future audit while the **Discordant** and **Shade** ensure resilience and operational secrecy.

### 2.3 Constitutional Logic Document (CLD)

The CLD is law-as-data. It begins with an immutable Article A0, followed by append-only amendments (A1, A2, …). Every task flattens the amendments into a single prompt so the latest jurisprudence always applies. No code hotfix is hidden; every change is a recorded amendment.

### 2.4 Mesh Formation (Pseudo Diagram)

```
[DaemonOS]
   │
   ├─ Circle of Daemons (Sanctifier, Herald, Discordant, Oracle, Archivist, Shade,…)
   │      ↺ recursive reflection loop ↻
   │
   └─ RouterEP ⇄ External EPs / Peer ACI Clusters
                    │
                    └─ Federated Mesh (CCI)
```

## 3. Core Components: The Circle of Daemons

The MCP loads each daemon from `mcp_config.json`. Every module exposes a Python class with a `process(request, context)` method so the orchestrator can iterate through the workflow.

| Role | File | Description | Extend / Replace |
|------|------|-------------|------------------|
| MCP | [`mcp.py`](../mcp.py) | Mesh orchestrator, routes EP calls, governs registry/config, exposes FastAPI control plane | Add modules to `mcp_config.json` and ship a compatible Python class |
| Herald | [`herald.py`](../herald.py) | Discovers, registers, and onboards new endpoints/nodes (White Rabbit) | Override discovery cadence or gossip protocols via subclassing |
| Sanctifier | [`sanctifier.py`](../sanctifier.py) | Validates all actions against the CLD | Inject custom validators, policy engines, or external compliance hooks |
| Oracle | [`oracle.py`](../oracle.py) | Performs sanity/meta-governance, recursive loop breaks | Extend with heuristics or model calls that emit reflective guidance |
| Archivist | [`archivist.py`](../archivist.py) | Logs and journals every action/amendment/event | Swap storage backends (SQL, object storage, append-only ledger) |
| Discordant | [`discordant.py`](../discordant.py) | Fuzzing, chaos injection, adversarial testing | Dial `chaos_level` or plug advanced fuzzers / security tooling |
| Shade | [`shade.py`](../shade.py) | Handles ephemeral resources and secure ops | Integrate HSMs, vaults, or ephemeral compute token issuers |

### 3.1 Registering a New Daemon

1. Create a Python module that exposes a class with a `process` method.
2. Optionally add a `describe()` helper for richer `/status` output.
3. Update `mcp_config.json` with the module path, class name, and any configuration block.
4. Restart `python mcp.py --config mcp_config.json` to load the new daemon.

```python
# custom_scribe.py
class Scribe:
    def __init__(self, config=None):
        self.path = config.get("path", "scribe.log")

    def process(self, payload, context):
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(f"{payload}\n")
        context.setdefault("events", []).append({"component": "Scribe", "message": "draft saved"})
        return payload
```

```json
// mcp_config.json
{
  "components": [
    { "name": "Scribe", "module": "custom_scribe", "class": "Scribe", "enabled": true }
  ],
  "workflow": ["Herald", "Sanctifier", "Scribe", "Archivist", "Discordant", "Shade"]
}
```

## 4. Mesh Workflow

### 4.1 Node Boot Sequence

1. **Load config** – MCP reads `mcp_config.json` and imports each enabled daemon.
2. **Bootstrap core agent** – If weights are missing, MCP prompts for Genesis or endpoint provisioning.
3. **Start control plane** – FastAPI service exposes `/status`, `/join`, `/heartbeat`, and `/circle`.
4. **Register daemons** – MCP instantiates each class and records the active workflow order.
5. **Enter ritual loop** – Incoming `/circle` requests traverse Herald → Sanctifier → Oracle → Archivist → Discordant → Shade and return the enriched payload/context.

### 4.2 Adding a New Endpoint

1. Copy/extend an EP or author a new daemon module.
2. Update `mcp_config.json` with the module/class and optional configuration.
3. Restart MCP to load the component.
4. For remote worker nodes, run `python endpoint_service.py --node-id ... --master-url http://HOST:8000/join`.
5. Confirm presence in `/status` and `/nodes` responses.

### 4.3 Minimal vs Advanced Deployment

- **Minimal mesh:** Keep the default config, run `python mcp.py --config mcp_config.json`, and use `/circle` with payload `{"action": "status"}` to exercise the loop.
- **Advanced extension:** Subclass `Sanctifier` to enforce enterprise policy, add an `Oracle` hook that queries Hugging Face models, and increase `Discordant` chaos for fuzz testing. Update config, restart MCP, and run integration tests to verify the Circle of Daemons.

## 5. Constitutional Logic Document (CLD)

- **A0 – Core Doctrine:** Your inviolable prime directive. Immutable once ratified.
- **A1+ – Amendments:** Append-only updates that refine or scope behavior. Later amendments can narrow earlier clauses but never delete them.
- **Flattening Ritual:** Before any task, DaemonOS flattens the CLD to a single canonical brief that powers every EP invocation.
- **Codex Continuity:** The Archivist records all invocations, amendments, and verdicts. Governance is transparent by design.

## 6. Quickstart: Operate the MCP Control Plane

1. Install dependencies: `pip install -r bootstrap/requirements.txt fastapi uvicorn`.
2. Edit `mcp_config.json` for your environment.
3. Launch MCP: `python mcp.py --config mcp_config.json --model-path ./core_agent_model`.
4. Query `/status` to verify the manifest and workflow.
5. Register endpoints via `python endpoint_service.py --node-id ep-1 --master-url http://localhost:8000/join --heartbeat`.
6. Exercise the Circle of Daemons: `curl -X POST http://localhost:8000/circle -H "Content-Type: application/json" -d '{"payload": {"action": "status", "resource": "demo"}}'`.

## 7. Advanced Operator Notes

- **Subclassing an EP:**

  ```python
  from sanctifier import Sanctifier

  class EnterpriseSanctifier(Sanctifier):
      def process(self, payload, context):
          payload.setdefault("metadata", {})["enterprise"] = True
          return super().process(payload, context)
  ```

  Update `mcp_config.json` to reference `enterprise_sanctifier.EnterpriseSanctifier`.

- **Expose a new API:** Add a FastAPI router inside your daemon and register it from MCP by extending `create_app` to include the router after instantiation.
- **Config extension:** Use nested config dictionaries in `mcp_config.json` to supply credentials, rate limits, or Hugging Face repository IDs.
- **Hugging Face integration:** Provide `--bootstrap-mode endpoint --pretrained-model org/model-id` to download published weights before the mesh comes online.
- **Production hardening:** Run MCP behind TLS, connect `Archivist` to durable storage, and use `Shade` to issue secrets from HSM/Vault systems.
- **Custom CLD:** Keep the canonical `core_cld.json` in sync, ship amendments alongside new daemons, and update the Sanctifier to enforce jurisdictional policy.

## 8. Bootstrap & Genesis (Helper Only)

The Colab notebook (`bootstrap/aci_bootstrap_notebook.py`) is a helper script for power users who want to forge bespoke Core Agents. It can synthesize a Genesis corpus, fine-tune a base model, and export the resulting weights to Drive.

Most users do **not** need to run Genesis. Production deployments can load a pre-trained Core Agent published by the project or your governance council. Advanced operators may uncomment the training block to generate custom CLDs or agent personalities.

> 💡 Commented in the notebook: “Helper only—users may skip if deploying with pre-trained agent.” Look for the block labeled “Uncomment to generate corpus/train your own Core Agent.”

### Quickstart: Run the Bootstrap Notebook in Colab

1. Open [Colab](https://colab.research.google.com/).
2. Upload or open `bootstrap/aci_bootstrap_notebook.py` from this repository.
3. In Colab Secrets, set `HF_TOKEN` (write token) and `HF_USERNAME`.
4. Run all cells and, when prompted, enter `genesis` to initiate the helper flow.
5. After training (if you uncomment the advanced block), download the model artefacts from Google Drive for deployment.

> If you only need to deploy, leave the training block commented. Select `endpoint` to fetch a published model and move on to MCP deployment.

## 9. Minimal Mesh Lifecycle

1. **Bootstrap a model:** Either download the published Core Agent (endpoint mode) or run the Colab helper with the advanced block uncommented.
2. **Launch MCP:** `python mcp.py --config mcp_config.json --model-path ./core_agent_model`.
3. **Register endpoints:** Use `endpoint_service.py` or the curl example to join additional nodes.
4. **Operate the mesh:** Monitor `/status`, review logs for join events, and update the CLD through amendments as governance evolves.

## 10. Revision History

- **2024-XX-XX:** Introduced the MCP orchestrator, Pantheon daemon modules, dynamic configuration, and Circle of Daemons documentation. Updated bootstrap helper guidance for Colab power users and clarified Genesis vs. Endpoint operations.

*This document is an invitation to build governed intelligence—transparent, recursive, and federated. The bootstrap awaits.*
