"""Runtime-independent self-checks of the M32 test oracles (these may PASS before GREEN)."""
from __future__ import annotations

import hashlib
import unicodedata

from tests.m32 import _harness as H


def test_reference_canonical_json_rules():
    assert H.ref_canonical_json({"b": 1, "a": [2, 1]}) == '{"a":[2,1],"b":1}'
    assert H.ref_canonical_json({"k": "é"}) == '{"k":"é"}'
    assert H.ref_canonical_json(unicodedata.normalize("NFD", "é")) == H.ref_canonical_json("é")


def test_reference_invocation_id_is_order_independent_and_hex64():
    d = H.ref_datum(H.TEXT_T, H.TEXT_V1, "v")
    a = H.ref_invocation_id("test.pair", "v1", [("a", d), ("b", d)], {})
    b = H.ref_invocation_id("test.pair", "v1", [("b", d), ("a", d)], {})
    assert a == b and H.HEX64.match(a)
    pre = ('{"immutable_config":{},"inputs":[{"datum":{"datum_type":"test.text","schema_version":"v1","value":"v"},'
           '"slot_name":"a"},{"datum":{"datum_type":"test.text","schema_version":"v1","value":"v"},"slot_name":"b"}],'
           '"primitive_spec_version":"v1","primitive_type":"test.pair","schema_version":"m32.invocation.v1"}')
    assert a == hashlib.sha256(pre.encode("utf-8")).hexdigest()


def test_protected_paths_come_from_seal_and_sentinel():
    paths = H.protected_paths()
    for p in ("app/cognition", "app/knowledge/b8", "app/harness/state_explicit", "scripts/foundation_sentinel.py",
              "tests/b7", "tests/b8", "tests/b9", "tests/security"):
        assert p in paths
    assert not any(p.startswith(("app/primitives", "tests/m32")) for p in paths)


def test_m32_base_is_ancestor_of_head():
    import subprocess
    rc = subprocess.run(["git", "merge-base", "--is-ancestor", H.M32_BASE, "HEAD"], cwd=H.REPO).returncode
    assert rc == 0
