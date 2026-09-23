# OBSIDIA SRL — Acte de promotion canonique V1

**Date** : 2026-07-08
**Autorité** : Étienne Aubin (opérateur) — instruction explicite en session
(« Promotion SRL CANONICAL »), exécutée par Claude Code.
**Référence audit** : `OBSIDIA_SRL_SESSION_REGISTRY_LAYER_AUDIT_V0` (2026-06-25),
verdict `FOUNDATION_PRESENT_NOT_CANONICAL`, 0 violation, invariants souverains
respectés (`memory_write=False`, `decision_authority=KX108_ONLY`,
`kernel_mutation=False`).

## Modules promus `CANONICAL`

| Pilier | Module | Statut avant | Statut après |
|---|---|---|---|
| presave_buffer | `session_presave_buffer_readonly` (v1) | ACTIVE / non canonique | **CANONICAL** |
| auto_triage | `auto_triage_memory_intake_readonly` (v1) | ACTIVE / non canonique | **CANONICAL** |
| ledger | `brody_api_bridge_runtime_authorization_ledger_readonly` | ACTIVE / non canonique | **CANONICAL** |

## Portée et limites

- La promotion couvre les **trois piliers fondation** uniquement. Les modules
  `SEMI_ACTIVE` et `COLD` de la taxonomie V2 restent non canoniques.
- La promotion ne modifie aucun code : elle acte que ces modules sont la
  référence du pipeline mémoire (`intake → presave → triage → validation
  opérateur`), désormais alimenté par `_MEMORY_INTAKE_OUTBOX/` (gateway).
- Révocable par l'opérateur ; toute évolution de ces modules repasse par
  `PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE`.

`decision_authority = KX108_ONLY` — ce document est un acte opérateur, pas un verdict machine.
