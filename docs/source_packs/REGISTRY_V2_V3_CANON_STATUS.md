# Registry V2 / V3 — Canon Status

**Généré :** 2026-06-03  
**Palier :** P31  
**Décision globale :** `LOCAL_ONLY — ARCHIVE_REFERENCE`

---

## Registry V2 — `OBSIDIA_COMPONENT_GROUP_REGISTRY_V2_20260602_125604/`

### Contenu (13 fichiers)

| Fichier | Taille | Rôle |
|---------|--------|------|
| `00_git_tracked_files.txt` | 376,703 B | Inventaire complet des fichiers git trackés |
| `00_local_untracked_files.txt` | 24,250 B | Fichiers locaux non trackés |
| `01_root_counts_git_tracked.csv` | 510 B | Comptage par dossier racine |
| `02_local_untracked_root_counts.csv` | 210 B | Comptage untracked par dossier |
| `03_CANONICAL_GROUP_REGISTRY_V2.csv` | 3,021 B | **Registre canonique V2** |
| `README.md` | 428 B | Description |
| `SPLIT_apps.csv` | 75 B | Split apps/ |
| `SPLIT_docs.csv` | 3,311 B | Split docs/ |

### Fichier clé : `03_CANONICAL_GROUP_REGISTRY_V2.csv`
- Colonnes : `canonical_group, subgroup, source_path, source_corpus, file_count, module, pepite_family, domain, runtime_status, boundary_status, keep_action`
- 30 lignes de données

### Relation avec le source registry runtime
Ce registre est une **cartographie des dossiers repo** (canonique grouping), pas un registre des packs source ZIP. Il ne référence pas `source_file_registry.json` directement.

### Décision
`LOCAL_ONLY` — Ne pas committer le dossier complet (376 KB de listes de fichiers git). Seul `03_CANONICAL_GROUP_REGISTRY_V2.csv` a une valeur documentaire.

---

## Registry V3 — `OBSIDIA_COMPONENT_SPLIT_V3_20260602_125929/`

### Contenu (12 fichiers)

| Fichier | Taille | Rôle |
|---------|--------|------|
| `SPLIT_apps_DEPTH1.csv` | 75 B | Apps split depth 1 |
| `SPLIT_apps_DEPTH2.csv` | 4,717 B | Apps split depth 2 |
| `SPLIT_apps_DEPTH3.csv` | 6,192 B | Apps split depth 3 |
| `SPLIT_docs_DEPTH1.csv` | 3,311 B | Docs split depth 1 |
| `SPLIT_docs_DEPTH2.csv` | 46,559 B | Docs split depth 2 |
| `SPLIT_docs_DEPTH3.csv` | 50,512 B | Docs split depth 3 |
| `SPLIT_periphery_DEPTH1.csv` | 4,522 B | Periphery split depth 1 |
| `SPLIT_periphery_DEPTH2.csv` | 40,360 B | Periphery split depth 2 |

### Contenu
Ce répertoire contient des analyses de découpe du repo à différentes profondeurs. Les fichiers DEPTH2/DEPTH3 sont volumineux (40-50 KB chacun) et représentent des snapshots d'exploration intermédiaires.

### Décision
`LOCAL_ONLY — EXCLUDE` — Trop volumineux pour être commité. Valeur analytique uniquement. Les données sont dérivées du repo lui-même et peuvent être recalculées.

---

## Comparaison Corpus Map V4 vs Registry V2

| Critère | Corpus Map V4 | Registry V2 `03_CANONICAL_GROUP_REGISTRY_V2.csv` |
|---------|---------------|--------------------------------------------------|
| Taille | 6 KB | 3 KB |
| Lignes | 28 | 30 |
| Colonnes | 10 | 11 |
| Orientation | Groupes canoniques + action | Groupes + domaine + boundary |
| Valeur | Plus orientée action (KEEP/ARCHIVE) | Plus orientée domaine/module |
| Décision | **COMMIT** | LOCAL_ONLY (complémentaire) |

---

## Relation avec source_file_registry.json (runtime)

Aucun de ces registres n'est utilisé par le runtime source. Le seul registre utilisé par le runtime est :
- `runtime_wiring/source_registry/source_file_registry.json` (15 298 entrées, 7 familles)

Ces registres V2/V3 sont des outils d'inventaire humain pour la gouvernance du repo, pas des composants runtime.

---

## Décision finale

| Artefact | Décision | Raison |
|----------|----------|--------|
| Corpus Map V4 (6 KB CSV) | **COMMITÉ P31** | Référence canonique, petite taille |
| Registry V2 `03_CANONICAL_GROUP_REGISTRY_V2.csv` | LOCAL_ONLY | Redondant avec Corpus Map V4 |
| Registry V2 complet (dir) | LOCAL_ONLY | Trop lourd (376 KB listes git) |
| Registry V3 complet (dir) | LOCAL_ONLY — EXCLUDE | Trop volumineux, redérivable |
