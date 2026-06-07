# P65 — OS Adapters : Déblocage Bus Registry

**Audit ID :** P65  
**Statut :** `P65_OS_ADAPTERS_UNLOCK_BUS_REGISTRY_READY`  
**Mode :** `ADAPTER_ONLY`  
**Branche :** `p65-os-adapters-unlock-bus-registry`  
**Date :** 2026-06-07

---

## Objectif P65

Adapter les 4 candidats OS readonly (classifiés SAFE_READONLY_ADAPTER_CANDIDATE / IMPORT_AFTER_ADAPTER en P62) et débloquer `apps/obsidia_api/bus/registry.py` (bloqué depuis P61 car l'import `from modules.os_trad.adapter import os_trad_propose` ne résolvait pas).

Tous les adapters sont `DRY_RUN_ONLY=True` — aucun runtime actif, aucun ACT, aucun write.

---

## Phrase verrou P65

> "Tous les adapters OS P65 sont DRY_RUN_ONLY. Aucun runtime actif. Aucun ACT. Aucun write. Le bus registry est débloqué uniquement par substitution d'import — aucune route active n'est créée."

---

## Fichiers adaptés (5 fichiers)

### 1. `apps/obsidia_api/os_adapters/determinism.py`

| Champ | Valeur |
|---|---|
| Source | `engine/os0/determinism.py` |
| Source SHA256 | `168fa335d75dd9aafec0ce2dd2d32a61615cc08a096cf181649261435ff36bc5` |
| Target SHA256 | `0ac26197b450875780e49847ac18bb1e0a50d1801a1c390fcb0ec2693dec709c` |
| Classification | `SAFE_READONLY_ADAPTER_CANDIDATE` |
| Surface | `AUDIT_TOOLING` |
| Action | `ADAPTED_READONLY` |

**Modifications :** `DRY_RUN_ONLY=True` ajouté, `_BOUNDARY` déclaré. Logique `canonical_hash` conservée intégralement. Fonction pure — aucun write, aucune dépendance externe.

---

### 2. `apps/obsidia_api/os_adapters/parse_input.py`

| Champ | Valeur |
|---|---|
| Source | `engine/os1/parse_input.py` |
| Source SHA256 | `24de1ed54026ba402192bbfd6b4d96380e46aa4f7304b28a5bd968e0650ced05` |
| Target SHA256 | `b62058cd6f852cb57f0c68e320025819203c7408fcba61ea13e5001569390e0f` |
| Classification | `SAFE_READONLY_ADAPTER_CANDIDATE` |
| Surface | `AUDIT_TOOLING` |
| Action | `ADAPTED_STANDALONE` |

**Modifications :** Suppression dépendance `obsidia_os0.ir` (package vendor absent du repo proof). Les IR nodes (`FLOW`, `STATE`, `READ`, `WRITE`, `VALUE`, `EVENT`, `CALL`) sont remplacés par des plain dicts via `_ir_node(kind, **kwargs)`. `_dry_run=True` ajouté au retour. Logique de parsing identique.

---

### 3. `apps/obsidia_api/os_adapters/svg.py`

| Champ | Valeur |
|---|---|
| Source | `engine/os3/svg.py` |
| Source SHA256 | `0e12171c9c2104b4b0e1a22c67d73b0f75d43ecfaa2a6a14d029ee75db212c76` |
| Target SHA256 | `104bbcd99268fee640c290d468a30d08f70e82544a1f183073f8238e408fb97e` |
| Classification | `SAFE_READONLY_ADAPTER_CANDIDATE` |
| Surface | `AUDIT_TOOLING` |
| Action | `ADAPTED_DRY_RUN` |

**Modifications :** Original fait `open(out_path, "w")` — write disque interdit en DRY_RUN_ONLY. `out_path` rendu optionnel (`""`), jamais utilisé. `render_core_svg` retourne toujours le SVG string. Guard `ValueError` si `DRY_RUN_ONLY=False`.

---

### 4. `apps/obsidia_api/os_adapters/os_trad_adapter.py`

| Champ | Valeur |
|---|---|
| Source | `engine/core_full/modules/os_trad/adapter.py` |
| Source SHA256 | `fe4d904bf27d007f9f920694a029f06f798e7cb1e41858424a7899b2345daa8c` |
| Target SHA256 | `cadb07c0386f26f03e49391c952c6ecc903ccb5315ec165200698ae20539bd81` |
| Classification | `IMPORT_AFTER_ADAPTER` |
| Surface | `BUS_ADAPTER` |
| Action | `ADAPTED_DRY_RUN` |

**Modifications :** Original manipule `sys.path` pour trouver `vendor/proof/runner.py` et appelle `proof.runner.build`. Ces répertoires sont absents du repo proof. DRY_RUN_ONLY : validation des inputs uniquement, `build_skipped=True` dans la proposition. ACTION interdit (`ValueError`). Débloque `apps/obsidia_api/bus/registry.py`.

---

### 5. `apps/obsidia_api/bus/registry.py`

| Champ | Valeur |
|---|---|
| Source | `engine/bus/registry.py` |
| Source SHA256 | `0c7d16fe14a4ba5083658c83bf8cf4584042e816f24eb2c5aa32c9925271bc90` |
| Target SHA256 | `37e4a6dc8c0c6ec6692be91d7222745de827ca95c4f5de7002e2abbe60088e88` |
| Classification | `BUS_ADAPTER_BATCH` |
| Surface | `BUS_ADAPTER` |
| Action | `ADAPTED_DRY_RUN` |

**Modifications :** Import corrigé : `from modules.os_trad.adapter import os_trad_propose` → `from apps.obsidia_api.os_adapters.os_trad_adapter import os_trad_propose`. `DRY_RUN_ONLY=True`, `_BOUNDARY` déclaré. `build_default_router()` enregistre uniquement `OS_TRAD` en mode PROPOSE.

---

## Matrice de sécurité P65

| Fichier | readonly | dry_run_only | emits_act | memory_write | graphiti_write | kernel_mutation |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `os_adapters/determinism.py` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `os_adapters/parse_input.py` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `os_adapters/svg.py` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `os_adapters/os_trad_adapter.py` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `bus/registry.py` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

---

## Surfaces NON modifiées

| Surface | Statut |
|---|---|
| `sigma/` | INCHANGÉ — veto-only P56D maintenu |
| `runtime_wiring/` | INCHANGÉ — gel P56E maintenu |
| `apps/obsidia_api/routes/` | INCHANGÉ — aucune route active créée |
| `proofs/V18_3_1/` | INCHANGÉ — proof supérieure préservée |
| `engine_runtime / engine_final / kernel` | NON IMPORTÉS |

---

## Règles do_not_forget (héritage P64)

1. `DRY_RUN_ONLY=True` sur chaque adapter — jamais `False`
2. `emits_act=False` — aucun ACT émis
3. `memory_write=False` — aucune écriture mémoire
4. `graphiti_write=False` — aucune écriture Graphiti
5. `kernel_mutation=False` — aucune mutation kernel
6. ACTION interdit dans tous les adapters bus
7. Sigma post-Guard veto-only (P56D) — ne pas promouvoir
8. Ne pas importer engine_runtime / engine_final / kernel
9. OS2 gamma=1.0 proof est supérieur — ne pas réimporter OS2 core (gamma=0.5 SUPERSEDED)
10. Ne pas modifier proofs/V18_3_1 (version supérieure)
11. `decision_authority="KX108_ONLY"` dans tous les `_BOUNDARY`
12. Ne pas créer de route active dans apps/obsidia_api/routes/

---

## Vérification de compilation

Tous les fichiers vérifiés avec `python -m py_compile` :

```
apps/obsidia_api/os_adapters/__init__.py    COMPILE OK
apps/obsidia_api/os_adapters/determinism.py COMPILE OK
apps/obsidia_api/os_adapters/parse_input.py COMPILE OK
apps/obsidia_api/os_adapters/svg.py         COMPILE OK
apps/obsidia_api/os_adapters/os_trad_adapter.py COMPILE OK
apps/obsidia_api/bus/registry.py            COMPILE OK
```

Vérification runtime :

```
canonical_hash({'x': 1}) → 64-char hex ✓
parse_input('x = 1') → {"program": [...], "_dry_run": True} ✓
render_core_svg(...) → "<svg>...</svg>" string ✓
os_trad_propose(PROPOSE) → {"ok": True, "dry_run": True, "build_skipped": True} ✓
build_default_router() → Router modules=['OS_TRAD'] ✓
run_propose_modules(dry_run=True) → {"_dry_run": True, "_act_emitted": False} ✓
```

---

## Palier suivant

**P66 — AGENTS_COMPLEMENTARY_RECONCILIATION**

Réconciliation des agents complémentaires identifiés comme IMPORT_SAFE en P62 (2 fichiers agents). Conditions : mêmes contraintes DRY_RUN_ONLY, aucune activation runtime.

---

**Verdict :** `P65_OS_ADAPTERS_UNLOCK_BUS_REGISTRY_READY`
