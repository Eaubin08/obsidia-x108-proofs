OBSIDIA V18.3 FINAL — SEALED FREEZE

Timestamp: 2026-03-03T14:17:34.102216Z

What this is:
- A single, buildable, non-embedded (no zip-in-zip) sealed package combining:
  1) Fortress proofs (V18)    -> ./fortress_v18/
  2) Buildable engine (0.9.3.1 FLAT) -> ./engine_buildable_0_9_3_1/
  3) Seal verifier + master manifest

Core invariants covered (static presence verified):
- /v1/decision endpoint exists
- enforce_auth present (API non-bypass)
- append_audit present (append-only audit chain)
- X108 uses time_elapsed wiring

How to verify seal:
- python seal_verify.py   (PASS expected)

How to run engine (from engine dir):
- python entrypoint.py
- python -m pytest -q tests_fusion/test_fusion_F01_F04.py


---
ROOT HASH (A2 seal):
- python root_hash_verify.py   (PASS expected)
- See ROOT_HASH_V18_3.txt and SEAL_META_V18_3.json
