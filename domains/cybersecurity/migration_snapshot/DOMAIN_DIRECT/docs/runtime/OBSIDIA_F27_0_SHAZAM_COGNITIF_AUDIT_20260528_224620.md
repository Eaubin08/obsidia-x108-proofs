# OBSIDIA F27.0 — SHAZAM COGNITIF AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `42140fc`
Tags on HEAD: `BRODY_F23A6_SIGMA_BRODY_ORCHESTRATION_PALIER_20260528`

## Summary

- Scanned files: 19
- Active Shazam/tree records: 6
- Danger records: 0
- Gaps: 1

## Active files

- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/apps/obsidia_api/routes/periphery_ops.py`
  - L43 `memory_world` — from periphery.cognitive_trees.memory_world_mapper import map_memory_world
  - L43 `map_memory_world` — from periphery.cognitive_trees.memory_world_mapper import map_memory_world
  - L44 `ShazamCognitifResult` — from periphery.cognitive_trees.shazam_cognitif import ShazamCognitifResult
  - L45 `DominantTreeResult` — from periphery.cognitive_trees.dominant_trees import DominantTreeResult
  - L45 `dominant_trees` — from periphery.cognitive_trees.dominant_trees import DominantTreeResult
  - L116 `emits_act` — "emits_act": False,
  - L118 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L176 `dominant_ids` — dominant_ids: list[int] = Field(default_factory=list)
- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/periphery/cognitive_trees/dominant_trees.py`
  - L15 `DominantTreeResult` — class DominantTreeResult:
  - L18 `dominant_ids` — dominant_ids: list[int]
  - L28 `dominant_ids` — "dominant_ids": self.dominant_ids,
  - L36 `dominant_trees` — def find_dominant_trees(
  - L39 `DominantTreeResult` — ) -> DominantTreeResult:
  - L40 `dominant_ids` — dominant_ids = [i for i, a in enumerate(vector.activations) if a >= theta]
  - L42 `dominant_ids` — for i in dominant_ids:
  - L46 `DominantTreeResult` — return DominantTreeResult(
- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/periphery/cognitive_trees/memory_world_mapper.py`
  - L10 `ShazamCognitifResult` — from .shazam_cognitif import ShazamCognitifResult
  - L41 `ShazamCognitifResult` — def map_memory_world(shazam: ShazamCognitifResult) -> MemoryWorldContext:
  - L41 `memory_world` — def map_memory_world(shazam: ShazamCognitifResult) -> MemoryWorldContext:
  - L41 `map_memory_world` — def map_memory_world(shazam: ShazamCognitifResult) -> MemoryWorldContext:
  - L47 `dominant_ids` — for tid in shazam.dominant_result.dominant_ids:
- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/periphery/cognitive_trees/shazam_cognitif.py`
  - L11 `DominantTreeResult` — from .dominant_trees import find_dominant_trees, DominantTreeResult
  - L11 `dominant_trees` — from .dominant_trees import find_dominant_trees, DominantTreeResult
  - L24 `ShazamCognitifResult` — class ShazamCognitifResult:
  - L27 `DominantTreeResult` — dominant_result: DominantTreeResult
  - L36 `dominant_trees` — "dominant_trees": self.dominant_result.dominant_names,
  - L44 `ShazamCognitifResult` — def shazam_cognitif(vector: TreeActivationVector, theta: float = 0.15) -> ShazamCognitifResult:
  - L45 `dominant_trees` — dominant = find_dominant_trees(vector, theta=theta)
  - L46 `dominant_ids` — dominant_set = frozenset(dominant.dominant_ids)
- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/shazam_cognitif.py`
  - L55 `dominant_trees` — "dominant_trees": dominant,
- `C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B/periphery/shazam_cognitif.py`
  - L55 `dominant_trees` — "dominant_trees": dominant,

## Gaps

- `F27_G02` — No explicit tree_signal bridge detected.
  - target_phase: F27.1
  - patch_now: False

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
emits_act=false
kernel_mutation=false
x108_mutation=false
```

## Next

F27.1_TREE_SIGNAL_PACKET_AUDIT_OR_PATCH

## Status

F27_0_SHAZAM_COGNITIF_AUDIT_DONE
