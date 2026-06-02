# NPL_RAW_SEARCH_LOG
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION
# Date: 2026-06-02

> Journal brut des recherches effectuées pour le Plan 1 Bis NPL.

---

## Sources utilisateur prises en compte

| Source | Type | Présence locale |
|--------|------|-----------------|
| Texte logique humaine / culture compressée | USER_PROVIDED_SOURCE_ONLY | Fourni dans la conversation |
| Architecture NPL / arbo proposée (obsidia-npl) | USER_PROVIDED_SOURCE_ONLY | Non présent localement |
| Extraction NPL concepts | USER_PROVIDED_SOURCE_ONLY | Fourni dans la conversation |
| Courants externes (Berger, Lakoff, Foucault, Gramsci, Trouillot, Halbwachs, Scott, Said, Spivak, Kuhn) | USER_PROVIDED_SOURCE_ONLY | Non présents dans le repo |

---

## Repos inspectés

| Repo | Présent | Résultat |
|------|---------|---------|
| `obsidia-x108-proofs_REMOTE_A5F21C6B` | OUI | Repo principal — inspecté en détail |
| `obsidia-x108-proofs` | OUI | Non inspecté en détail (même codebase) |
| `_obsidia-local-workspace` | OUI | Données privées quarantinées — non pertinent NPL |
| `obsidiashell-main` | OUI | Non inspecté — hors scope NPL |
| Repos Priorité 2 | NON VÉRIFIÉS | ABSENT_LOCAL_REPO (Demo, agi-vison, bank-robo, Obsidia-lab-trad, etc.) |

---

## Commandes exécutées

### 1. Grep NPL / Narrative Provenance / Human Logic
```bash
grep -rl "NPL|Narrative.Provenance|Human.Logic.Packet|Narrative.Provenance.Packet|culture.compress|logique.humaine|truth.regime|hidden.transcript|conceptual.metaphor|archive.gap|mémoire.vaincue|récit.vainqueur|subaltern|common.sense.capture|bon.sens.captur|futures.lost" .
# → 1 résultat : periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md
# → Contient uniquement les sources docx bruts (BDF, HexaFlux, Shazam) — pas de NPL nommé
```

### 2. Grep OS Trad / IR / semantic mapper / réintégration cognitive
```bash
grep -rl "OS.Trad|OS_Trad|Obsidia.IR|semantic.mapper|phrase_to_structure|IR.candidate|réintégration.cognitive|cultural.matrix|education.blockage" .
# → apps/obsidia-workbench/OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md
# → apps/obsidia-workbench/OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md
# → .deepseek/pastes/ (non pertinent — pastes bruts)
```

### 3. Grep éducation / courants externes
```bash
grep -rl "education|student|Berger|Luckmann|Lakoff|Foucault|Gramsci|Trouillot|Halbwachs|Assmann|Scott.*hidden|Kuhn.*paradigm|Said.*gaze|Spivak|hegemony|collective.memory" .
# → docs/education/README.md
# → docs/EDUCATION_BIAS_LANGUAGE_BACKLOG_REPORT.md
# → periphery/education/education_score.py
# → apps/obsidia_api/routes/periphery_ops.py
# → Aucun courant externe (Berger, Foucault, etc.) trouvé dans le repo
```

### 4. Structure MMONDE complète
```bash
ls periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/
# → 20 dossiers (00_INDEX à 20_DEMO_MINIMALE) + fichiers Python
```

### 5. 34 arbres complet
```bash
ls periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/04_ARBRES_34_TENSOR_MATRIX/ARBRE_*
# → 34 arbres nommés, dont T10=Langage, T19=Culture, T24=Mémoire, T25=Histoire, T27=Vérité
```

### 6. Tree19 Culture non_decision_contract
```bash
cat .../ARBRE_19__Arbre_de_la_Culture/non_decision_contract.md
# → "Tree34 ↛ ACT. Toute décision finale appartient à X-108."
```

### 7. Agents 52 — liste complète
```bash
python3 -c "import json; d=json.load(...); print keys"
# → 52 agents dont MEMOIRE_PERSONNELLE_OBSIDIA, VOCABULAIRE_CANONIQUE, THEORIE_VIVANTE,
#   FRISE_HUMAINE, HUMAN_HISTORY_MAPPER, CARTOGRAPHE_34_ARBRES, ONTOLOGUE_OBSIDIA,
#   RECHERCHE_EXTERNE, DATA_SOVEREIGNTY_GUARD
```

### 8. Fichiers education / bias / language
```bash
head education_score.py, bias_gate.py, language_router.py
# → education_score.py: Score = w1*S + w2*C + w3*R + w4*F + w5*D, ADVISORY_ONLY
# → bias_gate.py: "Bias ≠ 0 is expected. Bias → sovereign decision without validation is blocked."
# → language_router.py: détection fr/en, authority markers détectés et bloqués
```

### 9. Reverse OS / Context Packet V2 / X108 ingress
```bash
# → periphery/reverse_os/action_projection_readonly.py: advisory_only=True, can_emit_act=False
# → periphery/context/context_packet_builder_v2.py: forbidden_tokens_detected, decision_authority, allowed_to_decide=False
# → periphery/x108_ingress/readonly_context_ingress.py: can_emit_act=False, can_write_memory=False
```

---

## Fichiers non trouvés localement (USER_PROVIDED_SOURCE_ONLY)

- `NPL_CANONICAL_SPEC.md` — absent
- `HUMAN_LOGIC_PACKET.py` — absent
- `NARRATIVE_PROVENANCE_PACKET.py` — absent
- `CULTURAL_MATRIX_PACKET.py` — absent
- `TRUTH_REGIME_SPEC.md` — absent
- `ARCHIVE_GAP_SPEC.md` — absent
- `WINNER_NARRATIVE_SPEC.md` — absent
- `DEFEATED_MEMORY_SPEC.md` — absent
- Tous les courants externes (Berger, Foucault, Gramsci, etc.) — absents

---

## Erreurs rencontrées

- `.deepseek/pastes/` contient des fichiers OS_Trad — données brutes, non pertinentes pour NPL spec
- `obsidia-npl` repo n'existe pas localement — à ne pas cloner sans validation humaine
