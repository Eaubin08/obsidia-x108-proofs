# External Tools Policy

> Rules for installing / using anything outside the repo's own toolchain.

## Default

**Do not install anything automatically.** Period.

## Specific tools

### autoskills

- **Status**: NOT ALLOWED in this repo by default.
- **Reason**: autoskills installs generic skills based on detected stack (`package.json`, framework files). This repo is Lean 4 + TLA+ + Merkle + RFC3161 + Sigma + PowerShell — not a generic stack. Generic skills risk:
  - Auto-formatting proof files (invalidates seals)
  - Adding lint hooks on `.lean` / `.tla` files
  - Suggesting refactors that break X-108 invariants
  - Treating frozen files as "to be updated"
- **Allowed only if**: user explicitly approves AND we're in a sandbox branch.

### Graphify / wiki-brain-skill

- **Status**: NOT INSTALLED by default. Bridge documented in `.claude/skills/wiki-brain-bridge/SKILL.md`.
- **Reason**: Graphify is interesting for token reduction (claimed 75× fewer tokens by building a persistent local knowledge graph), but for THIS repo it must be evaluated carefully because:
  - It indexes files — protected proof / seal / Merkle / RFC3161 paths must be excluded.
  - The graph must stay 100 % local — never sent to cloud.
  - It must not mutate the repo or create hidden generated files inside proof folders.
- **Allowed only if**: user explicitly approves AND a sandbox / separate branch evaluation has happened first AND an exclusion list for protected paths is in place.

### MCP servers

- **Status**: NOT CONFIGURED by default. No `mcpServers` block in `settings.json`.
- **Reason**: MCP servers (GitHub, database, browser, search) extend Claude's reach but each one is an external trust boundary. For this repo:
  - Never store API tokens / credentials in `settings.json`.
  - Never paste tokens into config files.
  - Database MCP servers should never have write access to production.
- **Allowed only if**: user explicitly requests AND tokens are passed via OS env vars (not committed) AND scope is read-only by default.

### Personal token URLs

- **Never fetch** URLs containing auth tokens (`?token=...`, `?mcp_token=...`, signed URLs).
- **Never store** them in any config file.
- **Never quote them back** in output.

### Package managers (`npm install`, `pip install`, `winget install`)

- **Default deny** — explicit in `settings.json`.
- **Allowed only if**: user explicitly requests, with the exact package name AND the requirements file or lock file is updated atomically in the same commit.

### `/ultrareview`

- **Status**: NOT ALLOWED.
- **Reason**: broad cross-file review = broad context load = high token cost + risk of false connections.
- **Alternative**: targeted `/proofcheck`, `/sigmacheck`, `/route` commands.

## Why this matters

This repo carries cryptographic proofs (Merkle, seal, RFC3161). External tools that "tidy up", "auto-format", or "run all the things" can silently invalidate proofs without producing visible code changes that look meaningful. The cost of one such invalidation is high: re-anchoring requires an external TSA call and re-signing.

## How to enable any of the above

Always via:

1. User's explicit request in chat ("yes, install X for this task").
2. Sandbox / separate branch first when relevant.
3. Documented exclusion list for protected paths.
4. Verification commands run after install.
5. `EXTERNAL_TOOLS_POLICY.md` updated to reflect the new approval.
