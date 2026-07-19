# Corpus Map V4 — Canon Status

**Généré :** 2026-06-03  
**Palier :** P31  
**Fichier source :** `OBSIDIA_CANONICAL_COMPONENT_CORPUS_MAP_V4_20260602_130452.csv`  
**Décision :** `COMMIT_CANDIDATE` — valeur de référence documentaire

---

## Métriques

| Attribut | Valeur |
|----------|--------|
| Taille | 6,058 bytes |
| Lignes totales | 28 |
| Lignes données | 27 |
| Encodage | UTF-8-BOM |
| Statut git | `??` local-only avant P31 |

---

## Colonnes

```
canonical_corpus, canonical_subgroup, source_patterns, known_file_count,
component_type, module_family, pepite_family, domain_family, status, action
```

---

## Familles couvertes (sample)

| canonical_corpus | component_type | status | action |
|-----------------|----------------|--------|--------|
| APPS_WORKBENCH | INTERFACE | ACTIVE_UI | KEEP_RUNTIME |
| BRODY_MEMORY_READONLY | MEMORY_RUNTIME | — | — |
| BUS_LAYER | RUNTIME | ACTIVE_READONLY | KEEP_RUNTIME |
| CORE_AUTHORITY | CORE | ACTIVE_SPEC_RUNTIME | KEEP_CORE_OR_OFFICIAL_REVIEW |
| ... | ... | ... | ... |

Le fichier couvre les composants principaux du repo : workbench UI, mémoire Brody, bus, autorité X108, et autres.

---

## Relation avec le source registry runtime

Le Corpus Map V4 est une **vue d'ensemble architecturale** du repo, pas un registre des packs sources. Il documente les groupes canoniques de composants (ex. `APPS_WORKBENCH`, `CORE_AUTHORITY`) mais ne référence pas directement les familles `source_file_registry.json` (ATLAS, NPL, COGNITIVE, etc.).

Il est complémentaire : le source registry runtime = entrées fichiers par famille source ; le Corpus Map = cartographie des composants repo.

---

## Décision

**COMMIT_CANDIDATE** — Commité dans P31 sous `docs/source_packs/CORPUS_MAP_V4_20260602.csv`.

**Justification :**
- Petite taille (6 KB) — acceptable
- Valeur documentaire : référence canonique des groupes de composants
- Risque : NONE — lecture seule, pas de modification du runtime

---

## Risques

| Risque | Niveau | Note |
|--------|--------|------|
| Stale par rapport au repo actuel | LOW | 27 lignes = snapshot 2026-06-02, repo évolue |
| Duplication avec Registry V2 | LOW | Corpus Map V4 = plus concis et orienté action |
| Contient des noms propriétaires | NONE | Colonnes publiques |

---

## Prochain palier

P32 : Vérifier si le Corpus Map V4 couvre la famille `OS_TRAD_REVERSE_OS` et l'ajouter si nécessaire.
