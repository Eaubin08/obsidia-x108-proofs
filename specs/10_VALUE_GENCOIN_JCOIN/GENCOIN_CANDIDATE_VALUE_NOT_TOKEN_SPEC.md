# GENCOIN_CANDIDATE_VALUE_NOT_TOKEN_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/gencoin.py`
- `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`
- `periphery/blockchain/token_policy.py`

Source Status: RUNTIME_CODE + SOURCE_CANON

Scope:
Verrouiller définitivement : Gencoin = valeur candidate gouvernée ≠ token réel.

Allowed:
- "Gencoin est un système de ledger append-only avec calcul de valeur candidate"
- "mint_allowed=True seulement si x108_gate == 'ALLOW'"
- "gencoin_candidate = valeur calculée — pas on-chain"

Forbidden:
- "Gencoin est un token"
- "Gencoin peut être minté sur blockchain"
- "Jcoin existe dans le repo" (ABSENT_UNDER_THIS_NAME)
- "smart contract Gencoin"
- "tokenomics finale Gencoin"

Inputs:
- GencoinMintCandidate : OS3ProofTicket + X108 ALLOW + métriques

Outputs:
- gencoin_candidate (float) — valeur calculée post-preuve
- mint_allowed (bool) — True seulement si X108 ALLOW + OS3_PROOF

Metrics:
- `GC = X108_ALLOW × OS3_PROOF × DATA_OK × MEMORY_STABLE × ENERGY_STABLE × OC_STABLE × PERMISSION_OK × ECONOMIC_OK × max(0, VALUE-DEBT)`

Invariants:
- `is_gencoin=True` → `token_policy.gate=BLOCK` dans `token_policy.py`
- `mint_allowed=False` si `x108_gate != "ALLOW"`
- Gencoin ≠ ERC-20, ≠ blockchain deployment

X108 Boundary: X108 ALLOW est une condition nécessaire pour gencoin_candidate > 0

Tests Required:
- test_gencoin_not_a_token
- test_mint_blocked_without_x108_allow

Proof Expected: Python test (token_policy BLOCK)

Runtime Status: RUNTIME_CODE + CANDIDATE

Claim-Scope Notes:
"candidate ≠ token réel" — gencoin_candidate est une valeur calculée, jamais on-chain.

Open Questions: Jcoin — alias Gencoin ou concept distinct ? Décision humaine requise.
