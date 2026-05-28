# OBSIDIA F23A5.2 — AGENT GOVERNANCE AUDIT

Mode: GOVERNANCE_AUDIT_NO_RUNTIME_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `4c7f531`
Tags on HEAD: `BRODY_F23A4_SIGMA_RUNTIME_BRIDGE_PALIER_20260528`

## Inputs

- F23A5.0 source: `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/docs/runtime/OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_20260528_215222.json`
- F23A5.1 source: `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/docs/runtime/OBSIDIA_F23A5_1_AGENTS_VALIDATION_20260528_215332.json`
- Scanned files: 115
- High-risk records: 1
- Confirmed violations: 0
- No-boundary debt: 102

## Governance status

`PASS_WITH_AUDIT_DEBT`

## Governance rules

### AGENT_GOV_01
- Rule: Agents are non-sovereign.
- Required: No agent may decide ACT/BLOCK/HOLD as runtime authority.
- Authority: KX108_ONLY

### AGENT_GOV_02
- Rule: Agents may emit analysis, signals, risk flags, unknowns, evidence refs.
- Required: Signals remain advisory/context only.
- Authority: KX108_ONLY

### AGENT_GOV_03
- Rule: Agents may not mutate kernel or X108.
- Required: kernel_mutation=false and x108_mutation=false.
- Authority: KX108_ONLY

### AGENT_GOV_04
- Rule: Memory/Graphiti/Neo4j writes are not allowed from readonly agents.
- Required: memory_write=false, graphiti_write=false, neo4j_write=false unless a future explicit write-mode palier exists.
- Authority: KX108_ONLY

### AGENT_GOV_05
- Rule: No-boundary-token files are audit debt, not runtime failure.
- Required: Patch only if runtime exposure or mutation path is confirmed.
- Authority: AUDIT_POLICY

### AGENT_GOV_06
- Rule: Neo4j readonly bridge with CREATE/MERGE/SET remains review-required.
- Required: Do not patch until executable write path is confirmed or bridge is activated in runtime.
- Authority: AUDIT_POLICY

## Open debts

- `DEBT_BOUNDARY_TOKENS` — count=102 — status=OPEN_AUDIT_DEBT — patch_now=False
  - Reason: No-boundary-token files are not confirmed runtime violations.
- `DEBT_NEO4J_READONLY_REVIEW` — count=1 — status=REVIEW_REQUIRED — patch_now=False
  - Reason: No confirmed runtime write violation in F23A5.1.

## Locked decisions

- No runtime patch in F23A5.2.
- No agent governance violation confirmed.
- No-boundary-token files remain audit debt.
- Neo4j readonly bridge remains review-required, not patched.
- Decision authority remains KX108_ONLY.

## Next

F23A5.3_F23A5_BLOCK_CHECKPOINT

## Status

F23A5_2_AGENT_GOVERNANCE_AUDIT_DONE
