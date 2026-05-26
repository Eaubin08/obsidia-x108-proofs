
# Genome Lock Policy — Obsidia O1–O8

## Statut

`LOCK_POLICY = CANONICAL_MINIMAL_V1`

Ce fichier fixe la règle de verrouillage du génome constitutionnel Obsidia.

## Objet

Le génome O1–O8 représente les lois de sûreté cognitive et de non-contournement du pack :

- O1 — Non-Action Légitime
- O2 — Irréversibilité Structurelle
- O3 — Épreuve Temporelle X-108
- O4 — Non-Arbitrage sous Conflit
- O5 — Élimination Décisionnelle
- O6 — Mémoire Négative
- O7 — Auditabilité Native
- O8 — Séparation Cognition / Action

## Règles de verrouillage

1. Aucune loi O1–O8 ne peut être supprimée par une couche périphérique.
2. Aucune loi O1–O8 ne peut être renommée sans décision humaine explicite.
3. Aucun agent, arbre, cortex, Shazam, Reverse OS, BDF, HexaFlux ou MCP Bridge ne peut ouvrir un chemin `ACT`.
4. Toute modification doit produire :
   - un diff lisible ;
   - une justification ;
   - un hash SHA256 ;
   - un audit de non-décision ;
   - un verdict humain ou kernel-boundary explicite.

## Invariant

```text
Genome(O1..O8) ↛ ACT
Decision = KX108
```

## Verdict

Ce fichier est une politique de verrouillage documentaire.  
Il ne constitue pas une preuve formelle Lean/TLA+.
