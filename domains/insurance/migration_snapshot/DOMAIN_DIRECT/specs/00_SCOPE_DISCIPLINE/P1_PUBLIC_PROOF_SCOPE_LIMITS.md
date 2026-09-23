# P1_PUBLIC_PROOF_SCOPE_LIMITS

Status: SOURCE_CANON
Authority: KX108_ONLY

Source Paths:
- `docs/PROOF_SCOPE.md` (SOURCE_CANON — NE PAS MODIFIER)

Source Status: SOURCE_CANON

Scope:
Reproduire les limites du périmètre public P1 telles que définies dans PROOF_SCOPE.md.

Allowed:
- Citer les 4 catégories de preuves définies dans PROOF_SCOPE.md
- "PASS dans proofs/lean/ = proof formelle compilant sous Lake"
- "PASS dans formal/tla/ = aucune violation TLC détectée"
- "PASS Python = scénarios canoniques publics validés"

Forbidden:
- Étendre le périmètre P1 sans modification de PROOF_SCOPE.md
- Affirmer que PASS Python = LEAN_PROVEN
- Affirmer que TLC PASS = preuve d'absence totale de violation

Inputs: PROOF_SCOPE_SOURCE.md

Outputs: Référence normative du périmètre public P1

Metrics: N/A

Invariants:
- 4 catégories séparées — PASS ne signifie pas la même chose dans chaque catégorie
- Ne jamais fusionner les catégories dans un claim public

X108 Boundary: KX108_ONLY

Tests Required: N/A — spec normative

Proof Expected: SOURCE_CANON — déjà gelée

Runtime Status: SOURCE_CANON

Claim-Scope Notes:
Cette spec est une référence — ne pas la modifier. Si le périmètre P1 évolue, modifier PROOF_SCOPE.md d'abord.

Open Questions: Aucune — source canonique
