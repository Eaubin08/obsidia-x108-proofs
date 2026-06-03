# P9C_INTEGRATION_DEMO_RESULTS
# _runtime_wiring_preflight/P9C_INTEGRATION_DEMO_RESULTS.md

## Run Info

- **Branche:** p8-runtime-dryrun-wiring
- **Date:** 2026-06-03
- **Script:** `runtime_wiring/source_registry/p9c_integration_demo.py`

## Résultat Global

```
P9C_REGISTRY_ROUTER_INTEGRATION_DEMO_READY
```

## Pipeline Exécuté

```
source_file_registry.json (14 779 entries)
  -> Familles vérifiées : 4/4
  -> Routable total : 14 182
  -> Rejetées : 597
  -> Packets produits : 4 (1/famille)
  -> Scénario A : ALLOW_CONTEXT_ONLY
  -> Scénario B : HOLD
  -> proof_claim : false
  -> zip_extraction : false
  -> source_pack_import : false
```

## Tests P8C + P9B

```
python -m pytest tests/test_runtime_wiring_p8c.py tests/test_source_registry_p9b.py -q
34 passed in 0.63s
```

## Fichiers créés en P9C

- `runtime_wiring/source_registry/p9c_integration_demo.py`
- `runtime_wiring/source_registry/reports/P9C_REGISTRY_ROUTER_INTEGRATION_DEMO_REPORT.md`
- `_runtime_wiring_preflight/P9C_INTEGRATION_DEMO_RESULTS.md` (ce fichier)

## Fichiers NON modifiés

- `runtime_contracts/` — intact
- `specs/` — intact
- `periphery/` — intact
- `apps/` — intact
- `_source_packs/` — intact
- `_freezes/` — intact
- `.claude/settings.local.json` — intact

## Commande de repro

```bash
python runtime_wiring/source_registry/p9c_integration_demo.py
```

## Prochain chantier

P9D — Branch Commit Preflight
