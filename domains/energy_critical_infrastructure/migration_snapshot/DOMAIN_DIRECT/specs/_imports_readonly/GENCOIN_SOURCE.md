# GENCOIN_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/gencoin.py`
- `periphery/gencoin_ledger.py`
- `periphery/gencoin_debt_model.py`
- `periphery/gencoin_distribution.py`
- `docs/gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md`
- `docs/gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md`
- `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`
- `periphery/blockchain/token_policy.py`

Imported Facts:
- `GencoinMintCandidate` : action_id, os3_ticket_id, x108_gate, proof_valid, data_ok, memory_stable, energy_stable, oc_stable, permission_ok, economic_ok, gross_value, total_debt, gencoin_candidate, mint_allowed
- Formule : `GC = X108_ALLOW × OS3_PROOF × DATA_OK × MEMORY_STABLE × ENERGY_STABLE × OC_STABLE × PERMISSION_OK × ECONOMIC_OK × max(0, VALUE-DEBT)`
- `mint_allowed = True` seulement si `x108_gate == "ALLOW"`
- token_policy.py : BLOCK absolu sur MINT/DEPLOY/CREATE pour Gencoin (`is_gencoin=True` → gate=BLOCK)
- `GENCOIN_NOT_A_TOKEN_POLICY_V1.md` : "Gencoin is NOT a real token."
- Jcoin = ABSENT_UNDER_THIS_NAME (0 occurrences dans le repo)

What This Source Proves:
- Gencoin est un système de ledger append-only avec calcul de valeur candidate
- La valeur Gencoin est conditionnée par X108_ALLOW + OS3_PROOF
- Il est impossible de minter ou déployer un token Gencoin

What This Source Does NOT Prove:
- L'existence de Jcoin (ABSENT_UNDER_THIS_NAME)
- Un déploiement blockchain ou smart contract
- Une tokenomics finalisée
- Que `gencoin_candidate` représente une valeur réelle échangeable

Boundary:
- Ledger local — CANDIDATE — pas on-chain — pas token réel

Claim-Scope:
- "Gencoin est un système de ledger de valeur candidate gouverné" — AUTORISÉ
- "Gencoin est un token" — INTERDIT
- "Jcoin existe dans le repo" — INTERDIT (ABSENT)

Specs Depending On This Source:
- 10_VALUE_GENCOIN_JCOIN/GENCOIN_CANDIDATE_VALUE_NOT_TOKEN_SPEC.md
- 10_VALUE_GENCOIN_JCOIN/GENCOIN_X108_MINT_CONTRACT.md
- 10_VALUE_GENCOIN_JCOIN/GENCOIN_TOKENOMICS_BOUNDARY.md

Runtime Status: RUNTIME_CODE + CANDIDATE

Do Not Move Original Source: true
Authority: KX108_ONLY
