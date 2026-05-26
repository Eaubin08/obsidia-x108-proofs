# PUBLIC REPO CLEANUP FREEZE — 2026-05-26

Status: VALIDATED_PUBLIC_HYGIENE_FREEZE
Branch: main
Head: 4155cde
Repo path:
C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B

## Validated phases

- PHASE 1A: clean clone / push recovery validated
- PHASE 1B: CURRENT_* root session packets removed from public tracking
- PHASE 2C: _local_audits and audit_logs removed from public tracking
- PHASE 2D: root scripts moved into scripts/, tools/, audit/
- PHASE 2E: ambiguous root scripts classified and removed from root
- PHASE 2F: root status docs moved into docs/status and private root docx removed
- PHASE 3A: periphery / Brody / Graphiti / Bank / GPS / Gencoin / Mmonde inventory completed
- PHASE 3B: public/private/core candidates diagnosed
- PHASE 3C: tracked Mmonde .docx private sources removed from public tracking
- PHASE 3D: root Mmonde duplicate resolved into docs/status/mmonde_reconciliation/
- PHASE 3E: Graphiti full records intentionally kept until tested light dataset exists
- PHASE 3F: final public hygiene snapshot validated

## Current public root tracked files

- .codeflowignore
- .dockerignore
- .gitignore
- AGENTS.md
- CLAUDE.md
- LICENSE
- MANIFEST.md
- MANIFEST_SHA256.json
- MANIFEST_SHA256_NEW.json
- merkle_seal.json
- package.json
- package-lock.json
- PROOF_INDEX.md
- README.md
- REPRODUCIBILITY_CHECKLIST.md
- requirements.txt
- SECURITY.md
- server.kernel.sealed.cjs
- shim_map.json
- START_HERE.md

## Validated public hygiene

- Tracked DOCX left: 0
- Root tracked Python/PowerShell scripts: 0
- Root Mmonde duplicate left: 0
- Working tree: clean before freeze report
- Graphiti full records: kept intentionally
- Graphiti file size: 22110590 bytes

## Local ignored files still present

These files remain local and ignored. They are not part of public tracking:

- bazar a branché pour la suite obsidia .docx
- test_neo4j.py

## Graphiti decision

Status: KEEP_FULL_RECORDS_FOR_NOW

Reason:
- Brody / Graphiti adapters reference the full records file directly.
- A 1000-byte stub was rejected as too destructive.
- The project commits complete functional states, not half-memory states.
- Any future reduction must be a tested functional public-light dataset.

## Boundary

- readonly: true
- memory_decision: false
- allowed_to_decide: false
- emits_act: false
- kernel_binding: false
- x108_merge: false
- decision_authority: KX108_ONLY

## Next phase

PHASE 4 — structural map / public README alignment / periphery documentation index.

No kernel mutation.
No X108 merge.
No Graphiti reduction until tested light dataset exists.
