# Insurance

> Domain Pack Insurance — scaffold sans architecture métier revendiquée.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**

## État réel

L'audit conceptuel n'a pas retrouvé de corpus assurance suffisamment spécifique pour définir correctement :

- policy lifecycle ;
- claim ;
- underwriting ;
- actuarial model ;
- insured object ;
- coverage ;
- indemnification.

Des concepts génériques existent ailleurs — risque, fraude, evidence, compensation, claim-scope — mais ils ne doivent pas être rebaptisés “Insurance” sans travail métier réel.

## Vision minimale

Le futur pack devra probablement séparer :

```text
risk evidence
≠ coverage
≠ claim validity
≠ compensation
≠ payment authorization
```

mais cette structure reste à construire.

## Sources

- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)
- [Domain Pack Standard](../../udip/DOMAIN_PACK_STANDARD.md)

## Manques

Pratiquement toute la sémantique domaine.

Le bon prochain geste est une source métier réelle avant toute extension du scaffold.
