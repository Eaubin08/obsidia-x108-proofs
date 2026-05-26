# Graphiti full records keep decision

Status: KEEP_FULL_RECORDS
Date: 2026-05-26

File:
_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/graphiti_readonly_records_v2.jsonl

Decision:
The full Graphiti readonly records file stays in the repository for now.

Reason:
- Brody / Graphiti adapters reference this file directly.
- Replacing the file with a 1000-byte stub is too destructive.
- We commit complete functional states, not half-memory states.
- Future reduction must be a tested functional public-light dataset, not a placeholder.

Boundary:
- readonly: true
- memory_decision: false
- allowed_to_decide: false
- emits_act: false
- kernel_binding: false
- x108_merge: false
- decision_authority: KX108_ONLY

Current file size:
22110590 bytes

Next:
Build and test a real sanitized light dataset before any replacement.
