# ACTION_LIFECYCLE_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/action_lifecycle.py` (lines 8-31)

Imported Facts:
- 10 états définis : INPUT_CAPTURED → ACTION_CANDIDATE_BUILT → PERIPHERY_SCORED → SIGMA_ROUTED → X108_EVALUATED → OS3_TICKETED → GENCOIN_EVALUATED → WORLD_ACTION_DRY_RUN_READY → FEEDBACK_CAPTURED → MEMORY_CANDIDATE_BUILT → CLOSED
- Transitions définies en Python comme graphe orienté
- FEEDBACK_CAPTURED = 9e état (présent dans le code, absent de certaines docs)
- Classe ActionPhase + ActionRecord

What This Source Proves:
- Le cycle complet d'une action gouvernée est spécifié en Python
- X108_EVALUATED est l'étape centrale — avant OS3_TICKETED et après SIGMA_ROUTED
- GENCOIN_EVALUATED ne se produit qu'après OS3_TICKETED

What This Source Does NOT Prove:
- Preuve formelle Lean de la machine à états
- Que FEEDBACK_CAPTURED est dans le périmètre public (décision humaine requise)
- Que CLOSED garantit absence de replay futur

Boundary:
- Code Python exécutable — pas de preuve formelle

Claim-Scope:
- "Le cycle d'action Obsidia comporte 10 états définis en Python" — AUTORISÉ
- "Le cycle est formellement prouvé" — INTERDIT (FORMAL_PROOF_PENDING)

Specs Depending On This Source:
- 01_X108_AUTHORITY/X108_TEMPORAL_GATE_SPEC.md
- 02_INTERLAYER_CONSTITUTION/ACTION_LIFECYCLE_X108_SPEC.md
- 11_PROOF_REPLAY_OS3/OS3_PROOF_RUNTIME_SPEC.md

Runtime Status: RUNTIME_CODE

Do Not Move Original Source: true
Authority: KX108_ONLY
