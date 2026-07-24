# 15_GUARDS_NON_DECISION — STATUT : CONCEPT_ONLY

**Audit 2026-07-08 (session gateway-fusion)** : les modules de ce dossier
(`readonly_context_guard.py`, `no_*_act.py`, `policy_scope_guard` du 09)
retournent tous `True` inconditionnellement. **Aucun code ne doit s'y fier
comme garde reelle.**

## Gardes REELLES en production (a utiliser a la place)

| Fonction | Implementation reelle |
|---|---|
| Gates DENY/HOLD/CLARIFY/ALLOW | `obsidia-router/app/gates/gates.py` (369+ tests) |
| Boundaries fail-closed | `_assert_boundary_compliance` des modules brody_memory_readonly |
| Derive intention/outil (δ2) | `.claude/hooks/obsidia_pretooluse_guard.py` |
| Zones protegees | `.claude/settings.json` deny-list + PROTECTED_SCOPE.md |
| Autorite domaine | kernel X108 via `/api/live/kernel/adapters/*` |

## Sortie de CONCEPT_ONLY

Remplir un guard = lui faire verifier reellement son invariant (modele :
`_assert_boundary_compliance`, fail-closed) + tests. Toute promotion passe
par PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE.

`decision_authority = KX108_ONLY`
