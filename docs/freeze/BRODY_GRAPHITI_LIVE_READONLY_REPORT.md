# Brody Graphiti Live Bootstrap Report

**Date:** 2026-05-19
**Status:** GRAPHITI_LIVE_BLOCKED_WITH_EXACT_REASON_PASS

---

## Probe Results

| Check | Result |
|-------|--------|
| NEO4J_URI | **NOT SET** (env var absent) |
| NEO4J_USER | **NOT SET** (env var absent) |
| NEO4J_PASSWORD | **NOT SET** (env var absent) |
| NEO4J_DATABASE | **NOT SET** (env var absent) |
| Port 7688 (Neo4j Bolt) | **CLOSED** |
| Port 8011 (ObsidiaShell) | **CLOSED** |
| neo4j Python driver | INSTALLED |

## Exact Blocker

```
BLOCKER: NEO4J_URI not set | NEO4J_PASSWORD not set | Neo4j port 7688 closed | ObsidiaShell port 8011 closed
```

## Run Command to Enable Graphiti

```powershell
# 1. Set Neo4j credentials
$env:NEO4J_URI="bolt://localhost:7688"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="your_password"
$env:NEO4J_DATABASE="neo4j"

# 2. Start Neo4j server (if installed)
neo4j start

# 3. Start ObsidiaShell (if obsidiashell-main exists)
cd obsidiashell-main
.venv_api8011\Scripts\uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011
```

## Current Runtime Mode

With Graphiti offline, the full orchestrator runs in `REAL_BRODY_RUNTIME_NO_GRAPHITI` mode:
- Terminal Structural Dialogue: ACTIVE (build_response fallback)
- Local Response Engine: LOADED (available as fallback)
- Content Hydration: LOADED (ready)
- Context Packet Query: LOADED (query_neo4j unavailable — no credentials)
- Memory modules: LOADED (but DISABLED by default flags)
- Graphiti manual-apply chain: LOADED_BUT_GRAPHITI_OFFLINE

## Modules Available (46 Python runtimes)

All 46 brody_memory_readonly Python files verified present on disk. All carry DECISION_AUTHORITY=KX108_ONLY in their pointer files. The orchestrator loads 13 modules for runtime status reporting.

## Status

**Not PASS** — Graphiti is definitively blocked by missing credentials and closed ports. This is an infrastructure dependency, not a code gap. The full Brody runtime operates correctly in NO_GRAPHITI mode with explicit blocker reporting.
