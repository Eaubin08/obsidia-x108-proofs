# OBSIDIA F41 — Public Investor Demo Narrative Pack Report

**Timestamp:** 20260529_073000  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK  
**Version:** F41_V1  
**HEAD:** ff33bac  
**Parent tag:** BRODY_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_STATUS=PASS
CHAIN_COVERAGE=F32-F40
HEAD=ff33bac
PARENT_TAG=BRODY_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_PALIER_20260529
TYPE=NARRATIVE_DOCUMENTATION_ONLY
FILES_CREATED=7
FILES_MODIFIED=none
TESTS_INHERITED=103/103
SMOKE_CHECKS_INHERITED=474
BOUNDARY_KX108_ONLY=true
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — FICHIERS CRÉÉS

| Fichier | Rôle |
|---------|------|
| `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md` | Pitch public investisseur (problème, démo, preuves, positionnement) |
| `docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md` | Script oral 7 beats ~4 minutes avec commandes terminales |
| `docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` | Audit honnête du périmètre probatoire |
| `docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md` | FAQ 14 questions investisseur/jury |
| `docs/runtime/OBSIDIA_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_INDEX_20260529_073000.json` | Index structuré F41 avec SHA256 |
| `docs/runtime/OBSIDIA_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_REPORT_20260529_073000.md` | Ce rapport |
| `.runtime_freezes/F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_20260529_073000/MANIFEST_SHA256.json` | Freeze manifest avec hashes |

**Fichiers modifiés :** aucun.  
**Code modifié :** aucun.  
**Tests modifiés :** aucun.

---

## SECTION 2 — NATURE DE F41

F41 est une couche de narration publique construite sur le RC1 F40. Elle ne crée pas de nouveaux modules Python, routes API, ou tests. Elle hérite intégralement des preuves de F40 :

| Métrique héritée | Valeur |
|-----------------|--------|
| Tests unitaires | 103/103 PASS |
| Checks smoke cumulés | 474 |
| Preuves live-server | 3 (F34B, F36B, F38) |
| Routes API | 7 READY_READONLY |
| Tags git | 10/10 |
| Tokens interdits trouvés | 0 |
| Mutations | 0 |

---

## SECTION 3 — CONTENU NARRATIF

### Pitch public (`OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md`)

Structure : one-liner → problème → ce que fait Obsidia → démo live → preuves RC1 → pourquoi ça compte → domaines → stade actuel → positionnement concurrentiel.

SHA256 : `1207F37E1693B691D40ADF89C5C3439D724F0963B44199961C8D0E3C739547F4`

---

### Script oral (`OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md`)

7 beats (~4 minutes) : hook → problème → démarrage serveur → appel principal → frontière → chaîne de preuve → close. Inclut commandes de backup pour les pannes de démo.

SHA256 : `28C89A4BD550703B975CDE4098489B14621D5A06233CEE031386C02A6E03D601`

---

### Ce que ça prouve / ne prouve pas (`OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md`)

**Prouvé :** frontière vérifiable, tokens interdits absents, frontière sur vrai serveur, chaîne palier complète, KX108_ONLY à tous les niveaux, 4 domaines hétérogènes.

**Non prouvé :** preuve Lean formelle, kernel KX108 instancié, résistance adversariale, scalabilité, persistance/mémoire, intégration système complète.

SHA256 : `E03E65D712038615FFC3E4532235249680FC505CEBA48C9647FF86ECC8C01E75`

---

### FAQ investisseur/jury (`OBSIDIA_F41_INVESTOR_JURY_FAQ.md`)

14 questions couvrant : fondamentaux, preuve, valeur et positionnement, pratique. Questions difficiles adressées honnêtement (preuve formelle absente, kernel KX108 non instancié, résistance adversariale non testée).

SHA256 : `D0E00D65E6DEDA8BE7778BBC8C479A5FBCB0C0D6C08249D83C2513C70AD39A40`

---

## SECTION 4 — BOUNDARY CONTRACT F41

```
decision_authority  = KX108_ONLY   ✅
allowed_to_decide   = False        ✅
readonly            = True         ✅
advisory_only       = True         ✅
emits_act           = False        ✅
emits_verdict       = False        ✅
kernel_mutation     = False        ✅
x108_mutation       = False        ✅
neo4j_write         = False        ✅
memory_write        = False        ✅
graphiti_write      = False        ✅
runtime_execute     = False        ✅
```

---

## SECTION 5 — TOTAUX F41

| Métrique | Valeur |
|----------|--------|
| Paliers couverts | 12 (F32→F40 + F41) |
| Fichiers narratifs créés | 4 |
| Fichiers runtime créés | 3 (index, rapport, manifest) |
| Tests hérités | 103/103 |
| Checks smoke hérités | 474 |
| Code modifié | 0 |

---

## TERMINAL FINAL

```
F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_STATUS=PASS
TYPE=NARRATIVE_DOCUMENTATION_ONLY
HEAD=ff33bac
PARENT_TAG=BRODY_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_PALIER_20260529
FILES_CREATED=docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md,
              docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md,
              docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md,
              docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md,
              docs/runtime/OBSIDIA_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_INDEX_20260529_073000.json,
              docs/runtime/OBSIDIA_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_REPORT_20260529_073000.md,
              .runtime_freezes/F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_20260529_073000/MANIFEST_SHA256.json
FILES_MODIFIED=none
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F41 → tag BRODY_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_PALIER_20260529
```
