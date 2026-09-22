"""
R8-A.

Long objective transport.
Explicit scope transport.
Terminal remains readonly.
KX108_ONLY remains sole authority.
"""

from __future__ import annotations

import ast
import sys

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import obsidia_build as B
import obsidia_cli as C


def test_no_200_char_business_limit(
    monkeypatch,
):

    captured = {}

    def fake_plan(
        objective,
        repo_root,
    ):
        captured["objective"] = objective
        return 0

    monkeypatch.setattr(
        B,
        "cmd_plan",
        fake_plan,
    )

    objective = (
        "R8-"
        + ("x" * 100_000)
    )

    rc = B.main(
        [objective]
    )

    assert rc == 0
    assert captured["objective"] == objective


def test_file_backed_objective_large_multiline(
    tmp_path,
    monkeypatch,
):

    captured = {}

    p = tmp_path / "objective.txt"

    body = (
        "\ufeffR8 SELF-HOSTED\n"
        + (
            "specification longue gouvernee\n"
            * 5000
        )
    )

    p.write_text(
        body,
        encoding="utf-8",
    )

    def fake_plan(
        objective,
        repo_root,
    ):
        captured["objective"] = objective
        return 0

    monkeypatch.setattr(
        B,
        "cmd_plan",
        fake_plan,
    )

    rc = B.main([
        "--objective-file",
        str(p),
    ])

    assert rc == 0

    objective = captured["objective"]

    assert objective.startswith(
        "R8 SELF-HOSTED"
    )

    assert len(objective) > 100_000

    assert not objective.startswith(
        "\ufeff"
    )


def test_explicit_scope_forwarded_phase2(
    tmp_path,
    monkeypatch,
):

    captured = {}

    p = tmp_path / "objective.txt"

    p.write_text(
        "R8\nKX108_ONLY",
        encoding="utf-8",
    )

    def fake_execute(
        objective,
        approval_token,
        repo_root,
        state_dir,
        explicit_scope=None,
    ):

        captured["objective"] = objective
        captured["token"] = approval_token
        captured["scope"] = explicit_scope

        return 0

    monkeypatch.setattr(
        B,
        "cmd_execute",
        fake_execute,
    )

    token = (
        "HUMAN_APPROVED_BUILD_SESSION="
        "deadbeef:0123456789abcdef"
    )

    rc = B.main([
        "--objective-file",
        str(p),
        "--scope",
        "scripts/obsidia_cli.py",
        "--approve",
        token,
    ])

    assert rc == 0

    assert captured["scope"] == [
        "scripts/obsidia_cli.py"
    ]

    assert captured["token"] == token


def test_terminal_target_routes_exact_scope(
    monkeypatch,
):

    captured = {}

    def fake_handler(
        objective,
        explicit_scope=None,
    ):

        captured["objective"] = objective
        captured["scope"] = explicit_scope

        return "PLAN_PROPOSED"

    monkeypatch.setattr(
        C,
        "_handle_build_plan",
        fake_handler,
    )

    out = C._dispatch_build(
        "target scripts/obsidia_cli.py "
        ":: R8 explicit planning"
    )

    assert out == "PLAN_PROPOSED"

    assert captured["objective"] == (
        "R8 explicit planning"
    )

    assert captured["scope"] == [
        "scripts/obsidia_cli.py"
    ]


def test_explicit_render_replays_scope():

    plan = {
        "session_id": "deadbeef",
        "objective": "R8",
        "domain": "PERIPHERAL",
        "risk": "LOW",
        "base_sha": "a" * 40,
        "manifest_hash": "0123456789abcdef",
        "scope_mode": (
            B.SCOPE_MODE_EXPLICIT_CHILD_TARGET
        ),
        "approved_scope_hash": (
            "1111111111111111"
        ),
        "plan_authority_hash": (
            "2222222222222222"
        ),
        "worktree_proposal": "wt",
        "branch_proposal": "branch",
        "candidate_files": [
            "scripts/obsidia_cli.py"
        ],
        "approved_scope_proposal": [
            "scripts/obsidia_cli.py"
        ],
        "excluded_files": [],
        "tests_required": [],
        "gates_required": [],
        "next_human_action": (
            "HUMAN_APPROVED_BUILD_SESSION="
            "deadbeef:2222222222222222"
        ),
    }

    rendered = B.format_plan_proposed(
        plan,
        "API_DOWN",
    )

    assert (
        "scope_mode        : "
        "EXPLICIT_CHILD_TARGET"
        in rendered
    )

    assert (
        "plan_authority_hash: "
        "2222222222222222"
        in rendered
    )

    assert (
        '--scope "scripts/obsidia_cli.py"'
        in rendered
    )


def test_terminal_has_no_subprocess_calls():

    source = Path(
        C.__file__
    ).read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    violations = []

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        func = node.func

        if not isinstance(
            func,
            ast.Attribute,
        ):
            continue

        if not isinstance(
            func.value,
            ast.Name,
        ):
            continue

        if func.value.id == "subprocess":

            violations.append(
                getattr(
                    func,
                    "attr",
                    "?",
                )
            )

    assert violations == []
