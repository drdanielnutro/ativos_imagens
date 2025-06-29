# AGENTS.md (root)

> **Audience:** any Codex/Gemini/Claude agent or human contributor that operates at the repository root.
>
> **Goal:** describe *where* agents may act and *which checks* must pass **before** proposing a patch or opening a PR.

---

## 1  Scope

| Path / Pattern               | Permission   | Notes                                     |
| ---------------------------- | ------------ | ----------------------------------------- |
| `/src/**`, `/tests/**`       | ✅ EDIT       | main application & unit/integration tests |
| `*.md`, `/docs/**`           | ⚠️ EDIT       | keep docs concise; no large media embeds  |
| `/data/**`, `*.csv`, `*.png` | ❌ READ‑ONLY  | production data & binary assets           |
| Files > 1 MB                 | ❌ PROHIBITED | commit history must stay lightweight      |

*Deeper* AGENTS.md files override these rules for their subtree.

---

## 2  Environment

```bash
# 🔒 Pin the sandbox Python version
CODEX_ENV_PYTHON_VERSION=3.11
```

Agents must run in **network‑disabled mode** unless the AGENTS.md inside that subtree explicitly allows network calls.

---

## 3  Setup pipeline (MUST succeed)

Agents **must** execute the steps below **locally** and only submit a patch when every command exits with `0`.

```bash
# 1. Self‑contained bootstrap
./setup.sh          # installs Poetry/venv, ADK, Replicate, etc.

# 2. Static analysis
ruff check .        # lint (PEP 8 + Ruff rules)
mypy src            # type‑checking

# 3. Tests
pytest -q --disable-warnings
```

> ✅ If all steps turn green, the patch may be submitted.
> ❌ If *any* step fails, the agent **must** fix the code and retry.

---

## 4  Style & Conventions

* Black formatting (PEP 8 default line length = 88).
* Typing mandatory for all new/edited functions.
* Commit messages: `<type>(<scope>): <subject>` (Conventional Commits).

---

## 5  DO NOT

* alter git history (no force‑push),
* commit secrets (.env, tokens, certificates),
* exceed API rate‑limits,
* generate Lottie JSONs > 500 kB without prior compression.

---

## 6  Useful snippets

```bash
# Run a local web server (if needed)
poetry run python -m http.server 8000
```

---

> **Remember:** explicit instructions in a task prompt overrule AGENTS.md. When in doubt, ask for clarification instead of guessing.