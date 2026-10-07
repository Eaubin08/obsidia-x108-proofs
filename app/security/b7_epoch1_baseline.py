"""B7 security epoch 1 baseline — frozen from docs/architecture/B7_RUNTIME_CLOSURE_20261007.md (closure
commit 44b0391e, runtime HEAD 756a6ba7). Read-only: no code path updates it. A new epoch requires an
explicit audited certification and a reviewed edit of this file (never an automatic one).

runtime_closure: the 40 modules certified in closure section 7 (b7_epoch1_closure.json).
fingerprints: SHA-256 (LF-normalized) of the security-sensitive sources at the certified HEAD.
"""
from __future__ import annotations

import json
import pathlib
from types import MappingProxyType

# certified closure module names live in a data file (read-only, checked: 40 entries, epoch 1)
_DATA = json.loads((pathlib.Path(__file__).with_name("b7_epoch1_closure.json")).read_text(encoding="utf-8"))
assert _DATA["security_epoch"] == 1 and len(_DATA["runtime_closure"]) == 40
_CLOSURE = tuple(_DATA["runtime_closure"])

BASELINE = MappingProxyType({
    "boundary_id": "B7_COGNITIVE_RESOLUTION",
    "security_epoch": 1,
    "certified_by": "docs/architecture/B7_RUNTIME_CLOSURE_20261007.md",
    "runtime_head": "756a6ba7",
    "package_prefix": "app/cognition/b7/",
    "root_module": "app.cognition.b7",
    "trust_sinks": ("admit_trusted_context", "register_derived"),
    "issue_call_sites": ("validate_candidate",),
    "external_issue_callers": 0,
    "same_process_untrusted_code": "NO_PROVEN_REACHABLE_PATH",
    "live_provider_wiring": "NOT_IMPLEMENTED",
    "memory_write": False,
    "emits_act": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
    "runtime_closure": _CLOSURE,
    "fingerprints": MappingProxyType({
        "app/cognition/b7/__init__.py": "b470a9de88d6b18a5625f6ae4f4f4ecb33ae0986e938c165823d6de8cee66538",
        "app/cognition/b7/contracts.py": "b356f84a49fb47e2a31bf9c2ba2efefad7fe57bf9f38459f0e33e5d8486ee30c",
        "app/cognition/b7/detector.py": "7cc247a25f795b14814f79b0d5fb46994354b3cf3658e00fabb5748f60a2baaf",
        "app/cognition/b7/router.py": "b2eebed1a94b3eb1e05118933aa0dba5c17c10735def40b53167f37635a3b377",
        "app/cognition/b7/translator.py": "5f2419c7a5ade7d2f7968c3adcacf80229081cacd71f2da0035636b6803eeaa2",
        "app/cognition/b7/validation.py": "8cee7f09f4bcab3a19d3cdb3559e24beaa8d3f3b63f0bb7add632770e127527a",
        "app/harness/state_explicit/contracts.py": "ee12a0542eb92a4eb9b7b3649305488355e7caf8ec15ab529180359758ad09c4",
    }),
    "security_sentinel_hardening": "HOLD_FUTURE",
    "pf_freeze_revisit_required": True,
})
