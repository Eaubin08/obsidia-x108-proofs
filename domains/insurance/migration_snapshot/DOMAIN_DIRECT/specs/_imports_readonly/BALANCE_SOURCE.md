# BALANCE_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/gencoin_sandbox/balance_operator.py`
- `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md`
- `docs/gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md`

Imported Facts:
- `balance_operator.py` : calcule un score de balance multi-facteur dans un sandbox
- BALANCE_CANON.md : document de référence canonique pour la Balance Obsidienne
- LIMITS_AND_STATUS.md : limites explicites de la balance sandbox
- BUV (Balance Universelle Valorisée) = nom conceptuel pour la balance — pas un fichier dédié dans le repo

What This Source Proves:
- Un opérateur de balance sandbox est implémenté en Python
- La balance produit un score — pas une décision ALLOW/HOLD/BLOCK
- Le concept BUV correspond à `BALANCE_CANON.md` + `balance_operator.py`

What This Source Does NOT Prove:
- Que la balance prend une décision finale
- Qu'il existe un fichier `buv_master_spec.md` (ABSENT_UNDER_THIS_NAME)
- Que le score de balance remplace le verdict X108

Boundary:
- SANDBOX — `balance_operator.py` est dans `gencoin_sandbox/`
- Balance → X108 décide

Claim-Scope:
- "Obsidia calcule un score de balance multi-facteur en Python" — AUTORISÉ
- "La Balance Obsidienne décide" — INTERDIT
- "BUV = token" — INTERDIT

Specs Depending On This Source:
- 05_BALANCE_BUV_GEOMETRIES/BUV_MASTER_SPEC.md
- 05_BALANCE_BUV_GEOMETRIES/BALANCE_NO_DECISION_RULE.md
- 10_VALUE_GENCOIN_JCOIN/GENCOIN_X108_MINT_CONTRACT.md

Runtime Status: RUNTIME_CODE (sandbox)

Do Not Move Original Source: true
Authority: KX108_ONLY
