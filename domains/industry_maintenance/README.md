# Industry / Maintenance

> Scaffold UDIP pour machines, production, maintenance, capteurs et opérateurs.

## Statut

- `NEW_DOMAIN_SCAFFOLD`
- `source_type: none`
- `implementation_state: SCAFFOLD_ONLY`

## Périmètre déclaré

- machines ;
- production ;
- maintenance ;
- sensors ;
- operators.

Aucun corpus domaine spécifique supplémentaire n'a été retrouvé lors de l'audit conceptuel.

## Vision cible

```text
machine / sensor / production state
→ observation
→ anomaly / maintenance signal
→ DomainSignal
→ KX108
→ Binder si action
→ intervention candidate
```

Cette chaîne est une cible documentaire, pas une implémentation.

## Sources

- [domain_pack.yaml](domain_pack.yaml)
- [sources.yaml](sources.yaml)
- [conformance.md](conformance.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

## Manques

Sources métier, object map, règles de maintenance, adapters, tests et preuves.
