# Obsidia GPS / Defense / Aviation V0.1 - State Matrix

Status date: 2026-08-02
Scope: hackathon / industrial demo readiness map
Claim discipline: this matrix separates runtime/demo evidence from production-grade proof, certification, replay, and cryptographic signing.

## Executive Status

Demo-ready: YES, for a strategic simulation and local governance demonstration.
Production-ready: NO.
Best current claim: Obsidia has a real GPS domain gate path that can fail-close spoofing/replay-style telemetry before a sovereign X-108 decision, plus reusable proof/audit primitives.
Forbidden current claim: certified aviation/defense runtime, real sensor PKI attestation, production replay, or completed named Lean proofs L-02/L-06.

## State Matrix

| Component | Exists where | Current status | Reusable now? | Protected? | Next action |
|---|---|---|---|---|---|
| P3-05 GPS X-108 Gate / Reality Authenticity Gate | `domains/gps/gps_x108_gate.py`, `tests/test_gps_x108_reality_authenticity_gate.py`, `artifacts/gps_v01_gate_live_nominal_result.json` | RUNTIME_CODE + LIVE_KERNEL_WIRED. Gate translates GPS telemetry into `GpsDefenseAviationState`, checks freshness, attestation field, anti-replay, multi-source coherence, physical envelope, fail-closes spoof/replay to `HOLD`, posts coherent nominal telemetry to live X-108, and embeds an OS3 ticket in the local receipt. | YES for MVP/demo and live governance check. Not an actuator/certification. | No direct protected marker found for this file. | Keep OS3 `replay_status` explicit until verifier runs; do not claim physical execution authorization. |
| P3-06 GPS Nuisance Registry | `domains/gps/nuisance_registry.py` | RUNTIME_CODE. Classifies spoofing, replay, jamming/noise, attestation failure, path fidelity breach, restricted zone, collision risk, physical envelope breach. | YES for MVP/demo. | No direct protected marker found. | Add tests for jamming, collision, restricted zone, and physical envelope breach. Align labels with specs/domain form. |
| P3-09 GPS decisional form / CIC boundary | `domain_packets/gps_defense_aviation_decisional_form_v0.yaml`, `tests/test_gps_p3_09_contract_and_receipts.py` | SOURCE_ORGANIZED / contract + TESTED_SURFACE. Defines `DOMAIN_BRIDGE_ONLY`, `KX108_ONLY`, Reality Authenticity Gate, Physical Signal Periphery, nuisances, and proof stack expectations. Test now checks P3-05 output against the P3-09 contract surface. | YES as demo contract and review artifact. | No direct protected marker found. | Replace text-surface assertions with full YAML schema validation when a YAML parser dependency is accepted. |
| Aviation connector runtime | `connectors/aviation_robo.py`, `specs/09_CRITICAL_WORLDS/AVIATION_CONNECTOR_X108_GATE_SPEC.md` | RUNTIME_CODE + DRY_RUN. Connector supports local P3-05 evaluation for nominal, spoof, and replay scenarios. Spec states connector must stay non-sovereign. | YES for hackathon demo and scenario runner. | No direct protected marker found. | Connect `--local-gate` output to OS3ProofTicket and then to kernel endpoint only as non-actuating request. |
| GPS state and Sigma GPS pipeline | `sigma/contracts.py`, `sigma/protocols.py`, `sigma/domains/gps_defense_aviation_agents.py`, `sigma/examples/gps_*.json` | RUNTIME_CODE. `GpsDefenseAviationState` exists; GPS agents evaluate source availability, trajectory integrity, source conflict, time skew, brownout, and attestation readiness; protocol runs GPS pipeline through `GuardX108`. | YES. This is a strong existing brick. | Sigma files are sensitive but not in the hard protected proof/seal class. | Build an integration test from P3-05 payload -> Sigma GPS pipeline -> envelope -> OS3 ticket. |
| GPS adapter | `periphery/adapters/gps_adapter.py`, `specs/_imports_readonly/GPS_SOURCE.md`, `specs/09_CRITICAL_WORLDS/GPS_TO_X108_INTENT_CONTRACT.md` | RUNTIME_CODE. Builds GPS `ActionCandidate` and `GpsDefenseAviationState`; spec says GPS produces intent and no direct decision. | YES for local runtime wiring. | No direct protected marker found. | Reuse adapter inside P3-05 instead of duplicating state construction where possible. |
| OS3ProofTicket / runtime receipt basis | `periphery/os3_ticket.py`, `domains/gps/gps_x108_gate.py`, `tools/generate_gps_v01_receipts.py`, `artifacts/gps_v01_receipts/*.json`, `specs/01_X108_AUTHORITY/DECISION_TICKET_CANONICAL_SPEC.md`, `specs/11_PROOF_REPLAY_OS3/OS3_PROOF_RUNTIME_SPEC.md` | RUNTIME_CODE + RECEIPTS_GENERATED. Ticket contains input/output/trace hashes, merkle root, evidence refs, and `replay_status`. P3-05 now builds and embeds an OS3 ticket in each local decision receipt. Current builder still hardcodes `replay_status='NOT_RUN'`. | YES as receipt basis for demo/audit. | No direct hard protected marker for `periphery/os3_ticket.py`; generated tickets touch proof claims carefully. | Add a replay verifier later; do not change `replay_status` until verification really executes. |
| P4-07 production signed decision receipt | `periphery/os3_ticket.py`, `domains/gps/gps_x108_gate.py`, `docs/audits/OBSIDIA_BRANCHING_MATRIX_SUMMARY_V0.md`, `docs/audits/OBSIDIA_BRANCHING_MATRIX_DRAFT_V0.csv` | PARTIAL. Local SHA-256 demo receipt exists; OS3ProofTicket exists. Branching matrix says `kernel/signed_decision_receipt.py` is missing and requires kernel-file proposal before creation. | PARTIAL. Good for demo receipt, not production signature. | Target kernel file is HIGH risk / proposal-required; Merkle/RFC3161 evidence is protected. | Create a non-kernel adapter first: GPS gate verdict -> OS3ProofTicket. Defer true P4-07 production signing until approved proof plan. |
| L-02 trajectory state proof | `proofs/lean/Obsidia/GeneratedPeripheral/IST_Indice_Stabilite_Trajectoire.lean`, `docs/audits/OBSIDIA_BRANCHING_MATRIX_SUMMARY_V0.md`, `docs/audits/OBSIDIA_BRANCHING_MATRIX_DRAFT_V0.csv` | PARTIAL / PROVISIONAL. Lean scaffold covers trajectory stability state and admissibility; branch matrix says `kernel/trajectory_state.py` is missing/proposal-required. | PARTIAL. Usable as proof surface and mapping candidate, not final named L-02 closure. | Lean proof files are protected; target kernel file is HIGH proposal-required. | Write an L-02 mapping note first, then only edit Lean/kernel with explicit approval and proof verification plan. |
| L-06 path fidelity proof | `proofs/lean/Obsidia/GeneratedPeripheral/P_DomainKernel_PathFidelity_RequiresCoherence.lean` | PRESENT as a small generated theorem: path fidelity requires coherence. Not necessarily full named L-06 production theorem. | YES/PARTIAL. Strong for demo claim "path fidelity cannot ignore coherence". | Lean proof files are protected. | Map this theorem as L-06 candidate and add missing invariants separately: continuity, authorized plan, drift bound, replay consistency. |
| P4-20 path fidelity guard runtime | `obsidia_core/guardians/path_fidelity_guard.py`, `tests/test_path_fidelity_guard_p4_20.py`, `docs/proposals/P4_20_PATH_FIDELITY_GUARD_PROPOSAL.md`, `domain_packets/gps_defense_aviation_decisional_form_v0.yaml` | RUNTIME_CODE. Pure non-sealed guard emits path-fidelity evidence only: coherence, drift bound, authorized route presence, replay consistency, physical envelope, reason codes, evidence hash. It never emits `ALLOW`. | YES for MVP/demo evidence. Formal Lean binding remains open. | Runtime file is non-protected; Lean proof files are protected. | Bind P4-20 evidence vocabulary to L-06 only after explicit proof-edit approval. |
| Sealed kernel runtime / X-108 authority | `server.kernel.sealed.cjs`, `runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs`, `sigma/guard.py`, `domains/gps/gps_x108_gate.py`, `artifacts/gps_v01_kernel_live_check.json`, `artifacts/gps_v01_gate_live_nominal_result.json`, `MonProjet/allData/decision_gps_defense_aviation_1785698704124.json` | LIVE_POST_OK + P3_GATE_LIVE_OK. Kernel process launched on `127.0.0.1:3001`; direct POST returned `HTTP 200`; P3-05 live nominal call returned `source=KERNEL_X108`, `x108_gate=ALLOW`, `market_verdict=TRAJECTORY_VALID`. Spoof/replay remain local `HOLD`. | YES for live governance check. Still not production certification and not physical actuation authorization. | HIGH for sealed kernel files. Do not edit. | Keep kernel running for demo; do not patch sealed kernel. |
| Merkle / seal evidence | `proofs/merkle_root.json`, `proofs/verifiers/merkle_root.json`, `proofs/verify_merkle.py`, `proofs/verifiers/verify_merkle.py`, `merkle_seal.json` | PRESENT. Verification scripts and Merkle roots exist; many files are protected evidence. | YES as evidence pack and audit reference. | HIGH. Protected/canonical evidence. | Read/verify only. Do not regenerate roots or seals for hackathon unless user approves proof plan. |
| RFC3161 anchor | `proofs/verifiers/rfc3161_anchor.json`, `docs/RFC3161.md`, `specs/11_PROOF_REPLAY_OS3/RFC3161_PRODUCTION_BOUNDARY.md` | PRESENT as anchor/spec evidence. Not automatically tied to GPS receipts yet. | PARTIAL. Good as proof-stack component, not GPS runtime signing. | HIGH for anchors. | Link GPS/OS3 receipts to anchor flow in a new adapter/report, not by mutating the anchor. |
| Replay / P4-07 receipt manifest | `tools/gps_v01_replay_verifier.py`, `tools/gps_v01_p4_07_receipt_manifest.py`, `artifacts/gps_v01_replay_report.json`, `artifacts/gps_v01_p4_07_receipt_manifest.json`, `periphery/os3_ticket.py` | DRY_RUN_PASS + DEMO_MANIFEST_SIGNED. Replay verifier checks nominal/spoof/replay receipts without mutating tickets. P4-07 demo manifest signs the receipt bundle with local HMAC and explicitly says not RFC3161/not production. OS3 tickets preserve `replay_status='NOT_RUN'`. | YES for demo/audit. NO for production replay/RFC3161 certification. | Replay/proof evidence can be protected depending on path. | Production replay/signing requires real verifier, key policy, RFC3161/PKI boundary, and approval. |
| Real sensor attestation | `sigma/contracts.py`, `sigma/guard.py`, `periphery/adapters/gps_adapter.py`, `domains/gps/gps_x108_gate.py`, `proofs/verify_decision.py` | LOGICAL FIELD PRESENT. `attestation_ready`, `sensor_attested`, and `attestation_ref` exist, but no real hardware/PKI sensor attestation provider was found in the GPS path. | YES for MVP simulation. NO for production sensor trust. | Real attestation/proof paths may be protected; current logical fields are not production certs. | Define `SensorAttestationProvider` interface and a demo provider; production provider later with keys/certs/hardware roots. |
| L-02/L-06 mapping note | `docs/formalisation_math/GPS_L02_L06_MAPPING_NOTE.md`, `proofs/lean/Obsidia/GeneratedPeripheral/IST_Indice_Stabilite_Trajectoire.lean`, `proofs/lean/Obsidia/GeneratedPeripheral/P_DomainKernel_PathFidelity_RequiresCoherence.lean` | MAPPING_NOTE_NOT_FINAL_PROOF. Existing proof surfaces are mapped to L-02/L-06 candidates without claiming final proof closure. | YES for audit/demo truthfulness. | Mapping note is not protected; Lean files are protected. | Use this note as the work order before any protected Lean edit. |
| Domain safety / security review | `specs/09_CRITICAL_WORLDS/*.md`, `docs/investor/*GPS*`, `docs/audits/OBSIDIA_BRANCHING_MATRIX_*` | DOCS/SPECS present. No external aviation/defense safety review found. | YES for internal claim boundary and hackathon narrative. | Mostly docs; proof/audit evidence referenced is protected. | Create GPS V0.1 safety review checklist and adversarial test matrix execution report. |
| Hackathon cockpit | `C:/Users/User/.codex/visualizations/2026/08/02/019fc2f0-5b0d-7471-aeb8-fdfb9d055d39` | WORKING_PROTOTYPE. Local web cockpit demonstrates AF994, spoofing, replay, degraded sensor, cognitive debugger, and simulated receipts. | YES for tomorrow's demo. | Outside repo; demo artifact only. | Keep it labelled strategic demo; optionally replace simulated receipt with OS3ProofTicket output. |

## What We Can Demonstrate Honestly Tomorrow

1. A GPS/Defense/Aviation cockpit showing the idea: "GPS is not believed, it is admitted only after Reality Authenticity checks."
2. A real Python P3-05 gate that can fail-close spoofed and replay-like telemetry into `HOLD`.
3. A domain nuisance registry that turns attacks into structured labels instead of letting raw data drive action.
4. A Sigma GPS pipeline already present in the repo, with agents for source availability, trajectory integrity, source conflict, time skew, brownout, and attestation readiness.
5. A runtime proof-ticket basis (`OS3ProofTicket`) with hashes and Merkle-style trace fields.
6. Lean proof surfaces for trajectory stability and path fidelity/coherence, clearly marked partial or generated where appropriate.

## What We Must Not Claim Yet

1. "Production aviation/defense certified."
2. "P4-07 production signed receipts are closed."
3. "Replay production is operational" while `replay_status` is still `NOT_RUN`.
4. "L-02 and L-06 are fully finalized named production proofs."
5. "Real sensor attestation exists" when the GPS path currently has logical readiness fields, not a live PKI/hardware trust chain.
6. "The sealed kernel was modified or certified for GPS" because sealed/protected kernel files were not touched.

## Best Next Build Order

1. DONE: GPS P3-05 -> OS3ProofTicket adapter embedded in local receipts.
2. DONE: Contract test verifies P3-05 output against `gps_defense_aviation_decisional_form_v0.yaml` surface.
3. DONE: GPS receipt parity test and JSON receipt generation for nominal/spoof/replay.
4. DONE: P4-20 runtime guard implemented as pure non-sealed evidence module.
5. DONE: L-02/L-06 mapping note names current Lean files and missing invariants.
6. DONE: GPS replay verifier dry-run report generated; `replay_status` remains `NOT_RUN`; P4-07 demo manifest signed locally.
7. DONE: Live kernel endpoint launched and checked; P3-05 nominal live path returns `ALLOW`; spoof/replay remain `HOLD` before kernel.

## Demo Narrative

The clean hackathon message is:

"Obsidia does not ask an AI whether a GPS signal is true. It forces the signal to prove freshness, provenance, physical coherence, and path fidelity before the sovereign X-108 kernel can authorize anything. If the world lies, the system holds state instead of improvising."

## Bottom Line

The project already has roughly 60-70% of the GPS V0.1 demonstration chain:
P3 gate, nuisance registry, GPS state, Sigma agents, OS3 ticket basis, proof surfaces, Merkle/RFC3161 evidence, and a working cockpit.

The missing 30-40% is not "more pitch". It is production closure:
GPS receipt adapter, replay verifier, finalized L-02/L-06 mapping/proofs, P4-20 runtime guard, real sensor attestation provider, and live kernel endpoint verification without touching sealed assets.
