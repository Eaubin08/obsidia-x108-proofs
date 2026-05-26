# Obsidia X-108 Workbench

A governed, read-only interface for the Obsidia X-108 governance kernel.
ChatGPT-like UX — but every response is advisory, every action is dry-run, and X-108 decides.

---

## Quick start

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\apps\obsidia-workbench"
npm install
npm run dev
# → http://localhost:5173
```

Works offline — mock fallback is always active.

---

## Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOP BAR: KERNEL: X-108 [ACTIVE]  READONLY  397 TESTS PASS         │
├──────────────┬──────────────────────────────┬───────────────────────┤
│ LEFT SIDEBAR │  BRODY CHAT (main)           │  RIGHT PANEL (tabs)   │
│              │  ─────────────────────────── │  ─────────────────── │
│ Sessions     │  [ADVISORY ONLY]             │  CONTEXT              │
│ Memory Srcs  │  Brody: context signal only  │  GOV                  │
│ Mode         │  emits_act=false             │  MEMORY               │
│ Invariant    │  memory_write=false          │  GENCOIN              │
│ Badges       │  decision_authority=KX108    │  AUDIT                │
│              │                              │  BACKEND              │
└──────────────┴──────────────────────────────┴───────────────────────┘
```

---

## Panels

| Panel | Content |
|-------|---------|
| **CONTEXT** | Context packet V2 — all sovereignty fields, dominant trees |
| **GOV** | OS3 proof ticket, SovereignTicket, WorldCall/Gateway dry-run |
| **MEMORY** | Memory candidates (human review required), Graphiti status |
| **GENCOIN** | Ledger entries — not a real token, post-proof only |
| **AUDIT** | Append-only WorldActionBus trace |
| **BACKEND** | Live probe: ObsidiaShell (8011), Engine API (8000), invariants |

---

## Governance invariants (always enforced)

| Invariant | Value |
|-----------|-------|
| `decision_authority` | `KX108_ONLY` |
| `Brody emits_act` | `false` |
| `memory_write` | `false` |
| `auto_promotion_allowed` | `false` |
| `graphiti_write` | `false` |
| `real_chain_action_allowed` | `false` |
| `Gencoin is_real_token` | `false` |
| `WorldAction dry_run_only` | `true` |

---

## Backend (optional)

The workbench runs fully in mock mode. To connect live data:

```powershell
# ObsidiaShell (port 8011):
cd obsidiashell-main
.venv_api8011\Scripts\uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011

# Then set in .env.local:
VITE_USE_MOCK_FALLBACK=false
```

See `LOCAL_RUNBOOK.md` for full setup.

---

## Files

```
src/
  api/
    obsidiaClient.ts    Main API client (safeFetch + mock fallback)
    contracts.ts        TypeScript types for API responses
    mockFallback.ts     Fallback mock values
  components/
    TopBar.tsx          Kernel status bar
    LeftSidebar.tsx     Sessions, memory sources, invariant badges
    BrodyPanel.tsx      Main chat panel
    RightPanel.tsx      Tabbed governance panels
    BackendStatusPanel.tsx  Live backend probe
  data/mockData.ts      All mock data (sovereignty-invariant)
  types/obsidia.ts      Domain types

BACKEND_DISCOVERY_REPORT.md
FRONTEND_BACKEND_BRIDGE_REPORT.md
LOCAL_RUNBOOK.md
```
