# BRODY_GRAPHITI_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/brody/brody_runtime_readonly.py`
- `periphery/brody/brody_context_query.py`
- `periphery/brody/brody_language_router.py`
- `sigma/graphiti_readonly_bridge.py`
- `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`
- `docs/freeze/BRODY_TREE_POLICY_BINDING_REPORT.md`
- `apps/obsidia_api/brody_tree_policy.py`

Imported Facts:
- `brody_runtime_readonly.py` : Brody en mode readonly — advisory uniquement
- `brody_language_router.py` : BrodyLanguageRoute avec `memory_write=False`
- `graphiti_readonly_bridge.py` : lecture graphiti uniquement — READONLY
- BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md : document freeze sur les droits Brody
- BRODY_TREE_POLICY_BINDING_REPORT.md : liaison Brody ↔ Tree34 (T31=Arbre des Flux)

What This Source Proves:
- Brody est readonly + advisory — `memory_write=False`
- Graphiti est en lecture uniquement dans le périmètre public
- Des documents freeze définissent les droits Brody

What This Source Does NOT Prove:
- Que graphiti_write est sécurisé en production
- Que Brody prend des décisions

Boundary:
- READONLY — advisory — gate humain obligatoire pour écriture mémoire

Claim-Scope:
- "Brody fournit un contexte readonly à X108" — AUTORISÉ
- "Brody décide ou écrit mémoire autonomement" — INTERDIT

Specs Depending On This Source:
- 08_MEMORY_BRODY_GRAPHITI/BRODY_RESPONSE_AUTHORITY_SPEC.md
- 08_MEMORY_BRODY_GRAPHITI/MEMORY_WRITE_X108_REVIEW_GATE.md
- 12_NARRATIVE_PROVENANCE_LAYER/NPL_TO_BRODY_MAP.md

Runtime Status: RUNTIME_CODE + READONLY

Do Not Move Original Source: true
Authority: KX108_ONLY
