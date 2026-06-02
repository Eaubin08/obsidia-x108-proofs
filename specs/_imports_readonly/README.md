# _imports_readonly/

Ces fichiers sont des **imports readonly** des sources existantes dans le repo.

## Règle

- Ils ne copient PAS le code source.
- Ils extraient les **faits utiles**, citent les **chemins originaux**, et rendent la source **compréhensible**.
- Ne jamais modifier les sources originales.
- `Do Not Move Original Source: true` dans chaque fichier.

## Format de chaque fichier

```
Import Type: READONLY_SOURCE_IMPORT
Original Source Paths: [chemins exacts]
Imported Facts: [faits extraits]
What This Source Proves: [ce que la source prouve]
What This Source Does NOT Prove: [ce qu'elle ne prouve pas]
Boundary: [limite d'usage]
Claim-Scope: [ce qu'on peut affirmer]
Specs Depending On This Source: [specs qui citent cette source]
Runtime Status: [statut runtime]
Do Not Move Original Source: true
Authority: KX108_ONLY
```
