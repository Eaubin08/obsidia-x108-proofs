# Note de gel P1

## Statut

P1 FERMÉ

## Références canoniques

- Commit de clôture technique : `bd87e15`
- Commit de gel public : `99e966a`
- Tag de gel officiel : `p1-freeze-2026-04-22`

## Interprétation

- `bd87e15` ferme les shadow zones techniques de P1
- `99e966a` ajoute le pack de clôture public et gèle P1 comme périmètre public lisible
- `p1-freeze-2026-04-22` est le tag de gel public canonique

## Ce qui est gelé

- périmètre de preuves Lean 4
- spécifications TLA+ / TLC et runs
- vérificateurs Python publics
- couche Sigma minimale publique
- exemples publics et smoke tests publics
- vérifications du schéma d'ancre RFC3161
- runner public : `run_all_proofs.ps1`

## Note sur la branche principale

- `main` peut continuer après le freeze
- P2-bank et les packs publics ultérieurs ne redéfinissent pas P1
- le périmètre P1 gelé reste le tag / commit ci-dessus

## Guide de lecture des tags

Ce dépôt contient plusieurs familles de tags. Voici comment les lire :

### Tags de gel P1 (cibles d'audit)

Ces tags sont la cible canonique pour tout audit du périmètre public P1 :

| Tag | Rôle |
|---|---|
| `p1-freeze-2026-04-22` | Gel canonique P1 — cible d'audit principale |
| `p1-public-final-2026-04-22` | Gel final public P1 |
| `v1.0.0-stable-kernel` | Release GitHub officielle (vérifiée) |
| `v1.0-sovereign-kernel` | Même commit, dimension souveraineté publique |

### Tags P2-bank (hors périmètre P1)

Ces tags couvrent les tests de montée en charge et la validation de P2-bank. Ils ne font **pas** partie de la cible d'audit P1 :

- `p2-bank-*` : tests scale, replay, fuzz (1k / 10k / 100k)
- `bank-robo-*` : validation nominale, robustesse, batch client
- `p2-bank-regulatory-proxy-*` : proxy réglementaire P2

### Tags de ligne trading / GPS / Sigma

Ces tags correspondent à la ligne de maturation trading. Ils sont post-P1 et ne redéfinissent pas P1 :

- `v1.0.8-*`, `v1.0.9-SIGMA-GPS-*` : intégration GPS / Sigma
- `v1.1.x-TRADING-*`, `v1.1.x-TRINITY-*` : ligne trading
- `v1.5.x-STABLE`, `v1.6.0-RAGNAROK-STABLE` : paliers stables trading

### Tags d'audit de traçabilité

Ces tags sont des ancres d'audit prises lors de sessions de validation :

- `audit-traceability-3-domains-*` : audit multi-domaines
- `audit-evidence-board-v2-*` : tableau de preuves d'audit v2
- `triple-confidence-x108-audit-*` : audit triple confiance X-108

### Tags techniques

Ces tags sont des ancres techniques prises lors de corrections :

- `node-bridge-*`, `bridge-server-merkle-repair-*` : réparation bridge/Merkle
- `integrate-temp-reims-critical-*` : intégration critique (branch supprimée après merge)
- `full-green-before-public-cleanup-*` : état vert avant nettoyage public

## Règle de lecture pour un auditeur

Si vous auditez P1 :

1. Clonez le dépôt
2. Checkout du tag `p1-freeze-2026-04-22`
3. Ignorez tous les tags P2-bank, trading, et audit-evidence
4. Lancez `.\\run_all_proofs.ps1`
5. Consultez `docs/AUDIT_TOOLS.md` pour les outils de scoring
