# MONDE_OBSIDIA_NATIVE_READ_MODEL_V0 — Read-only Forge

Branch: `feat/monde-obsidia-native-read-model-v0`
Base: `feat/universal-enterprise-stack-adapter-v0`
Main merge: NO

## Purpose

Supply Monde Obsidia with a **view** of real persisted canonical enterprise
objects. This does not create another source of truth.

The module `periphery/native_ops/monde_native_read_model_v0.py` reads four
independently optional local roots:
- SOURCE_RUNTIME_NATIVE_V0 packets
- CRM/TASKS NativeEntityStore
- governance decision records
- WORLD_ACTION execution receipts

It never runs the Digital Twin, a domain interpreter, KX108, the gateway or an
adapter; all filesystem operations are reads only.

## Trust semantics

- Source packets: schema + authority + packet hash verified
- Native CRM/TASKS: state + full existing receipt chain replay verified
- WORLD_ACTION receipts: existing receipt verifier used
- KX108 decisions: observed, **not claimed replay-verified** in this V0
- Missing observations: explicit `UNAVAILABLE`, never fabricated

In particular, `Interpretations`, `ActionCandidates`, and
`ProviderBindings` from transient runners are **not** falsely rendered as
persisted. When canonical persistence is added in a later Forge, they may
be surfaced using verified reader contracts.

The display model deliberately excludes free-text descriptions, raw
messages, raw recipients and credential fields.

```ini
readonly = true
canonical_truth = false
allowed_to_decide = false
allowed_to_act = false
emits_act = false
decision_authority = KX108_ONLY
```

## Proof

Workflow: `37701939187`
Result: **26 passed in 2.47s** on code HEAD
`10fb8ef34f15612ab1df5dd6bb35ee458f78105e`

The test constructs the existing 12-source Digital Twin upstream, then reads
the **persisted stores**. It confirms 12 source packets, 3 CASE, 3 TASKS,
3 FollowUps, 12 native receipts and 2 sandbox WORLD_ACTION receipts.
Tampered source packets and native states cause fail-closed errors. Re-reading
unchanged evidence is deterministic.

## Monde counterpart

Repository: `Eaubin08/monde-obsidia`
Branch: `feat/native-enterprise-read-model-v0`

Only a GET-only local API and an Enterprise native view are added. All
execution/governance logic remains in Obsidia.

## Boundaries before global freeze

- Read-only enterprise model is **not** a production ingestion service.
- It does not prove permissions or semantic compatibility with every
  real provider.
- No real CSSA data is ingested.
- The global X108 CI is separate; focused green does not imply it is green.
