# Graphiti Phase 0 Preview

This report documents a Graphiti pre-indexing preview performed outside the repository in:

`C:\Users\User\Desktop\obsidia-engine-proof-core\graphiti-lab`

## Status

- Graphiti lab installed outside repo
- Neo4j connection verified
- graphiti-core import verified
- No LLM/API key configured
- No Graphiti client indexing performed
- No API call performed
- No repository source file modified by Graphiti

## Phase 0 strict input

Source: `.graph-memory/reports/dry_run_candidates.md`

Included:
- `.claude/context/*.md`
- `.claude/skills/*/SKILL.md`
- `CLAUDE.md`
- `MANIFEST.md`
- `agents/**`

Excluded:
- `docs/*.md`
- `proofs/**`
- `formal/tla/**`
- `RECUPE_SCORING/**`
- seal / Merkle / RFC3161
- secrets
- audit local
- archive
- staging runtime candidates

## Result

- candidate files: 30
- preview episodes: 30
- total bytes: 109495
- mode: PREVIEW_ONLY_NO_GRAPHITI_CLIENT_NO_API_CALL

## Next decision

Real Graphiti indexing requires choosing a provider:

- OpenAI API key
- Gemini-compatible client
- Ollama/local-compatible path

Recommendation: evaluate Ollama/local first for sovereignty and cost control.
