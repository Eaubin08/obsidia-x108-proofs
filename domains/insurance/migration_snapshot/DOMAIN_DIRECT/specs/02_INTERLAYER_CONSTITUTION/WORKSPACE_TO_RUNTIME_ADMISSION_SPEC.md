# WORKSPACE_TO_RUNTIME_ADMISSION_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/` (workspace hub)
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/`
- `docs/status/PERIPHERY_PUBLIC_INDEX.md`

Source Status: DOC_ONLY

Scope: Définir les conditions d'admission d'un concept workspace dans le runtime Obsidia.

Allowed:
- "Un concept workspace peut devenir runtime seulement après spec contractuelle + tests"

Forbidden:
- "Un concept workspace peut être directement implémenté sans spec"
- "ABSENT_UNDER_THIS_NAME = justification pour créer runtime immédiatement"

Inputs: Concepts du workspace hub
Outputs: Spec contractuelle → tests → runtime

Metrics: N/A

Invariants:
```
Concept workspace
    → SOURCE_DISCOVERY (Plan 1)
    → SOURCE_ORGANIZED (Plan 2 — ici)
    → RUNTIME_CANDIDATE (Plan 3)
    → RUNTIME_CODE + tests
    → X108 gate
    → Claim public
```

X108 Boundary: KX108_ONLY pour tout runtime admis
Tests Required: Spec must exist before runtime
Proof Expected: N/A
Runtime Status: DOC_ONLY
Claim-Scope Notes: Workspace ≠ runtime — spec intermédiaire obligatoire.
Open Questions: Quels concepts workspace sont prioritaires pour Plan 3 ?
