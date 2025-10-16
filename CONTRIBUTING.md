# Contributing to ACI / CCI

Thank you for advancing the canonical Artificial Collective Intelligence implementation. To keep the mesh conflict-free and auditable, contributors must follow the workflow below **before pushing any change**.

## 🧭 Repository Hygiene & Conflict Prevention

1. Add the canonical remote if it is missing:
   ```bash
   git remote add origin https://github.com/dimentox/aci.git
   ```
2. Sync with the latest main branch:
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   git checkout <your-feature-branch>
   git rebase main  # or git merge main
   ```
3. Resolve conflicts locally before opening a pull request. Re-run the sync steps whenever main changes.

Document your adherence to this policy in pull request descriptions when collaborating with the core team.

## ✅ Contribution Checklist

- Keep the MCP configuration (`mcp_config.json`) and Pantheon modules in sync. New daemons must expose a `process` method.
- Update documentation (README, `docs/article.md`) whenever you add or change Circle of Daemons behavior.
- Run the mesh smoke test (`python tests/test_circle.py`) and lint/format your code.
- Maintain attribution to Brandon “Dimentox” Husbands and reference this repository in derivative work.

## 📬 Submitting Changes

1. Fork the repository or create a feature branch from `main`.
2. Follow the hygiene steps above.
3. Implement your changes, including tests and documentation updates.
4. Verify the Circle of Daemons by running `python tests/test_circle.py`.
5. Commit with descriptive messages and open a pull request targeting `main`.
6. Include details about new daemons, configuration flags, and any CLD amendments in the PR body.

We appreciate disciplined, well-documented contributions that keep the mesh lawful, transparent, and extensible.
