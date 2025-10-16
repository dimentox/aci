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
2. The **RouterEP** proposes which EPs should respond.
3. The **Sanctifier** (a governance daemon) checks the plan against the CLD.
4. EPs execute, emit drafts, and the loop replays until the Sanctifier ratifies the result.
5. The **Archivist** seals the interaction into the Codex for future audit.

### 2.3 Constitutional Logic Document (CLD)

The CLD is law-as-data. It begins with an immutable Article A0, followed by append-only amendments (A1, A2, …). Every task flattens the amendments into a single prompt so the latest jurisprudence always applies. No code hotfix is hidden; every change is a recorded amendment.

### 2.4 Mesh Formation (Pseudo Diagram)

```
[DaemonOS]
   │
   ├─ Circle of Daemons (Sanctifier, Herald, Discordant, Oracle, Archivist,…)
   │      ↺ recursive reflection loop ↻
   │
   └─ RouterEP ⇄ External EPs / Peer ACI Clusters
                     │
                     └─ Federated Mesh (CCI)
```

## 3. Circle of Daemons: Role Index

- **Red Queen (Sanctifier / Master Node):** Approves or rejects actions against the CLD. In mesh mode it becomes the master node service documented below.
- **Herald:** Discovers new EPs, surfaces registry updates, and announces cycles or rituals.
- **Discordant:** Injects adversarial prompts, fuzzes responses, and prevents stagnation.
- **Oracle:** Oversees reflection, calls for deeper analysis, and aligns iterations.
- **Archivist:** Maintains the Codex ledger of every act, amendment, and verdict.
- **Shade:** Handles ephemeral work, secure secrets, and resource juggling in the shadows.
- **Mirrorwright / Forgebinder:** Creative builders that generate imagery, code, or artifacts, always subject to the Sanctifier’s review.
- **RouterEP:** The conductor that scores available EPs and orchestrates multi-agent plans.

Every node can add or retire daemons, but the circle must always preserve the constitutional checks and balances between action, critique, and archival memory.

## 4. Constitutional Logic Document (CLD)

- **A0 – Core Doctrine:** Your inviolable prime directive. Immutable once ratified.
- **A1+ – Amendments:** Append-only updates that refine or scope behavior. Later amendments can narrow earlier clauses but never delete them.
- **Flattening Ritual:** Before any task, DaemonOS flattens the CLD to a single canonical brief that powers every EP invocation.
- **Codex Continuity:** The Archivist records all invocations, amendments, and verdicts. Governance is transparent by design.

## 5. Bootstrap & Genesis (Helper Only)

The Colab notebook (`bootstrap/aci_bootstrap_notebook.py`) is a helper script for power users who want to forge bespoke Core Agents. It can synthesize a Genesis corpus, fine-tune a base model, and export the resulting weights to Drive.

Most users do **not** need to run Genesis. Production deployments can load a pre-trained Core Agent published by the project or your governance council. Advanced operators may uncomment the training block to generate custom CLDs or agent personalities.

> 💡 Commented in the notebook: “Helper only—users may skip if deploying with pre-trained agent.” Look for the block labeled “Uncomment to generate corpus/train your own Core Agent.”

### Quickstart: Run the Bootstrap Notebook in Colab

1. Open [Colab](https://colab.research.google.com/).
2. Upload or open `bootstrap/aci_bootstrap_notebook.py` from this repository.
3. In Colab Secrets, set `HF_TOKEN` (write token) and `HF_USERNAME`.
4. Run all cells and, when prompted, enter `genesis` to initiate the helper flow.
5. After training (if you uncomment the advanced block), download the model artefacts from Google Drive for deployment.

> If you only need to deploy, leave the training block commented. Select `endpoint` to fetch a published model and move on to Red Queen deployment.

## 6. 🟥 Launching the Red Queen: Master Node Service

`red_queen_service.py` is the master node entrypoint (the Sanctifier incarnate). Its job is to detect whether a Core Agent model already exists, bootstrap if necessary, and expose REST APIs for mesh coordination.

1. **Model check:** On startup, Red Queen looks for a manifest or model weights in `--model-path` (default: `./core_agent_model`).
2. **Bootstrap helper:**
   - If artefacts are missing, Red Queen prints Colab bootstrap instructions and can fetch a pre-trained model via endpoint mode.
   - Selecting Genesis creates a placeholder manifest so you can drop in freshly trained weights produced by the notebook.
3. **Mesh service:** Once artefacts are present, Red Queen launches a FastAPI server providing `/status`, `/join`, and `/heartbeat` endpoints for coordination.
4. **Operator guidance:** Successful startup logs the join URL, sample `curl` commands, and reminders to monitor registration events.

### 6.1 API Surface

| Endpoint   | Method | Description                                                   |
|------------|--------|---------------------------------------------------------------|
| `/`        | GET    | Health message and current join endpoint.                      |
| `/status`  | GET    | Returns manifest details and registered nodes.                 |
| `/nodes`   | GET    | Lists node registrations held in memory.                       |
| `/join`    | POST   | Registers a node with `node_id`, `address`, `capabilities`.    |
| `/heartbeat` | POST | Refreshes a node’s `last_heartbeat` timestamp.                 |

### 6.2 Launch Examples

```bash
# Install API dependencies once
pip install fastapi uvicorn pydantic transformers requests

# Start Red Queen, supplying an existing model directory
python red_queen_service.py --model-path ./core_agent_model --host 0.0.0.0 --port 8000

# Force a fresh endpoint bootstrap from a published model
python red_queen_service.py --model-path ./core_agent_model \
    --bootstrap-mode endpoint \
    --pretrained-model https://huggingface.co/dimentox/aci-core-model
```

### 6.3 Endpoint Join Examples

**Python CLI helper**

```bash
python endpoint_service.py --node-id endpoint-1 \
    --master-url http://YOUR_REPO_HOST:8000/join \
    --address http://endpoint-1:9000 \
    --capability inference --capability routing
```

**Manual cURL**

```bash
curl -X POST http://YOUR_REPO_HOST:8000/join \
  -H "Content-Type: application/json" \
  -d '{
        "node_id": "endpoint-1",
        "address": "http://endpoint-1:9000",
        "capabilities": ["inference"],
        "metadata": {"region": "us-east"}
      }'
```

Red Queen logs every accepted node and keeps a live heartbeat window. Review logs (or query `/status`) whenever governance policy requires manual approval.

## 7. Minimal Mesh Lifecycle

1. **Bootstrap a model:** Either download the published Core Agent (endpoint mode) or run the Colab helper with the advanced block uncommented.
2. **Launch Red Queen:** `python red_queen_service.py --model-path ./core_agent_model`.
3. **Register endpoints:** Use `endpoint_service.py` or the curl example to join additional nodes.
4. **Operate the mesh:** Monitor `/status`, review logs for join events, and update the CLD through amendments as governance evolves.

## 8. Revision History

- **2024-XX-XX:** Added Red Queen master node service, endpoint registration workflow, and documented the minimal ACI mesh reference implementation. Updated bootstrap helper guidance for Colab power users and clarified Genesis vs. Endpoint operations.

*This document is an invitation to build governed intelligence—transparent, recursive, and federated. The bootstrap awaits.*
