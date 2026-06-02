# NPL_SOURCE_DISCOVERY_REPORT
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION

**Date** : 2026-06-02
**Mode** : SOURCE_DISCOVERY_EXTENDED_ONLY

---

## 1. Mode

```
SOURCE_DISCOVERY_EXTENDED_ONLY
```

Aucun patch runtime. Aucun commit. Aucun push.
Aucun adapter créé. Aucune spec finale créée. Aucun test exécutable créé.
Seuls les 6 fichiers du dossier `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/` ont été créés.

---

## 2. Pourquoi cet audit avant Plan 2

NPL (Narrative Provenance Layer) est un nouveau bloc conceptuel fourni par l'utilisateur. Avant de créer les specs Plan 2, il faut :

1. Vérifier si NPL existe déjà sous ce nom ou sous un autre nom dans les repos locaux.
2. Identifier les récepteurs Obsidia déjà existants qui peuvent recevoir les packets NPL.
3. Établir les boundaries KX108 — NPL est périphérique readonly, jamais décisionnel.
4. Classer les courants externes (Foucault, Gramsci, etc.) comme références, pas comme autorités.
5. Identifier les risques de claim-scope avant toute spec.

**Conclusion préliminaire** : NPL n'existe pas sous ce nom dans le repo — mais ses concepts s'ancrent naturellement dans des récepteurs déjà construits (Tree19, Tree24, Tree25, education_score.py, bias_gate.py, context_packet_builder_v2.py, x108_ingress).

---

## 3. Sources utilisateur prises en compte

| Source | Type | Statut |
|--------|------|--------|
| Texte conceptuel logique humaine / culture compressée | USER_PROVIDED_SOURCE_ONLY | Intégré dans les specs candidates |
| Architecture NPL proposée (arbo obsidia-npl) | USER_PROVIDED_SOURCE_ONLY | Intégrée dans la cartographie |
| Extraction Obsidia NPL | USER_PROVIDED_SOURCE_ONLY | Intégrée |
| Courants externes (Berger-Luckmann, Lakoff-Johnson, Foucault, Gramsci, Trouillot, Halbwachs/Assmann, Scott, Said, Spivak, Kuhn) | USER_PROVIDED_SOURCE_ONLY | Classés EXTERNAL_REFERENCE_REGISTRY — DOC_ONLY — NO_AUTHORITY — NO_DECISION |

---

## 4. Repos inspectés

| Repo | Présent | Statut | Notes |
|------|---------|--------|-------|
| `obsidia-x108-proofs_REMOTE_A5F21C6B` | OUI | Inspecté en détail | Repo principal — toutes les sources vérifiées |
| `obsidia-x108-proofs` | OUI | Non inspecté en détail | Même codebase |
| `_obsidia-local-workspace` | OUI | Non pertinent NPL | Données privées quarantinées |
| `obsidiashell-main` | OUI | Non inspecté | Hors scope NPL |
| `obsidia-engine-candidate` | OUI | Non inspecté | Hors scope NPL |
| `Demo-obsidia-x108-proof` | NON | ABSENT_LOCAL_REPO | — |
| `agi-vison` | NON | ABSENT_LOCAL_REPO | — |
| `bank-robo` | NON | ABSENT_LOCAL_REPO | — |
| `Obsidia-lab-trad` | NON | ABSENT_LOCAL_REPO | — |
| `preprint-conscience` | NON | ABSENT_LOCAL_REPO | — |
| `obsidia-npl` (nouveau repo proposé) | NON | ABSENT_LOCAL_REPO | À ne pas créer sans validation humaine |

---

## 5. Résumé exécutif

### NPL confirmé comme bloc à intégrer

NPL est un nouveau bloc périphérique cohérent avec l'architecture Obsidia — ses concepts s'ancrent dans des récepteurs existants (Tree34, education, bias, language router, context packet, x108_ingress). NPL doit être spécifié avant d'être implémenté.

### NPL doit rester périphérique readonly

```
NPL ↛ ACT
NPL ↛ ALLOW / HOLD / BLOCK
NPL ↛ KERNEL
NPL → contexte + signal + provenance + hypothèse uniquement
```

Ce principe est déjà établi par le non_decision_contract de Tree34 : *"Tree34 ↛ ACT. Toute décision finale appartient à X-108."* NPL hérite de cette règle.

### NPL doit se brancher aux récepteurs existants

NPL ne crée pas de nouveaux systèmes — il enrichit les récepteurs existants :
- Tree19 (Culture), Tree24 (Mémoire), Tree25 (Histoire), Tree27 (Vérité), Tree10 (Langage) → signaux d'activation
- `education_score.py` → education_blockage_packet
- `bias_gate.py` → common_sense_capture + manipulation_risk_signal
- `language_router.py` → language_encoding_score
- `context_packet_builder_v2.py` → HumanLogicPacket étendu
- `x108_ingress/readonly_context_ingress.py` → NPL_TO_X108_BOUNDARY
- `graphiti_readonly_bridge.py` → NPL_TO_GRAPHITI (NO_GRAPHITI_WRITE par défaut)
- `brody_context_query.py` → NPL_TO_BRODY (readonly)

### NPL nécessite claim-scope strict

Voir `NPL_CLAIM_SCOPE_WARNINGS.md` — 17 interdictions publiques absolues.
Point critique : les courants externes (Foucault, Gramsci, Trouillot, etc.) sont des **références bibliographiques**, pas des **preuves algorithmiques**.

---

## 6. Source map par bloc NPL

### Bloc A — NPL Core

| Élément | Trouvé dans le repo | Récepteur existant | Statut |
|---------|---------------------|--------------------|--------|
| NPL_CANONICAL_SPEC | NON | `docs/PROOF_SCOPE.md` (modèle de structure) | ABSENT_UNDER_THIS_NAME → SPEC_CANDIDATE |
| NPL_READONLY_BOUNDARY | NON (concept) | `periphery/x108_ingress/readonly_context_ingress.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| NPL_TO_X108_BOUNDARY | NON (concept) | `periphery/x108_ingress/x108_context_boundary.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| NPL_AUTHORITY_BOUNDARY | NON (concept) | `periphery/reverse_os/action_projection_readonly.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| NPL_RSSI_NON_MANIPULATION | NON (concept nommé) | `periphery/bias/bias_gate.py` + `bias_trace.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |

---

### Bloc B — Packets

| Packet | GitHub | Récepteur | Statut | Risque |
|--------|--------|-----------|--------|--------|
| HUMAN_LOGIC_PACKET | ABSENT | `context_packet_builder_v2.py` | SPEC_CANDIDATE | Diagnostic interdit |
| NARRATIVE_PROVENANCE_PACKET | ABSENT | `document_ingestion_pipeline.py` | SPEC_CANDIDATE | Certitude de provenance interdite |
| CULTURAL_MATRIX_PACKET | ABSENT | Tree19 Culture | SPEC_CANDIDATE | Hiérarchisation culturelle interdite |
| ARCHIVE_GAP_PACKET | ABSENT | Tree25 Histoire | SPEC_CANDIDATE | Absence ≠ preuve de manipulation |
| TRUTH_REGIME_PACKET | ABSENT | Tree27 Vérité | SPEC_CANDIDATE | Vérité unique interdite |
| DEFEATED_MEMORY_SIGNAL | ABSENT | Tree24 + Tree25 | SPEC_CANDIDATE | Mémoire vaincue ≠ "vraie" vérité |
| HIDDEN_TRANSCRIPT_PACKET | ABSENT | `context_packet_builder_v2.py` contradictions | SPEC_CANDIDATE | Verdict sur intention interdit |
| METAPHOR_MATRIX_PACKET | ABSENT | Tree04 + Tree08 | SPEC_CANDIDATE | Interprétation finale interdite |
| EDUCATION_BLOCKAGE_PACKET | ABSENT (nommé NPL) | `education_score.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | Diagnostic d'apprentissage interdit |

---

### Bloc C — Concepts

| Concept | GitHub | Récepteur | Statut |
|---------|--------|-----------|--------|
| LOGIC_AS_CULTURE_COMPRESSED | ABSENT (terme) | Tree19 + Tree10 | SPEC_CANDIDATE → inclus dans CULTURAL_MATRIX_SPEC |
| HUMAN_THINKS_FROM_A_WORLD | ABSENT (terme) | Tree01 + Tree06 | SPEC_CANDIDATE → inclus dans HUMAN_LOGIC_PACKET |
| WINNER_HISTORY_AND_DEFEATED_MEMORY | ABSENT | Tree25 + Tree27 | SPEC_CANDIDATE |
| ARCHIVE_GAP_AS_CONTEXT_SIGNAL | ABSENT | Tree25 | SPEC_CANDIDATE |
| COMMON_SENSE_AS_CAPTURED_NARRATIVE | ABSENT (terme) | `bias_gate.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| LANGUAGE_AS_CULTURAL_ENCODING | ABSENT (terme) | `language_router.py` + Tree10 | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| FUTURES_LOST_BY_HISTORY | ABSENT | Tree23 + Tree29 | SPEC_CANDIDATE (P3) |
| OFFICIAL_ARCHIVE_AND_WARM_MEMORY | ABSENT | Tree24 | SPEC_CANDIDATE |

---

### Bloc D — Courants externes

**Statut uniforme pour tous** : `EXTERNAL_REFERENCE_REGISTRY — DOC_ONLY — NO_AUTHORITY — NO_DECISION`

| Courant | GitHub | Statut |
|---------|--------|--------|
| Berger-Luckmann | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Lakoff-Johnson | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Foucault | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Gramsci | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Trouillot | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Halbwachs / Assmann | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| James Scott | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Edward Said | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Spivak | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |
| Kuhn | ABSENT | USER_PROVIDED_SOURCE_ONLY → EXTERNAL_REFERENCE_REGISTRY |

> Ces courants INFORMENT les specs. Ils ne FONDENT PAS le runtime. Ils ne sont PAS des autorités dans le système Obsidia.

---

### Bloc E — Branchements NPL → Obsidia existant

| NPL Branch | Récepteur Obsidia | Fichier réel | Boundary |
|------------|------------------|--------------|---------|
| NPL_TO_GRAPHITI | `graphiti_readonly_bridge.py` | `sigma/graphiti_readonly_bridge.py` | `NO_GRAPHITI_WRITE` sauf gate humain |
| NPL_TO_BRODY | `brody_context_query.py` | `periphery/brody/brody_context_query.py` | Signal contextuel uniquement |
| NPL_TO_OS_TRAD | `language_router.py` | `periphery/language/language_router.py` | IR candidate readonly |
| NPL_TO_SIGMA | `sigma/run_pipeline.py` | `sigma/run_pipeline.py` | CONTEXT_ONLY |
| NPL_TO_TREE34 | Trees 10/17/18/19/24/25/27 | `04_ARBRES_34_TENSOR_MATRIX/ARBRE_*/` | non_decision_contract respecté |
| NPL_TO_EDUCATION | `education_score.py` | `periphery/education/education_score.py` | ADVISORY_ONLY |
| NPL_TO_X108 | `readonly_context_ingress.py` | `periphery/x108_ingress/` | CONTEXT_ONLY — KX108_ONLY |
| NPL_TO_RSSI | `bias_gate.py` | `periphery/bias/bias_gate.py` | manipulation_risk_signal obligatoire |

---

### Bloc F — Métriques NPL

**Toutes les métriques NPL** sont des scores probabilistes dans [0,1].
**Aucune** ne peut produire un verdict final.
**Toutes** doivent inclure `provenance_uncertainty` et `manipulation_risk_signal`.

---

### Blocs G — Tests futurs

8 tests à créer au Plan 2. Voir `NPL_SOURCE_TO_SPEC_MAPPING.md` Bloc G.
Point clé : `test_education_student_blockage_packet` = extension de `tests/periphery/test_education_score.py` (existant).

---

## 7. Rattachement Obsidia existant

| NPL Block | Récepteur Obsidia | Source Obsidia | Statut | Boundary |
|-----------|------------------|----------------|--------|---------|
| Cultural signals | Tree19 Culture | `ARBRE_19__Arbre_de_la_Culture/` | DOC_ONLY + non_decision_contract | Tree34 ↛ ACT |
| Memory signals | Tree24 Mémoire | `ARBRE_24__Arbre_de_la_Memoire/` | DOC_ONLY + non_decision_contract | Tree34 ↛ ACT |
| History signals | Tree25 Histoire | `ARBRE_25__Arbre_de_l_Histoire/` | DOC_ONLY + non_decision_contract | Tree34 ↛ ACT |
| Truth regime | Tree27 Vérité | `ARBRE_27__Arbre_de_la_Verite/` | DOC_ONLY + non_decision_contract | Tree34 ↛ ACT |
| Language encoding | Tree10 + language_router | `ARBRE_10__Arbre_du_Langage/` + `periphery/language/language_router.py` | DOC_ONLY + RUNTIME_CODE | authority_claim_detected → BLOCK |
| Education blockage | Education score | `periphery/education/education_score.py` | RUNTIME_CODE + ADVISORY_ONLY | X108 décide |
| Common sense intercept | Bias gate | `periphery/bias/bias_gate.py` | RUNTIME_CODE | gate=HOLD si biais non validé |
| Context packet | ContextPacket V2 | `periphery/context/context_packet_builder_v2.py` | RUNTIME_CODE | `can_decide=False`, `allowed_to_act=False` |
| X108 boundary | X108 Context Ingress | `periphery/x108_ingress/readonly_context_ingress.py` | RUNTIME_CODE + READONLY | `can_emit_act=False`, `can_write_memory=False` |
| Memory agent | MEMOIRE_PERSONNELLE_OBSIDIA | `agents_52.registry.json` | SOURCE_CANON | readonly |
| History agent | HUMAN_HISTORY_MAPPER, FRISE_HUMAINE | `agents_52.registry.json` | SOURCE_CANON | readonly |
| External refs agent | RECHERCHE_EXTERNE | `agents_52.registry.json` | SOURCE_CANON | EXTERNAL_REFERENCE_REGISTRY |
| Sovereignty guard | DATA_SOVEREIGNTY_GUARD, ANTI_DISPERSION | `agents_52.registry.json` | SOURCE_CANON | NPL ne doit pas diluer X108 |
| OS Audit / OS Trad | OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md | `apps/obsidia-workbench/` | DOC_ONLY | IR candidate readonly |
| Graphiti readonly | graphiti_readonly_bridge.py | `sigma/graphiti_readonly_bridge.py` | RUNTIME_CODE + READONLY | NO_GRAPHITI_WRITE |
| Brody readonly | brody_context_query.py | `periphery/brody/brody_context_query.py` | RUNTIME_CODE + READONLY | signal contextuel — pas décision |

---

## 8. Nouveaux éléments à ajouter au Plan 2

**Specs P0** (bloquantes) :
1. `specs/npl/NPL_CANONICAL_SPEC.md`
2. `specs/npl/NPL_READONLY_BOUNDARY_SPEC.md`
3. `specs/npl/NPL_TO_X108_BOUNDARY_SPEC.md`
4. `specs/npl/HUMAN_LOGIC_PACKET_SPEC.md`
5. `specs/npl/NARRATIVE_PROVENANCE_PACKET_SPEC.md`
6. `specs/npl/NPL_RSSI_NON_MANIPULATION_SPEC.md`

**Specs P1** :
7. `specs/npl/CULTURAL_MATRIX_SPEC.md`
8. `specs/npl/TRUTH_REGIME_SPEC.md`
9. `specs/npl/ARCHIVE_GAP_SPEC.md`
10. `specs/npl/WINNER_NARRATIVE_SPEC.md`
11. `specs/npl/DEFEATED_MEMORY_SPEC.md`
12. `specs/npl/EDUCATION_BLOCKAGE_SPEC.md`

**Specs P2/P3** :
13-17. Voir `NPL_SOURCE_TO_SPEC_MAPPING.md`

---

## 9. Risques

| Risque | Description | Garde |
|--------|-------------|-------|
| Manipulation narrative | NPL présenté comme détecteur objectif de vérité | `provenance_uncertainty` obligatoire |
| Vérité culturelle → vérité finale | Un score culturel présenté comme verdict | `NO_VERDICT_FINAL` absolu |
| Courant externe → preuve | Foucault/Gramsci citées comme autorités algorithmiques | `EXTERNAL_REFERENCE_REGISTRY — NO_AUTHORITY` |
| NPL → verdict moral | "Cet humain pense de façon dominée" | Interdit dans NPL_CLAIM_SCOPE_WARNINGS |
| NPL écrit mémoire sans gate | Graphiti write déclenché par signal NPL | `NO_GRAPHITI_WRITE`, `NO_MEMORY_WRITE` par défaut |
| NPL passe dans kernel | Packet NPL modifie une preuve ou un seal | `NO_KERNEL_MUTATION` absolu |
| NPL produit action éducative intrusive | Education blockage → action correctrice | ADVISORY_ONLY — X108 décide |
| Diagnostic psychologique implicite | archive_gap → "il y a eu trauma" | Interdit — signal d'absence uniquement |
| Jcoin-type dilution | Nouveau concept (NPL) présenté comme déjà prouvé | Source réelle avant spec — spec avant runtime |

---

## 10. Verdict

```
NPL_PLAN1_EXTENSION_READY
```

**Justification** :
- Concepts NPL cartographiés — tous ABSENT_UNDER_THIS_NAME mais tous ancrés dans des récepteurs existants
- 5 récepteurs P0 identifiés avec chemins exacts
- Tree34 déjà équipé de `non_decision_contract.md` — NPL hérite directement
- Education, bias, language_router — récepteurs prêts à être étendus
- Courants externes classés EXTERNAL_REFERENCE_REGISTRY — pas d'autorité runtime
- Claim-scope warnings documentés (17 interdictions)
- Plan 2 input prêt : 17 specs candidates, 10 agents récepteurs, 8 tests futurs
- Aucun fichier runtime modifié
- Aucun commit, aucun push
