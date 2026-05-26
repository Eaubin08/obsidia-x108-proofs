# BRODY OUTPUT PRINCIPLE EXTENSION AUDIT

> **Mode**: AUDIT ONLY — no functional patches applied.
> **Date**: 2026-05-22
> **Reference**: `/api/brody/chat` stabilized at `BRODY_HTTP_UTF8_PAYLOAD_PACKETIZATION_V1_PASS` (82 tests, 0 failures)
> **Principle**: *The engine produces. The envelope transports.*

---

## 1. Canonical Reference — `/api/brody/chat`

The Brody endpoint validates a complete output contract:

### Pipeline (in order)
```
mémoire / contexte
→ Reverse OS
→ OS Trad
→ langage universel  
→ true response structure
→ final_answer
→ last-mile UTF-8 repair      (_last_mile_brody_utf8_repair)
→ compact/debug packetization (_compact_brody_payload)
→ JSONResponse (charset=utf-8)
```

### Contract packets

| Packet | Fields | Brody status |
|---|---|---|
| **A. Response** | `final_answer`, `response`, `response_md`, `topic`, `final_answer_source`, `language`, `timestamp`, `source` | Present |
| **B. Boundary** | `decision_authority=KX108_ONLY`, `emits_act=false`, `memory_write=false`, `graphiti_write=false`, `neo4j_write=false`, `kernel_mutation=false`, `readonly=true` | Present |
| **C. Debug** | snapshots, `context_packet`, `audit_event`, `memory_response_chain_snapshot`, `brody_full_context`, `runtime_context`, `true_voice_snapshot`, `temporal_context_snapshot` | Opt-in (`debug=true`) |
| **D. Evidence** | `graphiti_status`, `neo4j_status`, proof markers, `deep_snapshots_omitted`, `deep_snapshots_available` | Present |

### Mode control
- `compact=true` → light payload (core fields only, 28 deep snapshots omitted)
- `debug=true` → full payload (all snapshots + diagnostic markers)
- Default → backward-compatible (snapshots present, debug markers stripped)

---

## 2. Route Cartography

### Legend

| Column | Meaning |
|---|---|
| **Mélange response/debug** | Are user-facing text fields mixed with internal snapshots/logs? |
| **Payload lourd** | Does the endpoint return large nested dicts unconditionally? |
| **Boundary flags** | Are `decision_authority`, write flags explicitly returned? |
| **Compact/debug** | Does the endpoint support mode switching? |
| **UTF-8 repair** | Is last-mile UTF-8 mojibake repair applied? |

### Table

| Route / Fichier | Type de sortie | Mélange response/debug | Payload lourd | Boundary flags | Compact/debug | UTF-8 repair | Risque | Recommandation |
|---|---|---|---|---|---|---|---|---|
| `brody.py` `/api/brody/chat` | Chat response | Non (via compact/debug) | Oui (défaut) | Oui | Oui | Oui | — | **RÉFÉRENCE** |
| `status.py` `/api/status` | Status JSON | Non | Non | Oui (via safe_backend_response) | Non | Non | LOW | SAFE_NOW |
| `status.py` `/api/x108/status` | Status JSON | Non | Non | Oui (inline invariants) | Non | Non | LOW | SAFE_NOW |
| `x108.py` `/api/x108/*` | Math/cognitive | Non | Variable | Oui (`_BOUNDARY` sur chaque return) | Non | Non | LOW | SAFE_NOW |
| `blockchain.py` `/api/blockchain/*` | Blockchain ops | Non | Oui (fraud-check) | Oui (`_BOUNDARY`) | Non | Non | MEDIUM | NEEDS_ENVELOPE |
| `periphery_ops.py` `/api/periphery/*` | Pipeline ops | Non | Oui (multi-gate) | Oui (`_BOUNDARY`) | Non | Non | MEDIUM | NEEDS_ENVELOPE |
| `brody_monitoring.py` `/api/periphery/monitoring/*` | Monitoring | Non | Oui (CLI registry) | Oui (`_BOUNDARY`) | Non | Non | LOW | SAFE_NOW |
| `memory.py` `/api/memory/*` | Memory status | Non | Non | Oui (inline flags) | Non | Non | LOW | SAFE_NOW |
| `graphiti.py` `/api/graphiti/*` | Graphiti proxy | Non | Non | Oui (inline flags) | Non | Non | LOW | SAFE_NOW |
| `gencoin.py` `/api/gencoin` | Ledger | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `os3.py` `/api/os3/*` | Proof tickets | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `worldcalls.py` `/api/worldcalls/*` | WorldCalls stub | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `audit.py` `/api/audit/*` | Audit events | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `translation.py` `/api/translation/trace` | Translation trace | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `context.py` `/api/context/from-message` | Context builder | Non | Non | Non (relies on wrapper) | Non | Non | LOW | SAFE_NOW |
| `main.py` `/bus/stats` | Bus diagnostic | **Oui** (raw broker stats + bridge snapshot) | Non | Non (raw dict) | Non | Non | **MEDIUM** | NEEDS_ENVELOPE |
| `main.py` `/bus/bridge` | Bridge snapshot | **Oui** (raw bridge internals) | Non | Non (raw dict) | Non | Non | MEDIUM | NEEDS_ENVELOPE |
| `main.py` `/bus/health` | Bus health | Non | Non | Partiel (KX108_ONLY only) | Non | Non | LOW | SAFE_NOW |

---

## 3. Gap Detection

### 3.1 Snapshot leaks in response fields

**Found in**: `main.py` `/bus/stats`, `/bus/bridge`
- `brody_context`, `sigma_counters`, `bridge_snapshot` returned as top-level keys
- No separation between user-facing response and internal debug
- **Risk**: Exposes internal counter state to any HTTP client

### 3.2 Absence of compact/debug in non-Brody endpoints

**All routes except `brody.py`**: No compact/debug mode switching.
- Heavy payloads (e.g., `blockchain_classifiers_fraud_check` returns ~8 nested dicts) delivered unconditionally
- No way for client to request light vs full payload
- **Risk**: Unnecessary bandwidth, exposes internal structure

### 3.3 Absence of UTF-8 last-mile repair

**All routes except `brody.py`**: No `_last_mile_brody_utf8_repair` applied.
- `safe_backend_response` does NOT apply UTF-8 repair on string fields
- If peripheral modules return mojibake text, it passes through to the client
- **Risk**: Moji bake could appear in any endpoint that returns French text

### 3.4 Boundary flags inconsistency

- `x108.py`, `blockchain.py`, `periphery_ops.py`, `brody_monitoring.py`: Use local `_BOUNDARY` dict (consistent)
- `status.py`, `memory.py`, `graphiti.py`: Write flags inline (consistent but verbose)
- `gencoin.py`, `os3.py`, `worldcalls.py`, `audit.py`, `translation.py`, `context.py`: Rely on `safe_backend_response` defaults (adds boundary automatically — acceptable)
- `main.py` bus endpoints: Raw dict, no boundary wrapping
- **Risk**: Bus endpoints leak internal state without sovereignty guard

### 3.5 No standardized output envelope

Each route constructs its own return dict independently.
- `safe_backend_response` adds base invariants but no packetization logic
- No shared `OutputEnvelope` class/helper
- No consistent field ordering
- **Risk**: High maintenance burden, inconsistent client contracts

### 3.6 Event bus health endpoints

`/bus/stats` and `/bus/bridge` return internal broker state without:
- Boundary flags
- Decision authority marker
- Readonly assertion
- **Risk**: Information leak of broker internals

---

## 4. Classification

### SAFE_NOW — Already compatible

| Route | Reason |
|---|---|
| `brody.py` `/api/brody/chat` | Full reference implementation |
| `status.py` (all) | Light status endpoints, boundary via wrapper |
| `x108.py` (all) | Local `_BOUNDARY` on every return |
| `brody_monitoring.py` (all) | Local `_BOUNDARY` on every return |
| `memory.py` (all) | Write flags inline |
| `graphiti.py` (all) | Write flags inline |
| `gencoin.py`, `os3.py`, `worldcalls.py`, `audit.py`, `translation.py`, `context.py` | Light stubs, boundary via `safe_backend_response` defaults |
| `main.py` `/bus/health` | Light, has KX108_ONLY |

### NEEDS_ENVELOPE — Should receive an output envelope

| Route | Priority | Gap |
|---|---|---|
| `main.py` `/bus/stats` | HIGH | Raw broker internals exposed, no boundary |
| `main.py` `/bus/bridge` | HIGH | Raw bridge internals exposed, no boundary |
| `blockchain.py` `/api/blockchain/classifiers/fraud-check` | MEDIUM | Heavy payload (~8 nested dicts), no compact/debug |
| `periphery_ops.py` `/api/periphery/pipeline/run` | MEDIUM | Pipeline result could benefit from compact/debug |

### DO_NOT_TOUCH — Requires separate decision

| Target | Reason |
|---|---|
| `x108.py` cognitive/math endpoints | Already well-structured with `_BOUNDARY` |
| `safe_response.py` | Shared by all routes — changing it requires full regression |
| Event bus internals | Architecture decision needed for broker exposure |

---

## 5. Proposed Patch Plan (not applied)

### Phase 1: Shared helper `OutputEnvelopeV1`

Create `apps/obsidia_api/output_envelope.py`:

```python
def build_output_envelope(
    response_data: dict,
    *,
    compact: bool = False,
    debug: bool = False,
    source: str = "REAL_BACKEND",
) -> dict:
    """Standardized output envelope matching Brody contract."""
    # 1. Apply safe_backend_response base
    # 2. Apply last-mile UTF-8 repair on all string fields
    # 3. Apply compact/debug packetization
    # 4. Return enveloped dict
```

**Risk**: LOW — new file, no existing code changed.

### Phase 2: Apply to a non-critical route

Target: `main.py` `/bus/stats` or `/bus/bridge`
- Wrap existing return with `OutputEnvelopeV1`
- Add `compact`/`debug` query params
- Test via existing test suite

**Risk**: LOW — these endpoints are diagnostic-only.

### Phase 3: Extend to blockchain and periphery

Apply `OutputEnvelopeV1` to:
- `blockchain.py` fraud-check endpoint
- `periphery_ops.py` pipeline endpoints
- Add compact/debug support

**Risk**: MEDIUM — these routes have existing Pydantic models that must not break.

### Phase 4: Freeze and regression test

- Run full 82-test battery
- Add compact/debug tests for each converted route
- Verify no boundary regression
- Freeze with git tag

---

## 6. Non-Regression Confirmation

| Check | Status |
|---|---|
| X108 untouched | ✅ |
| sigma/ untouched | ✅ |
| proofs/lean/ untouched | ✅ |
| formal/tla/ untouched | ✅ |
| merkle_seal.json untouched | ✅ |
| Docker untouched | ✅ |
| Neo4j untouched | ✅ |
| No writes activated | ✅ |
| No kernel mutation | ✅ |
| No functional patches applied during audit | ✅ |
| 82 existing tests passing | ✅ |
| protected diff empty | ✅ |

---

## 7. Canonical Phrase

> *On ne simplifie pas le moteur. On applique le principe de paquet déjà validé chez Brody aux frontières de sortie des autres couches.*

---

*Audit completed. 2 HIGH-risk gaps identified (bus endpoints). 2 MEDIUM-risk gaps (heavy payloads without compact/debug). All other routes are SAFE_NOW or rely on `safe_backend_response` defaults that are acceptable.*
