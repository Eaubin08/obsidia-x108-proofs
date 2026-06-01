# Deferred Phases - Obsidia X-108

> Source: `docs/status/DEFERRED_PHASES_REPORT.md` | Date: 2026-05-30

The following modules and phases are explicitly deferred. They are not claimed as implemented. This declaration is required for honest external communication.

## BLOCKCHAIN_SECURITY_LAYER

**Status:** MISSING

All modules, schemas, documentation, tests - none created yet.
Requires Phase 1.

## NUMBER_ENCODING_SANDBOX

**Status:** MISSING

Radix systems, symbolic encoder, entropy, compression, crypto boundary, diffusion cost.
Requires Phase 2.

## SYMBOLIC_PHYSICS_BOUNDARY

**Status:** MISSING

Dimensional hygiene, frequency tag, physics claim gate, unit checker.
Requires Phase 3.

## COGNITIVE_TREES_34_MEMORY_WORLD

**Status:** MISSING

Tree registry (34 trees), activation vector, dominant trees, Shazam Cognitif, memory-world mapper.
Requires Phase 4.

## REVERSE_OS_BDF_HEXAFLUX

**Status:** MISSING

Audience projection, format projection, double brain router, LLM diffusion mix, transition mapper, LTCU+.
Requires Phase 5.

## CONSCIOUSNESS_REGIME_SANDBOX

**Status:** MISSING

Regime classifier, pass/fail metrics, collective sandbox summary.

**Hard constraint:** `STATUS=SANDBOX_ONLY, NO_CONSCIOUSNESS_CLAIM`. This phase must never assert consciousness.
Requires Phase 6.

## AGENTIC_CONSTITUTIONAL_DOCS

**Status:** MISSING

Civilisation stack docs, capability-is-not-authority, cognition-to-action governance.
Requires Phase 8.

## MEMORY_BRODY_GRAPHITI_STABILIZATION

**Status:** PARTIAL

Existing:
- `periphery/feedback_memory_bridge_brody_readonly.py` - base present
- `periphery/brody_memory_readonly/` - legacy readonly directory present
- `periphery/context/context_packet_builder.py` - base present
- `periphery/x108_ingress/readonly_context_ingress.py` - base present

Missing:
- `periphery/memory/`
- `periphery/brody/`
- `periphery/graphiti/`
- `periphery/interface/`

Requires Phase 7.

---

## Formal proof targets (FUTURE_FORMAL_TARGET)

The following properties are validated by Python tests today and are explicitly marked as future formal proof targets:

| Property | Current status | Future target |
|---|---|---|
| Sigma layer sovereignty | PYTHON_TEST_ONLY | `proofs/lean/Obsidia/SigmaReadonly.lean` |
| Bus bridge sovereignty | PYTHON_TEST_ONLY | `proofs/lean/Obsidia/BusBridgeReadonly.lean` |
| `graphiti_write=False` formally | PYTHON_TEST_ONLY | `proofs/lean/Obsidia/GraphitiReadonly.lean` |

---

## Security items deferred to F76c

| Item | Priority | Reason |
|---|---|---|
| Auth on `POST /api/x108/*` | P1 | Requires route analysis before protection |
| Redis-backed rate limit | P2 | Only if horizontal scaling required |
| Structured access logs | P2 | Audit middleware present, enrichment deferred |

---

_Obsidia X-108 Deferred Phases | 2026-05-30 | KX108_ONLY | No commit / No push_

