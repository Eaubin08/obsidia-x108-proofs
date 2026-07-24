
RUNTIME STACKS FREEZE INDEX — 2026-06-24
Frozen launchers
1. Domain Stack Only

Path:

scripts/start_domain_stack_only.ps1

Purpose:

Kernel Ragnarok 3001 + API 8000 + Bank / Trading / GPS

Run:

cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
.\scripts\start_domain_stack_only.ps1
2. Brody Only Stack

Path:

scripts/start_brody_only_stack.ps1

Purpose:

Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173 + 3 Brody terminals

Run:

cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
.\scripts\start_brody_only_stack.ps1
Runbooks
docs/runtime_launchers/DOMAIN_STACK_ONLY_RUNBOOK.md
docs/runtime_launchers/BRODY_ONLY_STACK_RUNBOOK.md
docs/runtime_launchers/RUNTIME_STACKS_FREEZE_INDEX_20260624.md
Boundary

Domain stack and Brody-only stack both use port 8000.

Do not run both launchers at the same time unless the launcher is adapted to avoid port collision.

Protected principle
Domain stack: execution matrix for domain connectors.
Brody-only stack: advisory/read-only chat/runtime surface.
Brody does not emit ACT.
Brody does not decide.
Brody does not write memory.
Kernel remains the only authority for domain execution.
