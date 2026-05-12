# BRODY SESSION MEMORY LEDGER READONLY V2

Status: peripheral readonly ledger.

Role:
- capture Brody terminal exchanges
- write JSONL session trace
- write per-turn JSON and MD records
- maintain hash chain
- keep session evidence local

Boundary:
- no decision
- no ACT
- no ALLOW/HOLD/BLOCK verdict authority
- no kernel mutation
- no X108 runtime binding
- no X108 merge
- no Graphiti write
- no auto-triage yet

Next intended palier:
BUILD_BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_V1
