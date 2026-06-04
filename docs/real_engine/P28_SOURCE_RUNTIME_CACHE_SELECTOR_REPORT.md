# P28 — Source Runtime Cache & Smart Family Selection Report

**Branch:** p10-real-engine-controlled-bridge  
**Date:** 2026-06-03  
**Status:** P28_SOURCE_RUNTIME_CACHE_SELECTOR_READY

---

## Résumé

P28 rend la couche source runtime exploitable en production :
- Cache TTL 60s pour registry et disponibilité des packs (évite 15 298 lectures JSON à chaque requête)
- Sélection intelligente de familles selon les mots-clés du message Brody
- Stats de cache exposées dans le payload API et dans `/api/runtime-wiring/preview`
- Correction d'un bug latent `pathlib.os.sep` dans le loader de répertoires (révélé par NPL via le selector)

---

## Composants créés / modifiés

| Fichier | Action | Rôle |
|---------|--------|------|
| `runtime_wiring/source_runtime/source_runtime_cache.py` | Créé | Cache TTL 60s pour registry + pack availability |
| `runtime_wiring/source_runtime/source_family_selector.py` | Créé | Sélection de familles par mots-clés du message |
| `runtime_wiring/source_runtime/source_runtime_query.py` | Modifié | Utilise le cache + `except Exception` élargi |
| `runtime_wiring/source_runtime/brody_source_context_bridge.py` | Modifié | Utilise selector + cache stats + nouveaux champs |
| `runtime_wiring/source_runtime/readonly_content_loader.py` | Bugfix | `pathlib.os.sep` → `joinpath(*parts)` |
| `apps/obsidia_api/routes/runtime_wiring_preview.py` | Modifié | Ajoute section `source_runtime_*` dans la réponse |

---

## Cache TTL

```
registry_ttl_seconds: 60
pack_avail_ttl_seconds: 60
```

**Fonctionnement :**
- Premier appel : charge registry JSON (15 298 entrées, ~14 MB) → cache_misses++
- Appels suivants (< 60s) : retourne depuis cache → cache_hits++
- `clear_cache()` disponible pour les tests (force reload)
- Stats : `cache_hits`, `cache_misses`, `cache_hit_rate`

**Gain de performance :**
- Avant : chaque requête Brody lisait 15 298 entrées JSON depuis disque
- Après : 1 lecture disque par 60s, toutes les requêtes intermédiaires depuis mémoire

---

## Smart Family Selector

Mapping message → familles par score de mots-clés :

| Mots-clés détectés | Famille sélectionnée |
|-------------------|---------------------|
| x108, kernel, governance, brody, cognitive | COGNITIVE_REINTEGRATION |
| rgpd, gdpr, conformité, privacy | RSSI_RGPD |
| atlas, arbre, tree, architecture | ATLAS |
| compliance, data governance, audit, policy | COMPLIANCE_DATA_GOVERNANCE |
| sécurité, security, rssi, cyber | RSSI_SECURITY_PRESENTATION |
| timeverse, temporal, time, signal | EXTERNAL_SIGNALS |
| npl, narrative, provenance, graphiti | NARRATIVE_PROVENANCE_LAYER |

**Fallback :** si aucun mot-clé → top 3 familles par défaut (COGNITIVE, ATLAS, NPL)

**Résultat :** au lieu d'interroger toutes les familles disponibles, le selector cible les 3 plus pertinentes, réduisant les hydratations inutiles.

---

## Nouveaux champs API (brody_source_context_bridge)

| Champ | Type | Description |
|-------|------|-------------|
| `source_pack_selected_families` | list | Familles sélectionnées par le selector |
| `source_pack_selection_desc` | str | Description de la sélection (KEYWORD_MATCH ou DEFAULT_FALLBACK) |
| `source_pack_keyword_matched` | bool | True si des mots-clés ont matchés |
| `source_pack_cache_hit` | bool | True si le registry était en cache lors de l'appel |
| `source_pack_runtime_stats` | dict | Stats complètes du cache (hits, misses, hit_rate) |

---

## Nouveaux champs API (/api/runtime-wiring/preview)

| Champ | Valeur |
|-------|--------|
| `source_runtime_available` | True |
| `source_runtime_cache_enabled` | True |
| `source_runtime_families` | Liste des 7 familles |
| `source_runtime_last_stats` | Dict stats cache |
| `brody_context_bridge_available` | True |
| `real_readonly_hydration_available` | True |

---

## Bugfix : pathlib.os.sep

**Problème :** `readonly_content_loader.py` utilisait `pathlib.os.sep` dans `_load_from_directory()`. `pathlib.os` n'est pas un attribut public de `pathlib` — cela causait `AttributeError` lors du chargement de fichiers depuis un répertoire extrait (NPL).

**Impact :** Le bug était masqué en P26/P27 parce que le selector aléatoire ne choisissait pas NPL systématiquement. Le selector P28 cible NPL explicitement quand le message contient "npl" ou "narrative", révélant le bug.

**Fix :** `resolved.resolved_path.joinpath(*internal_path.replace("\\", "/").split("/"))`

---

## Résultats des tests

### P28 (25/25)
```
tests/test_source_runtime_cache_p28.py         7 passed in 2.08s
tests/test_source_family_selector_p28.py       11 passed in 0.01s
tests/api/test_brody_source_pack_context_p28.py 7 passed in 5.08s
```

### Régression totale (121/121)
```
P26 + P27 + P28 + p8c + p9b + p10c + p10d = 121 passed in 11.07s
```

---

## Preuves de sécurité

- Cache uniquement pour métadonnées (entrées registry, disponibilité des packs) — jamais pour le contenu des fichiers
- `clear_cache()` ne supprime aucun fichier — reset mémoire uniquement
- Les invariants X108/OS3/no-ACT restent inchangés dans toute la chaîne
- `FORBIDDEN_CONTENT_PASS` confirmé

---

## Limites restantes

- Cache in-process uniquement (module-level globals) — pas de cache distribué
- TTL 60s fixe — pas de configuration externe pour l'instant
- Le selector utilise des mots-clés simples (substring) — pas de NLP sémantique
- Workbench UI (React/Vite) non mise à jour — P29

---

## Prochain palier : P29

- Surface Workbench React : afficher `source_runtime_families`, `cache_hit_rate`, `entries_used` dans le panneau Runtime
- TTL configurable via variable d'environnement
- Amélioration du selector : stemming, synonymes, poids par longueur de match
- Hydration partielle asynchrone pour réduire la latence Brody
