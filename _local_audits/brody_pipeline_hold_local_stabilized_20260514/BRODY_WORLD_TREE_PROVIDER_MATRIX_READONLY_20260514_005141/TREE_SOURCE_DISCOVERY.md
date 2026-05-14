# TREE_SOURCE_DISCOVERY
## Mission: BRODY_WORLD_TREE_PROVIDER_MATRIX_READONLY
## Timestamp: 20260514_005141
## Status: TREE_SOURCE_FOUND=true

---

## Anti-Invention Rule

> "Ne pas inventer de familles génériques de providers. Les familles doivent venir des arbres existants / 34 arbres / architecture déjà présente dans le corpus."

This matrix uses ONLY trees found in the actual corpus. No invented families. No generic provider categories.

---

## Discovery Method

Four sequential Python scripts queried Neo4j (bolt://127.0.0.1:7688) against the BrodyMemoryDoc label (3,267 nodes).

| Script | Purpose | Result |
|---|---|---|
| `_tree_discovery.py` | Keyword hit counts, T-numbered titles | T01–T12 found in titles, 17 tags |
| `_tree_discovery2.py` | Family hits, 34_arbres-tagged docs | Family keyword counts confirmed |
| `_tree_discovery3.py` | Full T-named docs with names | T01–T12 named from corpus titles |
| `_tree_discovery4.py` | arbres_34.canon.json + registry full text | doc_canon_count=34 confirmed |
| `_tree_discovery5.py` | Full registry parse T01–T34 | ALL 34 trees enumerated |

---

## Source Documents Found in BrodyMemoryDoc Corpus

| Title | Type |
|---|---|
| `arbres_34.canon.json` | Canonical tree definitions, 34 entries |
| `arbres_34.registry.json` | Registry with id, name, family per tree |
| `arbres_34.diff.json` | Diff/delta record |
| `arbres_34.raw_image.json` | Raw image snapshot |

---

## Confirmed: 8 Families (not 7)

The corpus shows **8 families**, not 7 as initially estimated. Family VIII_OBSIDIA_AGI contains T30–T34.

| Family Code | Range | Tree Count |
|---|---|---|
| I_FONDAMENTAUX | T01–T05 | 5 |
| II_COGNITIFS | T06–T10 | 5 |
| III_CONNAISSANCE | T11–T15 | 5 |
| IV_RELATIONNELS_SOCIAUX | T16–T19 | 4 |
| V_ACTION_TRANSFORMATION | T20–T22 | 3 |
| VI_TEMPORELS_MEMORIELS | T23–T25 | 3 |
| VII_META_STRUCTURELS | T26–T29 | 4 |
| VIII_OBSIDIA_AGI | T30–T34 | 5 |

**TOTAL: 34 trees across 8 families**

---

## Keyword Hit Counts (BrodyMemoryDoc corpus)

| Keyword | Doc Hits |
|---|---|
| X108 | 2557 |
| CANON | 850 |
| PEPITE | 374 |
| AGENTS | 389 |
| SHAZAM | 108 |
| BDF | 139 |
| MMONDE | 53 |
| MCP | 76 |
| HEXAFLUX | 51 |
| atlas | 50 |
| LTCU | 27 |

---

TREE_SOURCE_FOUND=true  
TREE_SOURCE_INVENTED=false  
DOC_CANON_COUNT=34  
FAMILY_COUNT=8  
DISCOVERY_COMPLETE=true
