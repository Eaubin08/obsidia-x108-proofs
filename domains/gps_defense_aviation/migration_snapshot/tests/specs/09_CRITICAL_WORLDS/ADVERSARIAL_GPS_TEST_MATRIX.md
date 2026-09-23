# ADVERSARIAL_GPS_TEST_MATRIX
Status: DOC_ONLY
Authority: KX108_ONLY
Source Paths:
- periphery/benchmarks/benchmark_case_schema.py\n- periphery/OBSIDIA_MMONDE_.../01_SOURCES/extracted_text_all.md (Scenario 2: GPS Spoofing)
Source Status: DOC_ONLY
Scope: Tests adversariaux GPS.
Allowed:
- Scénario spoofing GPS: source_conflict_score détecte contradiction\n- Bascule inertielle si spoofing détecté
Forbidden:
- GPS immunisé sans test adversarial
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: PYTHON_TEST_ONLY
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
