# X108 – Strasbourg Clock Sandbox

This bundle contains four sandbox tests demonstrating **structure-first coherence** using
a deterministic astronomical-clock-like model.

## Files
- test1_baseline.csv — Pure etalon vs pure system (no divergence)
- test2_noise.csv — Perturbed system with small noise (gradual divergence)
- test3_structural_error.csv — Single invalid exception (rapid divergence)
- test4_hold.csv — Same noise as test2 but with a HOLD threshold freezing irreversible drift

## Columns
- A_phase_day / B_phase_day — daily phase (0–1)
- delta_day — absolute phase difference
- A_phase_lunar / B_phase_lunar — lunar phase (0–1)
- delta_lunar — lunar phase difference

## Claim demonstrated
No intelligence, no learning, no data ingestion.
Coherence (or divergence) is revealed purely by **structural constraints**.
