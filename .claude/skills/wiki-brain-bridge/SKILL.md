---
name: wiki-brain-bridge
description: Use this skill ONLY when the user explicitly asks about Graphify, wiki-brain-skill, persistent project knowledge graph, or token reduction via knowledge graphs. The skill DOES NOT auto-install anything. It documents the integration policy, the protected-path exclusion list, and the sandbox evaluation procedure required before any installation.
obsidia_mapping_type: policy
obsidia_agents: []
obsidia_reduction: policy bridge for Graphify/wiki-brain, sandbox-only, not an Obsidia agent
---

# Wiki Brain Bridge

## Purpose

Document the policy and integration procedure for **Graphify / wiki-brain-skill** in the Obsidia X-108 repo. This skill **does not install anything**. It exists to make sure that, when the user one day decides to evaluate Graphify, the rules are already written.

## When to use

- The user explicitly asks about Graphify, wiki-brain-skill, knowledge graph, persistent project memory, or token-reduction patterns claimed by these tools.
- The user pastes a `bryan-richlab/wiki-brain-skill` install command and asks if it's safe.

## When NOT to use

- The user wants a normal code task — use the appropriate other skill.
- The user asks "reduce my tokens" without naming Graphify — direct them to `token-guard` and the token-discipline rules in `TOKEN_POLICY.md` first.

## Hard rules (non-negotiable for this repo)

1. **DO NOT auto-install** Graphify or wiki-brain-skill.
2. **Sandbox evaluation only** — install in a separate worktree or branch (e.g. `feat/eval-graphify`) before any merge.
3. **Never index protected paths** without explicit per-path approval from the user. Protected paths are listed in `.claude/context/PROTECTED_SCOPE.md`. Default exclude list (mandatory):

```
proofs/V18_3_1/**
proofs/V18_7/**
proofs/V18_8/**
proofs/lean/**
proofs/tla/**
formal/tla/**
proofs/merkle_root.json
merkle_root.json
proofs/merkle_seal.json
merkle_seal.json
proofs/rfc3161_anchor.json
server.kernel.sealed.cjs
RECUPE_SCORING/aggregation_stable.py
RECUPE_SCORING/contracts_stable.py
sigma/contracts.broken-ragnarok.py
P1_FREEZE_NOTE.md
PUBLIC_STATUS.md
.env
.env.*
secrets/**
audit/local/**
**/*.pem
vendor/wheels/**
System.*/**
Google.Protobuf.*/**
node_modules/**
artifacts/**
```

4. **Never send protected material to cloud**. Graphify must run **fully local**. If any part of the tool sends data off-machine, do not install it.
5. **Never mutate the repo**. The graph database, indexes, and caches must live OUTSIDE the repo (e.g. `~/.graphify/obsidia-x108-proofs/`), or in a top-level gitignored folder (e.g. `.graphify/` added to `.gitignore`).
6. **Never create hidden generated files inside `proofs/`, `formal/`, `sigma/`, `RECUPE_SCORING/`**. The indexer must be configured to skip writes inside any tracked folder.

## Required output format

When the user asks about Graphify / wiki-brain integration:

```
Mode: PROPOSE
Layer: AGENTIC
Files touched: none (this skill does not install)

Tool:                  Graphify / wiki-brain-skill
Status in this repo:   NOT INSTALLED (default policy)
Auto-install allowed?  NO
Sandbox eval required? YES
Cloud allowed?         NO — must run fully local

Required exclusion list:  see .claude/skills/wiki-brain-bridge/SKILL.md (full list)
Required graph location:  outside repo OR gitignored top-level folder

Proposed evaluation procedure:
  1. Create a new worktree on a sandbox branch:
       git worktree add ../obsidia-x108-eval-graphify feat/eval-graphify
  2. cd into the worktree.
  3. Install wiki-brain-skill there only (never in the main worktree).
  4. Configure the exclusion list above before any first scan.
  5. Run a dry-run (no write) and confirm zero protected paths are indexed.
  6. Inspect storage location — must be outside the worktree.
  7. Confirm no network egress during indexing (offline mode).
  8. Report findings. Do NOT promote to main without explicit user approval.

Verification commands (PREPARED, run only after user approval):
  git worktree list
  git status --short                  # in eval worktree, must be clean except for .gitignore
  git diff --name-only                # must not list any protected path

Risks if installed without these guards:
  - Indexing protected proof files → leak into graph cache
  - Hidden files in proofs/ → silent invalidation of seals
  - Cloud sync → exfiltration of sovereign material
  - Auto-update changing exclusion behavior

Approval required:  YES — explicit user "Approved." needed, plus confirmation each guard is in place.
```

## Forbidden actions

- Running `claude install` / `npm install` / any install command for Graphify automatically.
- Pretending the tool is installed when it isn't.
- Suggesting "we can just exclude later" — exclusion must be in place BEFORE first scan.
- Suggesting to send the graph to any cloud service.
- Editing `.gitignore` to hide a Graphify cache without flagging it.

## Verification checklist

- [ ] No install command was executed.
- [ ] The user has been informed of the sandbox-only policy.
- [ ] The full exclusion list is shown to the user.
- [ ] If the user proceeds, a separate branch / worktree exists for the eval.
- [ ] Cache / index storage location is outside the repo or gitignored.
- [ ] No protected path is in the indexer's input set.
