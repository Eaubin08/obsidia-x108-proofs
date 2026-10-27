
# Audit BDF

## Statut

`AUDIT_STATUS = MINIMAL_REAL_AUDIT`

## Périmètre

Bi-Cerebral Diffusion Framework, stubs LLM/Diffusion, garde AEG.

## Contrôles effectués

- Module BDF importable.
- Tests unitaires OK.
- BDF ne retourne pas ACT.
- Sortie interprétée comme proposition/intution, pas décision.

## Verdict

BDF est un stub sûr minimal.

## Limites

- Pas de modèle externe réellement appelé.
- AEG encore symbolique.

## Invariant de non-décision

```text
Layer ↛ ACT
Decision = KX108
```
