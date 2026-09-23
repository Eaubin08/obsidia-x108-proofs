# HR

> Domain Pack HR — vision à construire.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**

## État réel

Aucun corpus RH spécifique suffisamment solide n'a été trouvé pour revendiquer une architecture de recrutement, workforce, carrière ou paie.

Le dépôt possède en revanche des mécanismes transverses autour de :

- human review ;
- validation humaine ;
- operator permissions ;
- organization identity ;
- context packets ;
- consentement ;
- mémoire gouvernée.

Ils peuvent servir de fondation, mais ils ne constituent pas encore un domaine HR.

## Vision candidate

Un futur Domain Pack HR devrait distinguer au minimum :

```text
information sur une personne
≠ préférence
≠ recommandation
≠ permission
≠ décision organisationnelle
```

et traiter explicitement provenance, consentement, accès, rétention et possibilité de revue humaine.

Cette vision est une direction d'architecture, pas un runtime présent.

## Sources transverses utiles

- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [RGPD Compliance Scope Guard](../../runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

## Manques

- employee/workforce object model ;
- lifecycle RH ;
- recrutement ;
- règles métier ;
- object map ;
- sources auditées ;
- tests ;
- consent / review spécifiques au domaine.

Les snapshots génériques Brody/mémoire ne doivent pas être présentés comme une architecture HR.
