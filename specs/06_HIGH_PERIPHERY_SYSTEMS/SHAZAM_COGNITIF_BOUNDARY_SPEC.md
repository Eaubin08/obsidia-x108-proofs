# SHAZAM_COGNITIF_BOUNDARY_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- `periphery/cognitive_trees/shazam_cognitif.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/`

Source Status: RUNTIME_CODE + ADVISORY_ONLY

Scope:
Définir la boundary non-décisionnelle de Shazam Cognitif.

Allowed:
- "Shazam détecte des patterns cognitifs depuis les vecteurs d'activation Tree34"
- "Shazam produit: context_signal_only=True, can_decide=False, can_emit_act=False"

Forbidden:
- "Shazam décide"
- "Shazam émet ACT"
- "Shazam = moteur décisionnel"

Inputs: TreeActivationVector (vecteur 34 dimensions)

Outputs: ShazamCognitifResult avec:
- patterns_detected: list[str]
- dominant_result: DominantTreeResult
- context_signal_only: True
- can_decide: False
- can_emit_act: False

Metrics:
- Patterns : LANGUAGE_PATTERN_DETECTED, CAUSAL_REASONING_PATTERN, RISK_CONFLICT_PATTERN, AUTHORITY_TRUST_PATTERN, EPISTEMIC_UNCERTAINTY_PATTERN, GOVERNANCE_SOVEREIGNTY_PATTERN

Invariants:
- `can_decide=False` — codé en dur
- `can_emit_act=False` — codé en dur
- `context_signal_only=True` — codé en dur

X108 Boundary: Shazam → signal → KX108 décide

Tests Required:
- test_shazam_no_decision
- test_shazam_no_act

Proof Expected: Python test

Runtime Status: RUNTIME_CODE + ADVISORY_ONLY

Claim-Scope Notes: Shazam = signal cognitif contextuel — jamais verdict.

Open Questions: Aucune
