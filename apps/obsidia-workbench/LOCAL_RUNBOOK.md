# Local Runbook — Obsidia Workbench

**Date:** 2026-05-19

---

## Prerequisites

- Node.js >= 18 (confirmed: v24.15.0)
- npm >= 9 (confirmed: v11.12.1)
- Python 3.11+ with `.venv_api8011` in `obsidiashell-main/` for backend

---

## 1. Frontend — First install

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\apps\obsidia-workbench"
npm install
npm run dev
```

Open: http://localhost:5173

The UI works **without any backend** — mock fallback is active by default.

---

## 2. Frontend — Environment config

Create `.env.local` in the workbench root with:

```
VITE_OBSIDIA_API_BASE=http://127.0.0.1:8011
VITE_ENGINE_API_BASE=http://127.0.0.1:8000
VITE_USE_MOCK_FALLBACK=true
VITE_PROBE_TIMEOUT_MS=3000
```

Set `VITE_USE_MOCK_FALLBACK=false` once the backend is running to enable live data.

---

## 3. Backend — ObsidiaShell (port 8011)

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidiashell-main"
.venv_api8011\Scripts\uvicorn obsidia_core.agent_bridge:app `
    --host 127.0.0.1 --port 8011 --reload
```

Health check: http://127.0.0.1:8011/health
Interactive docs: http://127.0.0.1:8011/docs

### Environment variables needed

Copy `.env.obsidiashell.local` (already exists) or set:
```
GRAPHITI_V20_NEO4J_URI=bolt://localhost:7688
GRAPHITI_V20_NEO4J_USER=neo4j
GRAPHITI_V20_NEO4J_PASSWORD=obsidia-graphiti-dev
```

---

## 4. Backend — Engine API (port 8000, optional)

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core"
# Activate appropriate venv, then:
uvicorn engine.api_server.main:app --host 127.0.0.1 --port 8000
```

Note: requires `unified_interface` and `obsidia_kernel` modules in Python path.

---

## 5. Build for production

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\apps\obsidia-workbench"
npm run build
```

Output: `dist/`

---

## 6. Verification checklist

```
FRONTEND_BUILD_PASS         → npm run build exits 0
WORKBENCH_LOCALHOST_READY   → http://localhost:5173 responds
MOCK_FALLBACK_READY         → UI loads without backend
BACKEND_BRIDGE_READY        → BACKEND tab shows status
NO_REAL_ACTION_PASS         → All world calls show dry_run_only=true
```

---

## 7. Sovereignty invariants — always enforced

| Invariant | Value |
|-----------|-------|
| `decision_authority` | `KX108_ONLY` |
| `emits_act` | `false` |
| `memory_write` | `false` |
| `real_chain_action_allowed` | `false` |
| `graphiti_write` | `false` |
| `auto_promotion_allowed` | `false` |
| `Gencoin is real token` | `false` |
