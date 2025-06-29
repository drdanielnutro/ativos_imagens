# AGENTS.md

> **Audience:** agents operating *inside* `ativos_imagens/` — the multi‑agent production pipeline.
>
> **Entry point:** `adk web` (served from this directory).

---

## 1  Scope (overrides root rules for this subtree)

| Path / Pattern                              | Permission  | Notes                                          |
| ------------------------------------------- | ----------- | ---------------------------------------------- |
| `ativos_imagens/**`                         | ✅ EDIT      | all source & tools for asset generation        |
| `ativos_imagens/tools/**`, `assets_temp/**` | ✅ EDIT      | OK to create temp artefacts < 1 MB             |
| `test_multi_agent.py`, `/tests/**`          | ✅ EDIT      | extend tests but **keep them idempotent**      |
| `agente_antigo/**`                          | ❌ READ‑ONLY | legacy reference; do not modify                |
| External network                            | ⚠️ ALLOWED   | network is permitted **only** for ADK/Gemini & |
|                                             |             | Replicate API calls already coded              |

---

## 2  Runtime pipeline (MUST succeed)

```bash
# inside ativos_imagens/
# 1. Bootstrap (inherits root setup)
../../setup.sh

# 2. Unit & integration tests specific to SMA
pytest test_multi_agent.py -q --disable-warnings

# 3. Type‑check only this package
mypy ativos_imagens
```

If **any** step fails, the agent must fix and re‑run before submitting diffs.

---

## 3  Developer / Agent commands

```bash
# Start local web UI for manual QA
adk web  # served at http://127.0.0.1:8000

# Quick inventory report via FunctionTool
awk '/def get_quick_status/' -n ativos_imagens/tools/asset_manager.py
```

---

## 4  Coding standards (ativos\_imagens)

* Respect the abstractions: do **not** bypass `asset_manager` when writing files.
* Keep public functions documented with NumPy‑style docstrings.
* F‑Strings for all string interpolation — no `+` concatenation.

---

## 5  Common pitfalls & guards

| Risk                            | Guard‑rail                                                |
| ------------------------------- | --------------------------------------------------------- |
| API rate‑limit / 429 errors     | exponential back‑off (already implemented; do not remove) |
| Oversize Lottie JSON (> 500 kB) | run `lottie‑programmatic --compress` tool                 |
| Infinite generation loops       | use `MAX_STEPS` constant in orchestrator (keep ≤ 20)      |

---

Happy patching! Keep the pipeline green and the assets flowing. 💚
