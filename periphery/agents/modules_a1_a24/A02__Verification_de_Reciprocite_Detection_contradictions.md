# A02 — Vérification de Réciprocité / Détection contradictions

**Type :** MODULE_A
**Protocole :** Symétrie / RIT
**Statut source :** [x] Intégré
**Test V4 :** [ ] Test V4

## Ce que fait ce module
Ce module porte la fonction : **Vérification de Réciprocité / Détection contradictions**.
Son protocole opératoire associé est : **Symétrie / RIT**.

## Contrat de test V4
- État attendu : TESTED / NOT_TESTED / REJECTED / BLOCKED.
- Un test unitaire dédié doit exister.
- Un log de test doit être attaché comme évidence.
- Les modules A4, A7, A13 et T12 restent dépendants de G1 si liés à P36/P107/P161.

## Evidence attendue
- PYTHON_TEST_LOG ou VITEST_LOG
- AUDIT_D_MODULE_TEST_REPORT
- Statut final Audit D
