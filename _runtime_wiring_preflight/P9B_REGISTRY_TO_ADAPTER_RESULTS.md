# P9B_REGISTRY_TO_ADAPTER_RESULTS
# _runtime_wiring_preflight/P9B_REGISTRY_TO_ADAPTER_RESULTS.md

## Run Info

- **Branche:** p8-runtime-dryrun-wiring
- **Date:** 2026-06-03
- **Runner:** pytest 9.0.3 / Python 3.13.3
- **Durée:** 0.61s

## Résultat Global

```
20 passed in 0.61s
```

**P9B_REGISTRY_TO_ADAPTER_DRY_RUN_TESTS_READY**

## Détail Tests

```
tests/test_source_registry_p9b.py::test_registry_files_exist                                PASSED
tests/test_source_registry_p9b.py::test_registry_loads_json_and_csv                         PASSED
tests/test_source_registry_p9b.py::test_registry_summary_counts_match_expected              PASSED
tests/test_source_registry_p9b.py::test_all_families_present                                PASSED
tests/test_source_registry_p9b.py::test_all_runtime_allowed_false                           PASSED
tests/test_source_registry_p9b.py::test_all_emits_act_false                                 PASSED
tests/test_source_registry_p9b.py::test_all_emits_decision_false                            PASSED
tests/test_source_registry_p9b.py::test_py_entries_are_do_not_import_runtime                PASSED
tests/test_source_registry_p9b.py::test_quarantine_archive_entries_not_routable             PASSED
tests/test_source_registry_p9b.py::test_adapter_targets_exist                               PASSED
tests/test_source_registry_p9b.py::test_route_one_entry_per_family_to_context_packet        PASSED
tests/test_source_registry_p9b.py::test_routed_packets_never_emit_act                      PASSED
tests/test_source_registry_p9b.py::test_routed_packets_have_kx108_authority                PASSED
tests/test_source_registry_p9b.py::test_route_registry_packets_context_only_allows_context_only PASSED
tests/test_source_registry_p9b.py::test_route_registry_packets_critical_action_holds       PASSED
tests/test_source_registry_p9b.py::test_no_source_pack_file_read                           PASSED
tests/test_source_registry_p9b.py::test_no_zip_extraction                                  PASSED
tests/test_source_registry_p9b.py::test_no_forbidden_imports                               PASSED
tests/test_source_registry_p9b.py::test_os3_evidence_dry_run_only                         PASSED
tests/test_source_registry_p9b.py::test_no_packages_created                               PASSED
```

## Fichiers créés en P9B

- `runtime_wiring/source_registry/registry_to_adapter_dry_run.py`
- `tests/test_source_registry_p9b.py` (20 tests)
- `runtime_wiring/source_registry/reports/P9B_REGISTRY_TO_ADAPTER_DRY_RUN_TESTS_REPORT.md`
- `_runtime_wiring_preflight/P9B_REGISTRY_TO_ADAPTER_RESULTS.md` (ce fichier)

## Routing Sample (mini démo)

| Scénario | Packets | Decision | ACT produit | proof_claim |
|----------|---------|----------|-------------|------------|
| A — context only | 4 (1/famille) | `ALLOW_CONTEXT_ONLY` | false | false |
| B — critical action | 4 (1/famille) | `HOLD` | false | false |

## Fichiers NON modifiés

- `runtime_contracts/` — intact
- `specs/` — intact
- `periphery/` — intact
- `apps/` — intact
- `_source_packs/` — intact (aucun zip ouvert)
- `_freezes/` — intact
- `.claude/settings.local.json` — intact

## Commandes de repro

```bash
# Tests
python -m pytest tests/test_source_registry_p9b.py -v

# Mini démo
python -c "
import sys; sys.path.insert(0, '.')
from runtime_wiring.source_registry.registry_loader import load_registry_json
from runtime_wiring.source_registry.registry_to_adapter_dry_run import route_registry_packets_to_x108, summarize_routing_result
entries = load_registry_json()
print(summarize_routing_result(route_registry_packets_to_x108(entries, critical_action_requested=False, sample_size=1)))
print(summarize_routing_result(route_registry_packets_to_x108(entries, critical_action_requested=True, sample_size=1)))
"
```

## Prochain chantier

P9C — Registry Router Integration Demo complète  
P9D — Commit de la branche p8-runtime-dryrun-wiring
