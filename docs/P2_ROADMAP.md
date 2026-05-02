# Trajectoire P2 et suite

## Statut

P2-BANK EN COURS

## Frontière P1 / P2

P1 est gelé au tag `p1-freeze-2026-04-22`.

P2-bank et les packs publics ultérieurs s'empilent par-dessus P1 sur la branche `main`.
Ils ne redéfinissent pas le périmètre P1 gelé.

## Ce que P2-bank a validé (tags de référence)

Les tags suivants documentent la montée en charge et la validation de P2-bank :

| Tag | Contenu |
|---|---|
| `p2-bank-test-pack-2026-04-22` | Pack de tests initial P2-bank |
| `p2-bank-fix-2026-04-23` | Correction P2-bank |
| `p2-bank-regulatory-proxy-2026-04-23` | Proxy réglementaire P2 |
| `p2-bank-replay-1k-2026-04-23` | Replay 1 000 transactions |
| `p2-bank-replay-10k-2026-04-23` | Replay 10 000 transactions |
| `p2-bank-replay-100k-2026-04-23` | Replay 100 000 transactions |
| `p2-bank-scale-1k-2026-04-23` | Scale 1 000 transactions |
| `p2-bank-scale-10k-2026-04-23` | Scale 10 000 transactions |
| `p2-bank-fuzz-scale-1k/10k/100k` | Tests de fuzz scale P2-bank |
| `bank-robo-nominal-10of10-2026-04-23` | Validation nominale 10/10 |
| `bank-robo-robustness-pack-v1-2026-04-23` | Pack robustesse v1 |
| `bank-robo-client-batch1000-process-only-validated-2026-04-24` | Batch client 1 000 validé |
| `p2-bank-robo-real-consistency-1000-2026-04-24` | Consistance réelle 1 000 |

## Périmètre P2 public (en cours de définition)

Le périmètre public P2 sera défini et gelé quand :

- les adaptateurs bancaires publics sont stables et reproductibles
- un runner P2 e2e est validé localement
- un tag `p2-freeze-*` est posé sur `main`

Ce document sera mis à jour à ce moment.

## Ce que P2 n'est pas (encore)

- P2 n'est pas encore gelé publiquement
- Les tags `p2-bank-*` sont des ancres de développement, pas des cibles d'audit
- Le périmètre P2 complet (banking, trading, e-commerce, cockpit opérateur) reste en cours de consolidation

## Ligne de maturation trading

En parallèle de P2-bank, une ligne trading/GPS/Sigma a maturé (tags `v1.0.8-*` à `v1.6.0-RAGNAROK-STABLE`).
Cette ligne converge vers le kernel souverain (`v1.0-sovereign-kernel`).
Son intégration dans le périmètre public P2 sera documentée lors du gel P2.

## Liens utiles

- `P1_FREEZE_NOTE.md` — référence du gel P1
- `PUBLIC_STATUS.md` — statut public actuel
- `docs/REPO_MAP.md` — carte du dépôt
