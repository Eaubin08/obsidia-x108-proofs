# Smart Contract Risk Gate V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Blocks unaudited smart contract deployment and evaluates contract interaction risk.
**Module:** `periphery/blockchain/smart_contract_risk_gate.py`
**Gate:** BLOCK (deploy without audit), HOLD (unverified contracts)

## Role

The Smart Contract Risk Gate evaluates the risk of any smart contract interaction — deployment, invocation, approval. It blocks all unaudited contract deployments and flags unverified contract interactions.

## Inputs

- `contract_id: str` — contract identifier
- `action: str` — DEPLOY, CALL, READ, APPROVE, etc.
- `has_audit: bool` — whether the contract has been audited
- `is_verified: bool` — whether the contract source is verified
- `is_proxy: bool` — whether the contract uses a proxy pattern
- `has_unbounded_approval: bool` — whether approval is unbounded

## Outputs

- `SmartContractRiskDecision` with fields:
  - `gate: str` — BLOCK, HOLD, or ALLOW
  - `audit_required: bool`
  - `deploy_blocked: bool`
  - `risk_flags: list[str]`

## Risk Flags

| Condition | Flag |
|-----------|------|
| DEPLOY without audit | DEPLOY_WITHOUT_AUDIT → BLOCK |
| Unbounded approval | UNBOUNDED_TOKEN_APPROVAL |
| Unverified proxy | UNVERIFIED_PROXY_CONTRACT |
| Unverified contract (non-READ) | UNVERIFIED_CONTRACT → HOLD |

## Forbidden Actions

| Action | Condition | Gate |
|--------|-----------|------|
| DEPLOY | has_audit=False | BLOCK |
| Any non-READ | is_verified=False | HOLD |
| Any with proxy | is_proxy=True, is_verified=False | HOLD |

## Relation to X108

The smart contract gate recommends BLOCK/HOLD. X108 is the final decision authority but cannot override the DEPLOY_WITHOUT_AUDIT block.

## Tests

- `tests/periphery/test_smart_contract_risk_gate.py`
- `tests/non_sovereignty/test_no_smart_contract_deploy.py`

## Status

**DRY_RUN_ONLY** — No real contract deployment or interaction.
