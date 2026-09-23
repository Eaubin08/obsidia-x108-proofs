# OBSIDIA_INTERLAYER_CONSTITUTION

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md`
- `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`
- `docs/status/PERIPHERY_PUBLIC_INDEX.md`

Source Status: DOC_ONLY + SOURCE_CANON

Scope:
Constitution intercouche Obsidia — définit les règles fondamentales entre toutes les couches.

Allowed:
- "La couche Workspace fournit des sources conceptuelles"
- "La couche Import Readonly organise les sources"
- "La couche Spec définit les contrats d'usage"
- "La couche Runtime exécute sous contrôle X108"
- "La couche Claim définit les affirmations publiques autorisées"

Forbidden:
- Court-circuiter la hiérarchie Workspace → Spec → Runtime → Claim
- Créer du runtime sans spec préalable

Inputs: Toutes les sources Plan 1 + NPL
Outputs: Architecture intercouche documentée

Metrics: N/A

Invariants:
```
Workspace (source conceptuelle)
    ↓
Import Readonly (facts extraits)
    ↓
Spec (contrat d'usage)
    ↓
Runtime (code contrôlé)
    ↓
Claim (affirmation publique autorisée)
```

X108 Boundary: KX108_ONLY à chaque transition Runtime → Action

Tests Required: N/A (constitution documentaire)
Proof Expected: N/A
Runtime Status: DOC_ONLY
Claim-Scope Notes: N/A
Open Questions: Comment gérer les évolutions de constitution intercouche ?
