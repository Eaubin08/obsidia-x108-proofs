# Evidence Contract V4

## Règles

- Une tâche peut être TODO / FORMALIZED / DONE.
- DONE exige une preuve attachée.
- Une gate est OPEN uniquement si toutes ses tâches requises sont DONE.
- G5 est OPEN uniquement si G1, G2, G3 et G4 sont OPEN.

## Types d’évidence

- LEAN_BUILD_LOG
- NO_SORRY_SCAN
- TLA_REPORT
- PYTHON_TEST_LOG
- VITEST_LOG
- AUDIT_REPORT
- DOC_MATRIX
- SIGNED_VERDICT
