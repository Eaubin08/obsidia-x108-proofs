# `stage4_bounded_mission_authority_closure_v0/`

Canonical assurance archive for **Stage 4 — Bounded Mission Authority** on
`feat/terminal-runtime-repair-and-bounded-build-v1` @ `45e78c22dcec00bd379c6020f4513a62f8f7e5b6`.

Assurance-closure turn (`STAGE_4H`): **no runtime file, no Lean file, no `merkle_seal.json`** was
modified. All evidence here is regenerated from disposable stores against the committed rail.

| File | Contents |
|---|---|
| `MANIFEST.json` | master machine-readable manifest: commit chain, formal + runtime inventory, conformance results, ABC summary, human/KX claims, revocation & restart assurance, central theorem #17 classification, scope |
| `formal_runtime_assurance_map.json` | every important claim classified by assurance layer (FORMALLY_PROVEN / LEAN_RUNTIME_CONFORMANCE_VALIDATED / RUNTIME_TEST_VALIDATED / REAL_EXECUTION_VALIDATED / ARCHITECTURAL_INVARIANT / ASSUMPTION / TCB_DEPENDENT / NOT_YET_PROVEN) — categories not merged |
| `central_authority_map.json` | HMA -> plan -> action -> envelope -> EAH -> DAAW -> DMAE -> PRE -> KX108_PRE -> C2 -> TestContract -> KX108_POST -> disposition -> snapshot -> mission tip, edge by edge (producer / consumer / artifact / reference / validation / evidence) |
| `abc_execution_dossier.json` | one real isolated `A -> B -> C` Stage 4 mission; per-action exact references + witness checks; aggregate `MUTATION_WITHOUT_* = 0`, `UNACCOUNTED_GOVERNED_MUTATIONS = 0` |
| `attack_matrix.json` | 18 adversarial preconditions -> expected fail-closed gate -> actual gate -> target mutated / mission tip changed / result / evidence test |
| `tcb_and_limitations.json` | explicit Trusted Computing Base + limitations + claim-boundary statement |
| `CLOSURE_DOSSIER.md` | human-readable closure: what Stage 4 solves, human vs KX authority, why HMA/DAAW/DMAE are not sovereign, O(1) human / O(N) KX, revocation, replay prevention, restart, mission tips, what is proven vs validated vs open, Stage 5 |
| `HASH_MANIFEST.txt` | sha256 of every other file in this directory (LF-normalized via the scoped `.gitattributes`), deterministic |
| `.gitattributes` | `* -text whitespace=cr-at-eol` (byte-preserving archive, same convention as `canonical_c2_conformance_pilot_v0/`) |

## Reproduce

```
lake build Obsidia.MissionAuthority && lake build Obsidia          # 26 jobs PASS, axiom-free theorems
python -m pytest tests/cli/                                        # 498 passed / 4 skipped / 0 failed
python -m pytest tests/cli/test_mission_authority_conformance_v0.py  # 17/17 semantic + 11/11 scope, 0 divergence
python -m pytest tests/cli/test_stage4_multi_action_mission_v0.py     # real A->B->C + attack + revocation + restart
```

## Verdict

```
STACK_STAGE_4H_ASSURANCE_ARCHIVE_AND_STAGE4_CLOSURE_PASS
MATURITY = STAGE4_BOUNDED_MISSION_AUTHORITY_ASSURANCE_CLOSED_V0
CENTRAL_THEOREM_17_PROVEN_END_TO_END = FALSE   (runtime-validated V0 with documented TCB)
```
