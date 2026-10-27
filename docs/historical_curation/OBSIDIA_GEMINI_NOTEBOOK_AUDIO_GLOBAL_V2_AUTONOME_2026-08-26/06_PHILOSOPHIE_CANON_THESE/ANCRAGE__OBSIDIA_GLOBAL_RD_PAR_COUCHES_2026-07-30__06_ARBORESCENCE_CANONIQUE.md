# ARBORESCENCE CANONIQUE — OBSIDIA v7 bis

```text
OBSIDIA_SQUELETTE_CHANTIER_v5/
├── 00_PILOTAGE/
├── 01_ETAT_DU_REEL/
│   ├── 01_FREEZE_NOYAU/
│   ├── 02_V3_V3_1_CANON/
│   ├── 03_FORMALISATION_MATH/
│   ├── 04_RECHERCHE_RAPPORTS/
│   ├── 05_CERTIFICATION_X108/
│   ├── 06_CORPUS_MASTER_ET_ZONES/
│   ├── 07_GOUVERNANCE_ABCD/
│   └── 08_SOURCES_COMPLEMENTAIRES/
├── 02_CORPUS_CANONIQUE/
│   ├── 01_17_BLOCS_161_PEPITES/
│   ├── 02_40_BLOCS_FONDAMENTAUX/
│   ├── 03_7_FLUX/
│   ├── 04_LTO_16D/
│   ├── 05_LOIS/
│   ├── 06_PROTOCOLes/
│   ├── 07_METRIQUES_INVARIANTS_OBJETS/
│   ├── 08_REGIMES_GEOMETRIES/
│   ├── 09_MEMOIRE_SEMANTIQUE_TOPOLOGIE/
│   ├── 10_AGENTS_ECOLOGIES/
│   ├── 11_ETHIQUE_ADELE/
│   └── 12_INFRASTRUCTURE_INSTITUTIONNEL_EXTENSIONS/
├── 03_ARCHITECTURE_OS/
│   ├── 01_MONDE_INTERNE_OS0_OS4/
│   ├── 02_COUCHES_PUBLIQUES_C0_C9/
│   └── 03_COUCHES_COMPLEMENTAIRES/
├── 04_PALIER_1/
├── 05_PALIER_2/
├── 06_PALIER_3_V4/
├── 07_REGISTRE_MAITRE/
├── 08_RUNTIME/
├── 09_TESTS/
├── 10_FREEZES/
├── 11_PALIER_4/
└── 12_RESERVOIR/
```

## Règles de placement
- `00_PILOTAGE` : règles globales et navigation
- `01_ETAT_DU_REEL` : artefacts, freezes, zips, dossiers de certification, masters
- `02_CORPUS_CANONIQUE` : composants nommés du corpus
- `03_ARCHITECTURE_OS` : couches OS, C0–C9 et couches complémentaires
- `04_PALIER_1` à `11_PALIER_4` : specs et feuille de route par palier
- `07_REGISTRE_MAITRE` : registre et vues filtrées
- `08_RUNTIME` : code exécutable
- `09_TESTS` : suites de tests
- `10_FREEZES` : snapshots figés
- `12_RESERVOIR` : différé / rejeté / hors périmètre

## Règle finale
Un objet sans place claire dans cette arborescence ne peut pas devenir actif.


## Ajouts v6
- `02_CORPUS_CANONIQUE/01_17_BLOCS_161_PEPITES/PEPITES_PAR_BLOC/`
- `03_ARCHITECTURE_OS/04_COUCHES_OS_B_OS_S/`
- `02_CORPUS_CANONIQUE/13_EXTENSIONS_CORPUS_ELARGI/`
- inventaires des archives V3.1 et du kernel proof freeze

---

## Corrections v7 bis appliquées
1. `03_ARCHITECTURE_OS/` est organisé en 4 familles actives :
   - `01_GRILLE_OS_CANONIQUE/`
   - `02_COUCHES_PERIPHERIQUES_ET_TRANSVERSES/`
   - `03_GRADIENT_D_EXPOSITION_C0_C9/`
   - `04_PONTS_VERS_LE_MONDE/`
2. `OS0–OS4` restent les couches canoniques actives.
3. `Sigma`, `Balance`, `AVDR`, `Pentade`, `Double verrou`, `Memzum`, `Noyau Omega`, `Toroïde` vivent en couches périphériques/transverses.
4. `Jarvis` n’est pas une couche OS : il vit dans `C2_HUB_JARVIS_PUBLIC.md`.
5. Les contenus v6 utiles restent archivés, mais leurs éléments actifs ont été réinjectés dans les fichiers v7 bis.
