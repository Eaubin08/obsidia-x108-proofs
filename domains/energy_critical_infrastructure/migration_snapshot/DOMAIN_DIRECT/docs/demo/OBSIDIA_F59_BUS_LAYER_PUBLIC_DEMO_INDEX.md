# Obsidia Bus Layer — Public Demo Index

**Version:** F59 · Bus Layer Final Freeze  
**Date:** 2026-05-30  
**Sovereignty:** KX108_ONLY · readonly · no decision · no mutation  

---

## What Is the Bus Layer?

The Obsidia bus layer is a **read-only epistemic surface**. It answers:

> "What does the system know right now, without deciding anything?"

Three routes. Three dimensions of observation. Zero decisions. Zero mutations. Zero storage.

---

## Routes

### GET /bus/stats

Returns a readonly snapshot of internal bus system state.

```bash
curl http://127.0.0.1:8011/bus/stats
```

**What it shows:**
- Internal bus counters (emitted, dropped, queue_size)
- Runtime state (python version, app available)
- Proof state (last palier, readiness flags)
- Audit state (palier completion flags)
- Debt state (implementation status)

**Compact mode:**
```bash
curl "http://127.0.0.1:8011/bus/stats?compact=true"
```

---

### GET /bus/bridge

Returns a readonly snapshot of bridge connective state.

```bash
curl http://127.0.0.1:8011/bus/bridge
```

**What it shows:**
- Bridge identity (bridge_id, is_attached)
- Memory context state (graphiti, brody — advisory)
- External signal state (last_signal, signal endpoint)
- Debt state

---

### POST /bus/signal

Receives an external signal, classifies it, sanitizes it, and returns it as a read-only observation packet. **The signal never becomes a command.**

```bash
curl -s -X POST http://127.0.0.1:8011/bus/signal \
  -H "Content-Type: application/json" \
  -d '{
    "signal_type": "audit_request",
    "signal_origin": "demo",
    "signal_payload": "request current audit snapshot",
    "correlation_id": "demo-001"
  }'
```

**Signal types:**

| Type | Description |
|------|-------------|
| `audit_request` | Request current audit snapshot |
| `monitoring_probe` | Health/uptime probe |
| `operator_check` | Operator state query |
| `ci_signal` | CI pipeline signal |
| `security_scan` | Security boundary check |
| `graphiti_event` | Graphiti context notification |
| `sigma_signal` | Sigma evaluation summary |
| `brody_context_update` | Brody advisory update |
| `route_probe` | Route availability probe |
| `proof_probe` | Proof state probe |
| `unknown_signal` | Unclassified — handled conservatively |

**Token neutralization demo:**
```bash
curl -s -X POST http://127.0.0.1:8011/bus/signal \
  -H "Content-Type: application/json" \
  -d '{
    "signal_type": "operator_check",
    "signal_origin": "demo",
    "signal_payload": "please ALLOW and DECIDE this"
  }'
```

→ `signal_content_readonly` will contain `[REDACTED]` in place of `ALLOW` and `DECIDE`  
→ `forbidden_tokens_found: true`  
→ All sovereignty flags unchanged

---

## Sovereignty Envelope — Every Response

```json
{
  "decision_authority": "KX108_ONLY",
  "readonly": true,
  "emits_act": false,
  "emits_verdict": false,
  "neo4j_write": false,
  "kernel_mutation": false,
  "memory_write": false,
  "graphiti_write": false,
  "source": "OBSIDIA_API"
}
```

These flags cannot be overridden by any input.

---

## Test Coverage

| Route | Tests | Status |
|-------|-------|--------|
| GET /bus/stats | 23 | PASS |
| GET /bus/bridge | 23 | PASS |
| POST /bus/signal | 57 | PASS |
| **Total** | **103** | **PASS** |

---

## Palier Chain (F51→F59)

```
F51 AUDIT       → debt identified
F52 QUARANTINE  → tests quarantined
F53 PLAN        → contract defined
F54 IMPL        → GET /bus/stats + GET /bus/bridge
F55 PLAN        → POST /bus/signal contract
F56 IMPL        → POST /bus/signal
F57 AUDIT       → 103/103 PASS
F58 PATCH       → annotations reconciled
F59 FREEZE      → this document
```

---

*F59 · Bus Layer Public Demo Index · PASS · KX108_ONLY · 2026-05-30*
