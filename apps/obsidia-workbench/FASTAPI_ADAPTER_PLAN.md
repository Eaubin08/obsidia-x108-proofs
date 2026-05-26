# FastAPI Adapter Plan

**Date:** 2026-05-19
**Target location:** `obsidia-x108-proofs/apps/obsidia-api/`
**Status:** PLAN ONLY — do not create backend without explicit user request

---

## Proposed structure

```
apps/
  obsidia-api/
    main.py          # FastAPI app + CORS
    routers/
      status.py      # GET /api/status, /health
      brody.py       # POST /api/brody/chat
      context.py     # GET /api/context, POST /api/context/from-ir
      graphiti.py    # GET /api/graphiti/status (proxy to ObsidiaShell)
      os3.py         # GET /api/os3/tickets
      gencoin.py     # GET /api/gencoin/ledger
      worldcalls.py  # GET /api/worldcalls
      blockchain.py  # GET /api/blockchain/status
      audit.py       # GET /api/audit/events
      os_trad.py     # POST /api/os-trad/translate
      ir.py          # POST /api/ir/candidate
      os_reverse.py  # POST /api/os-reverse/project
      alphabet.py    # GET /api/alphabet/units
    deps.py          # Shared dependencies (kernel boundary check)
    .venv/           # Python env
    requirements.txt
```

---

## Key routes

### Core

```
GET  /api/status
  → KernelStatus: id, status, readonly, tests_passing, protected_files_clean

GET  /health
  → ApiHealthResponse: status, gateway, version, timestamp, services

POST /api/brody/chat
  Body: { query: str, language: str, context_refs: list[str] }
  → BrodyResponse: response, readonly=true, advisory_only=true, emits_act=false,
                   memory_write=false, decision_authority=X108_ONLY
```

### Context + Graphiti

```
GET  /api/context?q=...&limit=10
  → ContextPacket (readonly, context_signal_only=true)

GET  /api/graphiti/status
  → proxy to ObsidiaShell 8011/graph/v20/frozen/status
```

### OS3 / Gencoin / WorldCalls

```
GET  /api/os3/tickets
  → list[OS3ProofTicket] (readonly)

GET  /api/gencoin/ledger
  → list[GencoinEntry] (ledger_only=true, is_real_token=false)

GET  /api/worldcalls
  → list[WorldCallEvent] (dry_run_only=true)

GET  /api/blockchain/status
  → { chain_action_allowed: false, wallet_signing: false }
```

### OS Trad / IR / OS Reverse

```
POST /api/os-trad/translate
  Body: { text: str, session_language: str }
  → TranslationTrace (readonly, allowed_to_decide=false, mode=LIVE)
  Maps to: periphery/language/language_router.py + new os_trad module

POST /api/ir/candidate
  Body: { text: str, alphabet_units: list }
  → IRCandidate (allowed_to_decide=false, allowed_to_act=false, decision_authority=X108_ONLY)
  Maps to: new periphery/ir module

POST /api/os-reverse/project
  Body: { ir_candidate_id: str, language: str }
  → { projection: str, advisory_only: true, can_emit_act: false }
  Maps to: periphery/reverse_os/action_projection_readonly.py

GET  /api/alphabet/units?text=...
  → list[AlphabetUnit] (symbolic tokenization, read-only)
  Maps to: new periphery/alphabet module

POST /api/context/from-ir
  Body: { ir_candidate_id: str, query: str }
  → ContextPacket (readonly, context_signal_only=true)
  Maps to: periphery/context/context_packet_builder_v2.py
```

### Audit

```
GET  /api/audit/events
  → list[AuditEvent] (append-only, read-only replay)
```

---

## All routes — sovereignty constraints

| Constraint | Status |
|-----------|--------|
| All endpoints read-only or dry-run | ✓ |
| No memory write endpoint | ✓ |
| No kernel mutation endpoint | ✓ |
| No wallet/chain endpoint | ✓ |
| No ACT emission endpoint | ✓ |
| decision_authority = KX108_ONLY | ✓ |
| CORS: allow_origins=["*"] for local dev | ✓ |

---

## Launch command (future)

```bash
cd apps/obsidia-api
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Then in `.env.local` of workbench:
```
VITE_ENGINE_API_BASE=http://127.0.0.1:8000
VITE_USE_MOCK_FALLBACK=false
```
