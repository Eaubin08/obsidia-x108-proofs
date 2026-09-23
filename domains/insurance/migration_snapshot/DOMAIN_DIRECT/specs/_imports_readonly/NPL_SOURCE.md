# NPL_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_SOURCE_DISCOVERY_REPORT.md`
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_PLAN2_INPUT_MATRIX.md`
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_CLAIM_SCOPE_WARNINGS.md`
- `periphery/education/education_score.py`
- `periphery/bias/bias_gate.py`
- `periphery/language/language_router.py`
- `periphery/context/context_packet_builder_v2.py`
- `periphery/x108_ingress/readonly_context_ingress.py`
- `periphery/OBSIDIA_MMONDE_.../ARBRE_19__Arbre_de_la_Culture/non_decision_contract.md`
- `periphery/OBSIDIA_MMONDE_.../ARBRE_24__Arbre_de_la_Memoire/`
- `periphery/OBSIDIA_MMONDE_.../ARBRE_25__Arbre_de_l_Histoire/`
- `periphery/OBSIDIA_MMONDE_.../ARBRE_27__Arbre_de_la_Verite/`

Imported Facts:
- NPL comme couche nommée = ABSENT_UNDER_THIS_NAME dans le repo
- Récepteurs existants : Tree19/24/25/27, education_score, bias_gate, language_router, context_packet_v2, x108_ingress
- non_decision_contract Tree19 : "Tree34 ↛ ACT. Toute décision finale appartient à X-108."
- education_score : ADVISORY_ONLY ; bias_gate : gate=HOLD si biais non validé ; x108_ingress : can_emit_act=False, can_write_memory=False
- Courants externes (Foucault, Gramsci, Lakoff, Trouillot, etc.) = ABSENT dans repo — USER_PROVIDED_SOURCE_ONLY

What This Source Proves:
- Les récepteurs NPL existent dans le repo avec gardes de non-décision
- NPL peut s'ancrer sans modification du kernel

What This Source Does NOT Prove:
- NPL comme couche implémentée
- Les courants externes comme preuves algorithmiques

Boundary:
- PERIPHERAL_READONLY — ADVISORY_ONLY — KX108_BOUNDARY_REQUIRED

Claim-Scope:
- "NPL est une couche de signaux contextuels narratifs, readonly" — AUTORISÉ
- "NPL diagnostique, décide, prouve la provenance d'une pensée" — INTERDIT

Specs Depending On This Source:
- Tout le dossier 12_NARRATIVE_PROVENANCE_LAYER/

Runtime Status: SPEC_CANDIDATE

Do Not Move Original Source: true
Authority: KX108_ONLY
