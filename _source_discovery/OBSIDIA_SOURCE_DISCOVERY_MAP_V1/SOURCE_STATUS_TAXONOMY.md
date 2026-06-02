# SOURCE_STATUS_TAXONOMY
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1

> Définition canonique de chaque statut utilisé dans les rapports de découverte.

---

## Statuts primaires

| Statut | Définition |
|--------|-----------|
| `SOURCE_CANON` | Fichier de référence désigné, freezé, jamais modifiable sans protocole |
| `RUNTIME_CODE` | Code Python exécutable présent, non formellement prouvé en Lean |
| `PYTHON_SPEC` | Fichier Python servant de spécification, pas encore de preuve formelle |
| `LEAN_PROVEN` | Fichier prouvé formellement via Lean 4 + Lake (périmètre `proofs/lean/`) |
| `FORMAL_TLA` | Spécification TLA+ vérifiée par TLC (périmètre `formal/tla/`) |
| `PYTHON_TEST_ONLY` | Couverture test Python uniquement, pas de source runtime ni de preuve formelle |
| `DOC_ONLY` | Documentation Markdown ou rapport — aucun code exécutable associé |
| `PLACEHOLDER` | Stub minimal présent (ex. `jarvis_projection.py`) — logique non implémentée |
| `CANDIDATE` | Données ou calculs candidats, non finalisés (ex. `gencoin_candidate`) |
| `DRY_RUN` | Pipeline configuré mais jamais exécuté en production réelle |
| `PROD_BLOCKED` | Blocage explicite vers production (CORS wildcard, auth absente, etc.) |
| `PACK_PARTIAL` | Pack externe incomplet — certains fichiers présents, d'autres manquants |
| `ABSENT_UNDER_THIS_NAME` | Concept cherché sous ce nom exact — introuvable sous cette dénomination |
| `SOURCE_FOUND_UNDER_DIFFERENT_NAME` | Concept présent dans le repo, mais sous un nom différent de celui utilisé par Gemini/audio |
| `ABSENT_LOCAL_REPO` | Repo listé comme prioritaire mais absent du disque local |

---

## Statuts secondaires (complémentaires)

| Statut secondaire | Signification |
|-------------------|--------------|
| `NON_SOVEREIGN` | Le composant ne prend pas de décision autonome (ex. Brody, Shazam, BDF) |
| `KX108_BOUNDARY` | La décision finale appartient exclusivement à KX108 — le composant ne peut qu'alimenter |
| `READONLY` | Le module est strictement en lecture — aucune écriture, aucun ACT |
| `ADVISORY_ONLY` | Signal contextuel uniquement — ne peut pas déclencher d'action |
| `NEEDS_HUMAN_VALIDATION` | Gate humain obligatoire avant toute application |
| `CLAIM_SCOPE_RISK` | Risque de sur-interprétation publique — la source prouve moins qu'elle ne semble promettre |
| `PRODUCTION_MISSING` | Production non prête — bloqueurs techniques documentés |
| `FORMAL_PROOF_PENDING` | Preuve formelle Lean/TLA+ non encore réalisée pour ce composant |

---

## Hiérarchie de vérité (ordre décroissant de fiabilité)

```
1. Code / schema / registry réel (ce qui existe sur disque)
2. Rapport freeze / audit (docs/freeze/, .runtime_freezes/)
3. Index public / arborescence (ARBORESCENCE_COMPLETE.md)
4. README / doc générale
5. Audio / Gemini
6. Hypothèse
```

> Si plusieurs sources se contredisent, toujours privilégier le niveau le plus haut.
