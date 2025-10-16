# Artificial Collective Intelligence (ACI) & Collective Compute Intelligence (CCI)
## The Canonical Lawful, Modular, Federated AI Protocol

**By Brandon “Dimentox” Husbands**
https://www.witchbornsystems.org | https://github.com/dimentox/aci

## Canonical Reference

All architectural, naming, and implementation decisions must align with the following source documents (located in `/docs`):

- Artificial_Collective_Intelligence__Beyond_AGI-published.pdf
- THE CCI TESTAMENT1.pdf
- From ACI to CCI A Fractal Offloading Architecture for Distributed Intelligence.md

Any feature or extension diverging from the reference must be clearly marked as “evolutionary” and cite the relevant section/line in the source doc.

---

### Overview

This repository is the **official source** for ACI/CCI—modular, lawful, and federated AI.
All derivatives, forks, and deployments MUST retain credit and sync with the canonical law and registry.

The 2024 refresh introduces the **Master Control Program (MCP)** orchestrator and a documented Circle of Daemons so every node can load, audit, and extend the mesh using configuration instead of hard-coded wiring.

---

## 🚦 Quick Start

### Quickstart: Minimal Reference ACI

1. **Install dependencies**

   ```bash
   git clone https://github.com/dimentox/aci
   cd aci
   pip install -r bootstrap/requirements.txt  # API + FastAPI deps
   ```

2. **Edit `mcp_config.json` (Pantheon daemons enabled)**

   Confirm each Pantheon role is enabled by default and adjust configuration blocks as needed for your deployment.

3. **Start MCP**

   ```bash
   python mcp.py --config mcp_config.json --model-path ./core_agent_model
   ```

4. **All daemons autoloaded; no mesh/federation/registration logic by default**

   The CLI bootstraps Core Agent artefacts if missing, loads every Pantheon daemon, and serves the FastAPI control plane with only the canonical `/` and `/status` endpoints.

Revision: Removed legacy registration/join APIs from the default quickstart; see Evolutionary Extensions for mesh/federation options.

## Evolutionary Extensions

> **Note:** The following mesh federation/registration logic is not part of the minimal ACI reference. It is provided for advanced or federated mesh use only. Reference: From ACI to CCI, Section: Fractal Offloading.

### Evolutionary Extension: Mesh Federation & Endpoint Registration

- Enable federation by setting `"features.mesh_registration.enabled": true` in `mcp_config.json`. The config includes the note `"The following are evolutionary/experimental mesh features. See: From ACI to CCI..."` to highlight its non-canonical status.
- Restart MCP after changing the configuration. When enabled, `/join`, `/nodes`, and `/heartbeat` routes are exposed and logged as evolutionary extensions.
- Optionally run the helper CLI:

  ```bash
  python endpoint_service.py --node-id endpoint-1 \
      --master-url http://localhost:8000/join \
      --address http://endpoint-1:9000 \
      --capability inference --capability routing \
      --heartbeat
  ```

  The helper is marked with the same evolutionary reference and should only be used when the mesh extension is activated.

### Witchborn Certification & Registry (Evolutionary)

1. Submit a **Pull Request** to add your node/EP to `registry/registered_eps.json`.
2. Include: project/node name, maintainer, amendments, endpoint (if meshable).
3. Only registered/certified nodes are discoverable/mesh-authorized when the evolutionary federation layer is enabled.

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
