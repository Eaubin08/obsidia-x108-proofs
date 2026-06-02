# DRY_RUN_NOT_PRODUCTION_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `connectors/aviation_robo.py` (DEFAULT_API_BASE = http://127.0.0.1:8000)
- `periphery/world_action_controlled_runtime_stub.py`
- `docs/architecture/F74_F77_FINALIZATION_AUDIT.md`

Source Status: RUNTIME_CODE + DRY_RUN

Scope:
Définir la frontière dry-run / production et les claims associés.

Allowed:
- "Le connector aviation POST en local (127.0.0.1) — DRY_RUN"
- "WORLD_ACTION_DRY_RUN_READY = l'action est prête pour revue humaine, pas déclenchée"

Forbidden:
- "Obsidia exécute des actions dans le monde réel en production"
- "DRY_RUN = production"
- "aviation connector = défense réelle"

Inputs: GPS_SOURCE.md + ACTION_LIFECYCLE_SOURCE.md

Outputs: Frontière DRY_RUN ↔ production documentée

Metrics: N/A

Invariants:
- WORLD_ACTION_DRY_RUN_READY est un état du cycle d'action — pas une action réelle
- Toute action réelle nécessite DecisionTicket + gate humain

X108 Boundary: KX108_ONLY — toute action réelle passe par X108

Tests Required:
- Vérifier que WORLD_ACTION_DRY_RUN_READY ne déclenche pas d'actuateur

Proof Expected: Python test

Runtime Status: DRY_RUN

Claim-Scope Notes:
GPS connector = local POST uniquement. Aucune utilisation en défense ou aviation réelle sans validation externe.

Open Questions: Quand le passage DRY_RUN → production sera-t-il planifié ?
