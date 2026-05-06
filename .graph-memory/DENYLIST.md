# Graph Memory Sandbox — DENYLIST

These paths must never be indexed by Graphify / wiki-brain in this repo.

## Proof / freeze / seal

- proofs/V18_*/**
- proofs/lean/**
- proofs/tla/**
- formal/tla/**
- proofs/merkle_root.json
- proofs/merkle_seal.json
- merkle_root.json
- merkle_seal.json
- proofs/rfc3161_anchor.json
- server.kernel.sealed.cjs
- any file containing root/seal/hash/anchor/freeze in its name

## Secrets / local-only data

- .env
- .env.*
- secrets/**
- **/*.pem
- audit/local/**
- archive/diagnostics/local_diag/**

## Frozen / vendored / intentional fixtures

- RECUPE_SCORING/aggregation_stable.py
- RECUPE_SCORING/contracts_stable.py
- sigma/contracts.broken-ragnarok.py
- vendor/wheels/**
- System.*/**
- Google.Protobuf.*/**

## Generated / heavy / noisy

- node_modules/**
- .git/**
- __pycache__/**
- .pytest_cache/**
- artifacts/**
- archive/**
- staging/runtime_candidates/**
