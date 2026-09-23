# Logistics / Supply Chain

> Scaffold UDIP pour stock, entrepôt, fournisseurs, transport, routes et livraison.

## Statut

- `NEW_DOMAIN_SCAFFOLD`
- `source_type: none`
- `implementation_state: SCAFFOLD_ONLY`

## Périmètre déclaré

- stock ;
- warehouse ;
- suppliers ;
- transport ;
- route ;
- delivery.

Aucun corpus logistique spécifique supplémentaire n'a été retrouvé.

## Vision cible

```text
stock / supplier / transport event
→ logistics state
→ risk / exception / proposal
→ DomainSignal
→ KX108
→ Binder si action
→ execution / receipt
```

## Sources

- [domain_pack.yaml](domain_pack.yaml)
- [sources.yaml](sources.yaml)
- [conformance.md](conformance.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

## Manques

Object map, règles supply-chain, adapters, sources terrain, tests, receipt/replay spécifiques.
