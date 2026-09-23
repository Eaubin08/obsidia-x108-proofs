# NPL_CANONICAL_SPEC

Status: SPEC_CANDIDATE
Authority: KX108_ONLY

Source Paths:
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_SOURCE_DISCOVERY_REPORT.md`
- `periphery/x108_ingress/readonly_context_ingress.py`
- `periphery/context/context_packet_builder_v2.py`

Source Status: SPEC_CANDIDATE (NPL non implémenté comme couche nommée)

Scope:
Spec canonique de NPL — Narrative Provenance Layer — couche périphérique readonly de signaux narratifs contextuels.

Allowed:
- "NPL est une couche périphérique readonly de signaux contextuels narratifs"
- "NPL propose des hypothèses de provenance narrative"
- "NPL expose les incertitudes — `provenance_uncertainty` obligatoire dans chaque packet"
- "NPL reste readonly et non souverain"
- "X108 reste autorité si une action est demandée"

Forbidden:
- "NPL prouve la provenance réelle d'une pensée"
- "NPL détecte objectivement la vérité culturelle"
- "NPL sait ce que pense vraiment l'humain"
- "NPL diagnostique un trauma"
- "NPL remplace historien, sociologue, psychologue"
- "NPL décide"
- "NPL corrige moralement l'humain"

Inputs: Signaux textuels, contexte culturel, context packets

Outputs:
- HumanLogicPacket (hypothèse de provenance)
- NarrativeProvenancePacket
- Métriques : provenance_confidence ∈ [0,1], provenance_uncertainty ∈ [0,1], manipulation_risk_signal

Metrics:
- provenance_confidence ∈ [0,1] (jamais = 1.0 sans validation humaine)
- provenance_uncertainty ∈ [0,1] (obligatoire dans tout packet)
- manipulation_risk_signal (booléen + score)

Invariants:
- PERIPHERAL_READONLY absolu
- KX108_ONLY pour toute décision
- NO_ACT
- NO_VERDICT_FINAL
- NO_MEMORY_WRITE sans gate humain
- NO_GRAPHITI_WRITE sans gate humain
- NO_KERNEL_MUTATION

X108 Boundary:
- NPL → ContextPacket enrichi → KX108 évalue — jamais NPL → décision directe

Tests Required:
- test_npl_no_decision_authority
- test_npl_no_act_emission
- test_npl_packet_schema (provenance_uncertainty obligatoire)
- test_npl_never_outputs_forbidden_tokens

Proof Expected: Python test

Runtime Status: SPEC_CANDIDATE (à implémenter en Plan 3)

Claim-Scope Notes:
17 interdictions publiques documentées dans NPL_CLAIM_SCOPE_LIMITS.md.
Les courants externes (Foucault, Gramsci, Lakoff, etc.) sont des références — pas des preuves algorithmiques.

Open Questions:
- Jcoin = alias Gencoin ou concept distinct ? (hors NPL — mais à confirmer)
- 7 flux exacts = périmètre public ? (HORS selon docs/REPO_BOUNDARY.md)
