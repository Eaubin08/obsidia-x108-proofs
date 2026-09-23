# BTP / Construction

> Scaffold UDIP pour terrain, plans, documents, sous-traitants, planning et exceptions.

## Statut

- `NEW_DOMAIN_SCAFFOLD`
- `source_type: none`
- `implementation_state: SCAFFOLD_ONLY`

## Périmètre déclaré

- terrain ;
- plans ;
- documents ;
- subcontractors ;
- planning ;
- exceptions.

Aucun corpus métier BTP distinct n'a été retrouvé lors de l'audit conceptuel.

## Vision cible

Le pack devra transformer événements de chantier, documents, planning et exceptions en signaux gouvernables sans donner d'autorité au domaine.

## Sources

- [domain_pack.yaml](domain_pack.yaml)
- [sources.yaml](sources.yaml)
- [conformance.md](conformance.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

## Manques

Objets chantier, source terrain, contraintes métier, object map, adapters, tests et preuves.
