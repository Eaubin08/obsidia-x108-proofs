# Current Focus

> **Read this every session start.** Update at session end with a short delta.
> Keep ≤ 300 tokens. If it grows, move stale entries to `.claude/memory/snapshots/`.

---

## Current phase

Public repo cleanup completed. Canonical repo established. Next mission: choose next technical phase from roadmap.

## Active branch (as of last inspection)

- Branch: `main`
- Working tree: clean
- HEAD: `5c5c2ef` (aligned with origin/main)
- Canonical repo: `obsidia-x108-proofs_REMOTE_A5F21C6B`
- Old repo (`obsidia-x108-proofs`): `.git/config` corrupted — kept local, not canonical

## Known issues

- V18_3_1 root hash mismatch: **RESOLVED** (PROOFKIT_REPORT.json regenerated 2026-05-21, all checks PASS)
- Old repo `.git/config` corruption: NOT fixed — circumvented by using REMOTE clone as canonical

## Next technical mission

Choose next mission from `docs/roadmap/NOT_YET_IMPLEMENTED_AFTER_V2.md`:

- [ ] Runtime ACT réel
- [ ] Graphiti/Brody feedback loop
- [ ] Ledger Gencoin persistant
- [ ] Tests adversariaux
- [ ] Seuils par domaine
- [ ] Vue régulateur
- [ ] Machine-checking

## Open questions

- (none)

## 2026-05-05 settings-cleanup
- branch: ci-strict-sigma-qa-no-false-error_20260502_235213
- did: removed invalid `hooks._disabled_by_default` key from `.claude/settings.json`; committed as 4ea9de5
- next: begin read-only PROOF_SENTINEL diagnosis of V18_3_1 root hash mismatch
- blocked on: nothing

## 2026-05-26 public-cleanup-freeze
- branch: main (canonical: obsidia-x108-proofs_REMOTE_A5F21C6B)
- did: phases 1-4 public repo cleanup completed + 4 git tags pushed (HEAD 5c5c2ef)
- next: choose next technical mission from NOT_YET_IMPLEMENTED_AFTER_V2.md
- blocked on: nothing

## 2026-07-08 gateway-fusion + plan-build-integral
- branch: feat/path-brody-r02-thermo-mcp-closure
- did: hook UserPromptSubmit (router->Claude Code) + pont pre-inference dans
  obsidia_cli.handle() + gateway `obsidia chat` (cascade L0/L2/brody/claude -p)
  + audit log MEASURED `audit/obsidia_gateway_usage.jsonl`. Router hackathon :
  fix route brody (unified_ir.py, 542 tests OK), .gitignore blinde (.local_*).
- plan build integral (4 phases): P0 hackathon (B1 run live MEASURED avec
  FIREWORKS_API_KEY, B11 catalogue modeles, Docker froid); P1 memoire par sens
  (fix import Shazam 05_SHAZAM, exporteur gateway_memory_index depuis ledger +
  MATH_MEMORY_INDEX ACTIVE, brancher Shazam+similarity_search 13_NUAGE au L2);
  P2 calibration chat (invariants drift/DecisionTicket dans prompt L3, traca
  M.A.P. -> audit bus, fix ANTHROPIC_MODEL settings.json, suppr patch_alphabet);
  P3 MCP (auditer 09_MCP_BRIDGE_OBSIDIA_IR AVANT d'ecrire, promotion SRL par
  operateur, de-stub Brody, benchmark OIE V0.3 MEASURED). Vigilance: 07_BDF,
  08_HEXAFLUX, 15_GUARDS vs gates router, test_cosmos_friction_eml.
- next: fin P0 (docker + run live) puis P1 etape 1 (import Shazam)
- blocked on: FIREWORKS_API_KEY (B1/B11) — a fournir par l'operateur

---

## Update protocol

At session end, the user (or `context-keeper` skill, with approval) appends a 3–5 line delta:

```
## YYYY-MM-DD <short tag>
- branch: <name>
- did: <one line>
- next: <one line>
- blocked on: <one line or "nothing">
```

When this file passes ~80 lines, oldest deltas move to `.claude/memory/snapshots/CURRENT_FOCUS-<date>.md`.
