# Cognitive Convergence Registry

Verified head: `0b230112afeb317b8f8f279c00c664a9c2bc6830`

This directory contains the canonical registry for known Obsidia cognitive, semantic, memory, source, governance, science, language, adapter, and output blocks.

The registry exists to stop repeated archaeology. A block can be registered even when it is not ready to connect. Uncertainty is preserved directly in the record.

## Rule

Any newly rediscovered Obsidia block must be registered immediately, even if it cannot yet be connected.

Workflow:

```text
DISCOVER
-> VERIFY SOURCE
-> REGISTER
-> CLASSIFY STATUS
-> MAP TARGET
-> RECORD BLOCKER
-> RECORD_DO_NOT_CONNECT_TO
-> AUDIT
-> WIRE
-> TEST
-> FREEZE
-> UPDATE REGISTRY
```

## Files

- `COGNITIVE_CONVERGENCE_MASTER_REGISTRY.json` is the source of truth.
- `COGNITIVE_CONVERGENCE_MASTER_MAP.md` is the readable operating map.
- `tools/cognitive_registry_query.py` is a readonly stdlib-only query utility.

## Discipline

Do not assume that a historical concept is runtime-ready. Do not invent a target hook. If an exact destination is not proven, use `target_hook_status = "UNRESOLVED"` and record `target_layer_candidate`, `target_reason`, and `required_audit`.

Knowledge is not memory. Memory is not proof. Source packs are not runtime modules. C1 compact projection is not authority. KX108 remains the only decision authority.
