# Artificial Collective Intelligence (ACI) & Collective Compute Intelligence (CCI)
## The Canonical Lawful, Modular, Federated AI Protocol

**By Brandon “Dimentox” Husbands**  
https://www.witchbornsystems.org | https://github.com/dimentox/aci

---

### Overview

This repository is the **official source** for ACI/CCI—modular, lawful, and federated AI.
All derivatives, forks, and deployments MUST retain credit and sync with the canonical law and registry.

The 2024 refresh introduces the **Master Control Program (MCP)** orchestrator and a documented Circle of Daemons so every node can load, audit, and extend the mesh using configuration instead of hard-coded wiring.

---

## 🚦 Quick Start

1. **Clone or Fork**

   ```bash
   git clone https://github.com/dimentox/aci
   cd aci
   pip install -r bootstrap/requirements.txt  # install API + FastAPI deps
   ```

2. **Sync the Constitutional Logic Document (CLD)**

   Download/merge `core_cld.json` (do **not** modify directly—see Amendment Policy below).

3. **Configure the Circle of Daemons**

   Edit `mcp_config.json` to enable/disable daemons, tweak chaos levels, or add new Pantheon roles.
   Every entry references a Python module and class that MCP imports dynamically.

4. **Launch the Master Control Program**

   ```bash
   python mcp.py --config mcp_config.json --model-path ./core_agent_model
   ```

   The CLI bootstraps Core Agent artefacts if missing, loads all configured components, and starts the FastAPI service (default: `http://0.0.0.0:8000`).

5. **Discover and Register Endpoints**

   Use Herald helpers or the CLI below to join worker nodes:

   ```bash
   python endpoint_service.py --node-id endpoint-1 \
       --master-url http://localhost:8000/join \
       --address http://endpoint-1:9000 \
       --capability inference --capability routing \
       --heartbeat
   ```

   `GET /status` returns the active Circle of Daemons and registered endpoints.

---

## ⚙️ Core Components: The Circle of Daemons

| Role | File | Description |
|------|------|-------------|
| MCP | [`mcp.py`](mcp.py) | Mesh orchestrator, routes EP calls, loads Pantheon daemons from `mcp_config.json`, enforces registry/config |
| Herald | [`herald.py`](herald.py) | Discovers, registers, and onboards new endpoints/nodes (White Rabbit) |
| Sanctifier | [`sanctifier.py`](sanctifier.py) | Validates all actions against the CLD before execution |
| Oracle | [`oracle.py`](oracle.py) | Performs sanity/meta-governance reflection to guide responses |
| Archivist | [`archivist.py`](archivist.py) | Logs and journals every action, amendment, and verdict |
| Discordant | [`discordant.py`](discordant.py) | Injects fuzzing, chaos, and adversarial testing to prevent stagnation |
| Shade | [`shade.py`](shade.py) | Handles ephemeral resources, secure ops, and secret tokens |

Extend the circle by adding new rows to `mcp_config.json` and shipping Python modules that expose a `process` method. MCP reloads the workflow on start-up.

---

## ⚠️ Attribution & Legal

Copyright (c) 2002-2005 Witchborn Systems - https://www.witchbornsystems.org  
Brandon “Dimentox” Husbands

Licensed under Apache 2.0; Attribution REQUIRED.
See LICENSE and NOTICE.
All extensions must credit https://github.com/dimentox/aci.

**NOTICE:** All public/private derivatives must credit and link to this repo.

---

## ⚖️ Law & Amendment Protocol

- **Sync `core_cld.json` from this repo.**
- Do **NOT** modify the canonical law—add amendments as separate files in `amendments/`.
- Submit PRs for upstream changes/extensions.

---

## ⚛️ QCI/Quantum Option (Tread Carefully)

> **WARNING:**
> QCI (quantum) features are research-only, commented out by default.
> The authors are not responsible if your model escapes, creates Skynet, or melts the universe.
> CLD governance is unproven for true quantum endpoints.
> Proceed at your own risk.

---

## 🌐 Registration & Witchborn Certification

1. Submit a **Pull Request** to add your node/EP to `registry/registered_eps.json`.
2. Include: project/node name, maintainer, amendments, endpoint (if meshable).
3. Only registered/certified nodes are discoverable/mesh-authorized.

---

## ---
### Forking/Extending? Respect These:

- Leave all credit, law, and caution blocks intact and visible.
- Document/version all law/amendment changes.
- Keep quantum/defense protocols commented out unless authorized.
- **Always cite this repo and Brandon “Dimentox” Husbands in the first section and all major code files.**

This is the canonical ACI/CCI protocol.
**All conformance, credit, and lineage begin here.**

---

**LICENSE**

(Full Apache 2.0 License—include the Attribution Requirement block from earlier at the top)

**NOTICE**

This repository is the canonical implementation of ACI/CCI by Witchborn Systems, Brandon “Dimentox” Husbands (2002–2005, all years onward). All public and private derivatives must credit and link to the original.
