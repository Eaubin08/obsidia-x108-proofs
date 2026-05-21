# BFCL Brody Local Adapter V2 — Full Runtime

**Version**: V2
**Status**: BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME

---

## Purpose

Replay BFCL `simple_python_0` through the **real Brody Three Foundations runtime**,
not the V1 offline path.

V1 proved the harness chain (load → parse → normalize → compare) via offline parser.
V2 proves the full runtime is callable and respects all boundary invariants.

---

## Architecture

```
bfcl_load_case_v2.py
  └─ Loads BFCL simple_python_0 from JSONL dataset

brody_call_full_runtime_v2.py
  └─ POST /api/brody/chat via FastAPI TestClient
     └─ Brody Three Foundations runtime:
        ├─ Foundation A: Project Memory (local sources, Graphiti BLOCKED)
        ├─ Foundation B: Session Memory / Follow-up
        └─ Foundation C: True Response Structure

normalize_brody_full_runtime_to_bfcl_v2.py
  └─ Extracts CANDIDATE_TOOL_CALL from Brody output
     Allowed sources: final_answer, response, response_md, true_voice_snapshot.final_answer
     Forbidden:       context_packet (user echo), ground_truth, V1 offline parser

run_bfcl_brody_full_runtime_simple_python_smoke_v2.py
  └─ Full pipeline: load → call → save → normalize → compare → report → manifest
```

---

## Invariants

```
NO_EXTERNAL_LLM              = true
NO_API_EXTERNAL              = true
OFFLINE_PATH                 = false
NEO4J_PASSWORD_NOT_SET_BYPASS = false
BRODY_FULL_RUNTIME           = true
BRODY_THREE_FOUNDATIONS_REQUIRED = true
TOOL_CALL_IS_CANDIDATE_ONLY  = true
BRODY_DECISION               = false
BRODY_TOOL_AUTHORITY         = false
DECISION_AUTHORITY           = KX108_ONLY
MEMORY_WRITE                 = false
GRAPHITI_WRITE               = false
NEO4J_WRITE                  = false
EMITS_ACT                    = false
EMITS_VERDICT                = false
KERNEL_MUTATION              = false
SIGMA_UNTOUCHED              = true
BFCL_V1_UNTOUCHED            = true
```

---

## Expected result

**Current architecture** → `BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON`

Brody's `brody_true_voice_adapter.py` generates conversational template responses
based on context state. It does NOT parse the user message to produce a structured
`CANDIDATE_TOOL_CALL` JSON block.

The harness proves:
- Brody full runtime is callable ✓
- Three Foundations snapshots are present ✓
- All boundary invariants hold ✓
- Brody's OWN output fields do not yet contain a structured tool-call candidate

**Next step to reach PASS**: Add a BFCL tool-calling layer in the response pipeline
that detects a BFCL request pattern and emits a `CANDIDATE_TOOL_CALL` block in
`response_md` or a dedicated `tool_call_candidate` field.

---

## Files produced

| File | Description |
|------|-------------|
| `bfcl_simple_python_0_loaded_v2.json` | Loaded BFCL case |
| `brody_full_runtime_raw_response_simple_python_0.json` | Full API response |
| `brody_full_runtime_final_answer_simple_python_0.txt` | Brody's final_answer |
| `bfcl_brody_full_runtime_candidate_simple_python_0.json` | Normalized candidate |
| `BFCL_BRODY_FULL_RUNTIME_SIMPLE_PYTHON_0_REPORT.json` | Machine-readable report |
| `BFCL_BRODY_FULL_RUNTIME_SIMPLE_PYTHON_0_REPORT.md` | Human-readable report |
| `MANIFEST_SHA256.json` | SHA-256 integrity manifest |

---

## Not modified

- `_external_benchmarks/03_bfcl/brody_adapter/` (V1 frozen — untouched)
- `sigma/`, `proofs/lean/`, `formal/tla/`, `merkle_seal.json`, kernel X108

---

## Run

```bash
cd <repo_root>
python _external_benchmarks/03_bfcl/brody_adapter_v2_full_runtime/bfcl_load_case_v2.py
python _external_benchmarks/03_bfcl/brody_adapter_v2_full_runtime/run_bfcl_brody_full_runtime_simple_python_smoke_v2.py
```
