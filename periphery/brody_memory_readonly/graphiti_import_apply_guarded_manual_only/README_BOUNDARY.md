# BRODY GRAPHITI IMPORT APPLY — GUARDED MANUAL ONLY

Status: READY

This module prepares an import/apply plan from reviewed Brody memory candidates.

Default mode is dry-run.

Real Neo4j write requires:
- explicit `-Apply`
- explicit confirm token
- `NEO4J_PASSWORD` in environment

Boundary:
- no X108 mutation
- no kernel mutation
- no autonomous memory decision
- no ACT
- no verdict
- KX108 remains sole decision authority
