# P8B_CREATED_FILES
# _runtime_wiring_preflight/P8B_CREATED_FILES.md
# Inventaire des fichiers créés en phase P8B

## Branche

`p8-runtime-dryrun-wiring` (créée depuis `main` @ ea27f59)

## Fichiers créés

### runtime_wiring/ (nouveau module — isolé)

- `runtime_wiring/__init__.py`
- `runtime_wiring/packet_types.py`
- `runtime_wiring/contracts_loader.py`
- `runtime_wiring/source_adapters.py`
- `runtime_wiring/x108_admission_stub.py`
- `runtime_wiring/os3_evidence_stub.py`
- `runtime_wiring/dry_run_packet_router.py`
- `runtime_wiring/p8b_demo.py`
- `runtime_wiring/README.md`
- `runtime_wiring/reports/P8B_RUNTIME_DRY_RUN_WIRING_REPORT.md`

### Preflight

- `_runtime_wiring_preflight/P8B_CREATED_FILES.md` (ce fichier)

## Fichiers NON modifiés

Conformément aux contraintes P8B_DRY_RUN_WIRING_ONLY :

- `runtime_contracts/` — aucune modification
- `specs/` — aucune modification
- `periphery/` — aucune modification
- `apps/` — aucune modification
- `connectors/` — aucune modification
- `sigma/` — aucune modification
- `proofs/` — aucune modification
- `formal/` — aucune modification
- `tests/` — aucune modification
- `_source_packs/` — aucune modification
- `_freezes/` — aucune modification
- `.claude/settings.local.json` — aucune modification

## Garantie d'isolation

`runtime_wiring/` importe UNIQUEMENT depuis :
- Python stdlib : `dataclasses`, `hashlib`, `json`, `pathlib`, `datetime`, `typing`, `sys`
- Ses propres modules internes (`from .packet_types import ...`)

Il N'importe PAS depuis :
- `apps/`
- `periphery/`
- `connectors/`
- `sigma/`
- `_source_packs/`
- Tout package tiers

## Vérification de l'isolation

```bash
python -c "
import ast, pathlib
violations = []
for f in pathlib.Path('runtime_wiring').glob('*.py'):
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = getattr(node, 'module', '') or ''
            names = [a.name for a in getattr(node, 'names', [])]
            combined = mod + ' ' + ' '.join(names)
            if any(x in combined for x in ['apps', 'periphery', 'connectors', 'sigma', '_source_packs']):
                violations.append(f'FORBIDDEN: {f}: {mod} {names}')
if violations:
    for v in violations: print(v)
else:
    print('ISOLATION OK — aucun import interdit détecté')
"
```

## Vérification de la démo

```bash
python runtime_wiring/p8b_demo.py
```

Attendu :
- `scenario_a_context_only.decision_ticket.decision = "ALLOW_CONTEXT_ONLY"`
- `scenario_b_critical_action.decision_ticket.decision = "HOLD"`
- `boundary_enforcement_summary.all_packets_no_act = true`
- `boundary_enforcement_summary.all_packets_kx108_authority = true`
