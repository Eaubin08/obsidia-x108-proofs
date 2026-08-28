# Stage 4 — Bounded Mission Authority — Closure Dossier (V0)

**Checkpoint:** `STAGE_4H_ASSURANCE_ARCHIVE_AND_STAGE4_CLOSURE`
**Canonical branch:** `feat/terminal-runtime-repair-and-bounded-build-v1` (local, not pushed)
**Canonical HEAD:** `45e78c22dcec00bd379c6020f4513a62f8f7e5b6`
**Nature of this turn:** assurance closure only — no runtime file, no Lean file, and no `merkle_seal.json` modified.

Machine-readable companions in this directory: `MANIFEST.json`, `formal_runtime_assurance_map.json`,
`central_authority_map.json`, `abc_execution_dossier.json`, `attack_matrix.json`,
`tcb_and_limitations.json`, `HASH_MANIFEST.txt`.

---

## 1. What Stage 4 solves

Stage 3 gave a persistent bounded **multi-action mission** (immutable `MissionActionPlan`, deterministic
dependency order, per-action governed execution, verified accumulated Git state, restart-safe) — but at a
human cost of **O(N)**: a human had to approve the exact `execution_authority_hash` (EAH) of **every**
action.

Stage 4 introduces **Bounded Mission Authority**: one human authorization, issued once for one exact
fixed plan, lets the whole plan run **without any per-action human EAH approval**, while every single
action is still individually decided and veto-able by the sovereign KX108 kernel (PRE and POST).

Concretely, a real `A -> B -> C` mission was executed (`abc_execution_dossier.json`) with:
**1** HumanMissionAuthorization, **3** actions, **3** distinct ExecutionEnvelopes / EAH / DAAW / DMAE,
**0** per-action human EAH approvals, **3** KX108_PRE ALLOW, **3** governed mutations, **3** TestContract
PASS, **3** KX108_POST ALLOW, **3** KEEP, **3** local snapshots; canonical base immutable, mission tip
`BASE -> T1 -> T2 -> T3`, final target == state C. 4 `advance` calls, at most 1 governed mutation each.

---

## 2. Which authority is human

Exactly one object is human-rooted: the **HumanMissionAuthorization (HMA)**.

* `issuer = HUMAN`, carries a `human_authorization_reference` the stack never synthesizes (fail-closed if
  absent), immutable / write-once.
* Bound to **one exact `plan_hash`** (`EXACT_PLAN_HASH`) — never a family of plans. A different plan
  hash, target, source, operation, extra action, larger budget or different dependency graph is
  fail-closed.
* Revocable by a human at any time (append-only `MissionAuthorityRevocation`, `actor = HUMAN`).

That is the entire human surface for a Stage 4 mission. It is **O(1)** for that fixed bounded plan — and
only for that plan. It is **not** a grant of general or unrestricted autonomy.

---

## 3. Which authority is KX

The **KX108 kernel** renders two sovereign decisions **per action**:

* **KX108_PRE** — the only sovereign pre-execution decision. It always executes; a derived approval
  never bypasses it. `x108_gate` must be `ALLOW` for the governed write to proceed.
* **KX108_POST** — bound cryptographically to the exact KX108_PRE record and the sealed evidence;
  drives disposition D1 (KEEP) or rollback D2.

KX stays **O(N)**: three actions -> three independent KX108_PRE and three independent KX108_POST
decisions. There is deliberately **no** mission-level KX blanket ALLOW.

`KX_DECISION_AUTHORITY = KX108_ONLY`.

---

## 4. Why HMA / DAAW / DMAE are not sovereign

| Object | Role | Sovereign? |
|---|---|---|
| **HumanMissionAuthorization (HMA)** | human root, upper bound, exact plan hash | **No** — it is the *root of trust*, not the *pre-execution decision*. It satisfies no KX decision and authorizes no write on its own. |
| **DerivedActionAuthorityWitness (DAAW)** | machine, per action, binds exact EAH / action base / scope | **No** — `NON_SOVEREIGN`. Evidence that "this action is inside the human-authorized scope"; it cannot widen scope (`scopeLE`), and it does not satisfy any HumanApproval or authorize PRE. |
| **DerivedMissionApprovalEvidence (DMAE)** | PRE-compatibility artifact, `approved_by = HUMAN_MISSION_AUTHORITY_DERIVED` | **No** — `NON_SOVEREIGN`, `is_execution_authority = false`, `bypasses_kx_pre = false`. It only opens a *tentative* execution; KX108_PRE still decides. |

Every privileged consumer of a derived approval **reloads and exact-binds the canonical DMAE artifact**
(and, pre-mutation, the full HMA -> DAAW chain with revocations). `approved_by` + structure + a valid
self-hash are **never** sufficient (Stage 4F Fix A). The 16 machine-checked Lean invariants formalize
the non-amplification and scope-subset properties.

---

## 5. How O(1) human authorization works

```
human reference
  -> HumanMissionAuthorization (issuer HUMAN, exact plan_hash)         [ONE human act]
  -> MissionActionPlan (immutable, write-once)
  -> for each action i in deterministic dependency order:
       ExecutionEnvelope + child + exact EAH_i
       -> DerivedActionAuthorityWitness_i   (auto, NON_SOVEREIGN, binds EAH_i / tip_i / scope)
       -> DerivedMissionApprovalEvidence_i  (auto, NON_SOVEREIGN, full canonical HMA->DAAW reverify)
       -> HumanApproval_i (approved_by = HUMAN_MISSION_AUTHORITY_DERIVED, human_authorization_reference = HMA root)
       -> KX108_PRE_i  (SOVEREIGN)  == ALLOW
       -> C2 governed mutation      (under the mission_id lock)
       -> TestContract_i            == PASS
       -> KX108_POST_i (SOVEREIGN)  == ALLOW
       -> D1 KEEP -> LocalSnapshotReceipt_i -> mission_tip advances tip_{i-1} -> tip_i
```

No human input is required anywhere between the single HMA and plan closure. The sequencer only
*composes* existing proven pieces (`execute_mission_action`, `derive_and_record_action_authority_witness`,
`create_local_snapshot`); it fabricates no target write, KX decision, approval, EAH, DAAW, DMAE or Git
snapshot.

---

## 6. Why KX remains O(N)

By construction: the sequencer executes one action per `advance` call, each action independently reaches
`obsidia_governed_execution_driver_v0.execute_governed_remediation`, which independently builds
KX108_PRE evidence, obtains a fresh sovereign KX108_PRE decision, and later a fresh sovereign KX108_POST
decision. There is no code path that turns "the mission was authorized once" into "KX approved every
action". `MISSION_LEVEL_KX_BLANKET_AUTHORITY = false`.

---

## 7. How revocation works

A human commits a `MissionAuthorityRevocation` (append-only, `actor = HUMAN`).

* **Between actions:** the next `advance` re-runs the full canonical HMA -> DAAW chain; a revoked HMA is
  detected at the PRE evidence adapter / the driver freshness re-check / the C2 in-lock re-check ->
  `HMA_REVOKED` -> `PLAN_BLOCKED`. The already-KEPT actions keep their evidence; later actions never run.
* **Concurrent with a mutation:** the revocation writer and the Stage 4 C2 critical section
  (final full canonical freshness re-check + `atomic_replace_with_bytes` + post-write measurement)
  acquire the **same `mission_id`-keyed OS cross-process lock** (Windows `msvcrt.locking`, POSIX
  `fcntl.flock`; bounded timeout -> fail-closed; released on process death).
  Result: a **total serialized commit order**. Either the revocation commits first and the mutation does
  not happen, or the mutation linearizes first and the revocation commits only afterwards. There is
  **no** execution in which a committed revocation precedes a successful mutation.

**Claim boundary:** a revocation *request* that arrives after the executor already owns the lock does
**not** retroactively cancel an already-linearized action. The V0 property is about commit order, not
mid-flight cancellation.

---

## 8. How replay is prevented

Every derived artifact binds the **exact** execution identity:

* **EAH** is recomputed from the envelope at every boundary and must equal the stored value; each
  action has a distinct EAH.
* **DAAW** binds `mission_id`, `missionAuthId` (HMA id), `plan_hash`, `action_id`, `ordinal`,
  `action_base_sha` (== current mission tip) and the exact EAH; its idempotence key is
  `EXACT_RECORDED_WITNESS_MATERIAL`, never `action_id` alone.
* **DMAE** binds `mission_id`, `batch_execution_id`, `child_execution_id`, `plan_hash`, `action_id`,
  the exact EAH, the HMA id/hash, the DAAW id/hash, and `authority_mode`. The derived `approval_id` is
  `appr-sha256(beid:child:eah:dmae_id)[:32]` and is re-derived and checked.

Cross-action and cross-mission replays of EAH / DAAW / DMAE / derived approval all fail closed
(`attack_matrix.json`).

---

## 9. How restart works

There is **no in-memory authority dependency**. All authority state lives on disk: the HMA is a mission
revision event; DAAW artifacts are write-once files; the DMAE is rebuilt fresh from the canonical chain
at each execution. A fresh process projects the mission from the append-only, hash-chained revision log.

* After `A` KEEP + snapshot `T1`: reload -> `active_hma_id` recovered, tip `== T1`, `A` recognised
  complete, `B` selected fresh; `B` and `C` then run to `PLAN_EXECUTION_COMPLETE`.
* `B` prepared + DAAW persisted but not executed -> reload -> the **same** canonical DAAW is reused,
  no divergent duplicate, no human EAH requested -> `B` executes.

---

## 10. How mission tips work

`canonical_base_sha` is immutable. `mission_tip_sha` is **derived** by folding
`ACTION_LOCAL_SNAPSHOT_COMMITTED` events: **only a KEEP** advances it. Each action `i` is prepared with
`expected_action_base_sha = current mission_tip_sha`, so `action_base_sha_i == tip_{i-1}` and
`tip_i == the local snapshot commit of action i`. Observed: `BASE -> T1 -> T2 -> T3`.

A local per-action snapshot commit is **not** final human Git acceptance, a push, or a main merge:
`MISSION_SNAPSHOT_IS_FINAL_GIT_ACCEPTANCE = false`, `FINAL_GIT_DISPOSITION_STILL_HUMAN = true`.

---

## 11. What is formally proven

Machine-checked in Lean 4, **axiom-free** (`does not depend on any axioms`), 0 `sorry`/`admit`/custom
axiom:

* 16 of the 17 bounded-mission-authority invariant specifications, including `NoAuthorityAmplification`,
  `ActionWithinMissionScope`, `ActionAuthorityBindsExactEAH`, `ActionBaseEqualsCurrentMissionTip`,
  `MissionActionBudgetNeverExceeded`, `RevokedMissionCannotAuthorizeAction`,
  `ClosedMissionCannotAuthorizeAction`, `PlanRevisionCannotExpandAuthorizedScope`,
  `PerActionAuthorityDistinct`;
* the 2nd central theorem `DerivedScopeSubsetHumanAuthorizedScope`;
* `scopeLE` is a preorder.

`lake build Obsidia.MissionAuthority` and `lake build Obsidia` pass (26 jobs), pre and post this turn.

---

## 12. What is runtime validated (not formally proven end-to-end)

* **Lean <-> runtime conformance** over 17 semantic vectors + 11 scope pairs, 0 divergence — a **finite**
  canonical corpus, not universal refinement.
* The **central theorem #17** ("every governed mutation has a valid human mission witness AND a valid KX
  witness") for the canonical `A -> B -> C` fixture and the single-operation V0 domain: the mechanical
  map in `abc_execution_dossier.json` shows every one of the 3 physical mutations has exactly one
  action identity, exact EAH, HMA coverage (`issuer HUMAN`), DAAW (`NON_SOVEREIGN`), DMAE
  (`NON_SOVEREIGN`), KX108_PRE ALLOW record and KX108_POST ALLOW record —
  `MUTATION_WITHOUT_{HMA,DAAW,DMAE,KX_PRE_ALLOW,KX_POST_EVIDENCE} = 0`,
  `UNACCOUNTED_GOVERNED_MUTATIONS = 0`.
* The full negative / replay / revocation / restart / rollback matrix (`attack_matrix.json`).
* Full runtime regression: `pytest tests/cli/` = **498 passed / 4 skipped / 0 failed**.

```
CENTRAL_THEOREM_17_RUNTIME_EVIDENCE   = MULTI_ACTION_V0_VALIDATED
CENTRAL_THEOREM_17_RUNTIME_REFINEMENT = VALIDATED_V0_WITH_DOCUMENTED_TCB
CENTRAL_THEOREM_17_PROVEN_END_TO_END  = FALSE
```

---

## 13. What remains unproven

* A machine-checked proof that the runtime `ProducedBy` relation faithfully refines the Lean
  `Event`/`Step` model for **all** traces (not a finite vector set).
* Formal `sha256` / EAH byte-equivalence (currently a semantic `CryptoInterface` hypothesis; runtime
  uses `hashlib.sha256`).
* **Multi-operation** governed authority — the Lean `Operation` type has a single constructor
  (`UPDATE_TARGET_FROM_SOURCE`); `MULTI_OPERATION_FORMAL_GENERALIZATION = NOT_YET_PROVEN`. Stage 4
  closure does **not** imply CREATE / DELETE / MOVE / RENAME authority.
* Hard technical enforcement that Claude is transport-only
  (`CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED = FALSE`) — a separate future checkpoint.

The trust boundary and every TCB component are enumerated in `tcb_and_limitations.json`.

---

## 14. What Stage 5 must solve (explicitly outside Stage 4)

A. **Governed Operation Algebra** — CREATE / DELETE / MOVE / RENAME and multi-operation formal
   generalization (Lean `Operation` cardinality > 1, conformance `op_expansion` vector representable).
B. **UNKNOWN / resource-resolution wiring**.
C. **Claude / LLM Gateway**.
D. **Cognitive Capability Lease**.
E. **Hard technical enforcement** of `CLAUDE_ROLE = TRANSPORT_INTERFACE_ONLY` (tool permissions /
   gateway).

None of these are in Stage 4 scope.

---

## 15. Assurance verdict

```
STAGE4_BOUNDED_MISSION_AUTHORITY_ASSURANCE_CLOSED_V0

Core bounded mission authority invariants are machine-checked in Lean; canonical representable
semantics are validated against runtime vectors; bounded multi-action Stage 4 execution has been
empirically validated against positive, negative, replay, revocation, restart and rollback tests
under the documented V0 TCB and single-operation domain.

Obsidia Stage 4 is NOT claimed to be "formally proven secure".
```

Autonomy level: **one human mission authorization with per-action KX-governed execution** for a fixed
bounded plan. Not general autonomy. Not L4.
