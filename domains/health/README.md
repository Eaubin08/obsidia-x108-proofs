# Health

> Domain Pack Health — vision à construire.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**

## État réel

Aucun corpus médical/clinique suffisamment spécifique n'a été trouvé pour justifier un README métier détaillé.

Le dépôt contient toutefois des mécanismes transverses potentiellement nécessaires à un futur domaine Health :

- contexte humain ;
- consentement ;
- provenance ;
- RGPD / data governance ;
- human review ;
- non-souveraineté ;
- evidence / receipts.

Ces mécanismes ne sont **pas** un modèle médical.

## Vision candidate

Un futur Health pack devrait probablement séparer :

```text
observation de santé
≠ interprétation
≠ recommandation
≠ autorisation
≠ action clinique
```

et préserver systématiquement :

- source ;
- date / fraîcheur ;
- incertitude ;
- consentement ;
- evidence refs ;
- limites du modèle.

Cette section est une **vision cible prudente**, pas une architecture existante.

## Sources transverses utiles

- [RGPD Compliance Scope Guard](../../runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md)
- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

## Manques

- objets métier ;
- sources santé ;
- terminologie clinique ;
- consent model domaine ;
- object map ;
- tests ;
- preuves ;
- revue métier externe.

Aucune maturité Health ne doit être déduite des fichiers génériques présents dans `migration_snapshot/`.
