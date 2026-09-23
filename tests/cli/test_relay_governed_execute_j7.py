from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from pathlib import Path


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


import obsidia_cognitive_governed_runtime_handoff_v0 as J3
import obsidia_governed_execution_driver_v0 as DRV
import obsidia_jarvis_governed_mutation_v0 as J5
import obsidia_relay_v0 as R


_EAH = "e" * 64


def _proposal(
    target_path: str = "target.txt",
) -> dict:
    return J3.prepare_cognitive_governed_handoff(
        mission_id="mission-j7-001",
        provider_id="jarvis-openjarvis",
        capability=J5.CAPABILITY_ID,
        payload={
            "source_git_commit":
                "a" * 40,
            "source_historical_path":
                "source.txt",
            "target_path":
                target_path,
            "test_contract":
                {"checks": []},
            "objective":
                "J7 governed resume",
        },
        domain="JARVIS_OPENJARVIS",
        action_id="action-j7-001",
        intent="resume governed update",
        action_type=J5.ACTION_TYPE,
        irreversible=False,
    )


def _prepare_request(
    root: Path,
) -> dict:
    repo = root / "exec-wt"
    repo.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        repo / "target.txt"
    ).write_text(
        "A\n",
        encoding="utf-8",
    )

    stores = {}

    for name in (
        "ledger",
        "selector",
        "execution",
        "pec",
    ):
        stores[name] = root / name
        stores[name].mkdir(
            parents=True,
            exist_ok=True,
        )

    return {
        "proposal":
            _proposal(),
        "execution_worktree_path":
            str(repo),
        "main_worktree_path":
            str(root / "main"),
        "branch_name":
            "j7-test-branch",
        "base_sha":
            "b" * 40,
        "ledger_dir":
            str(stores["ledger"]),
        "selector_dir":
            str(stores["selector"]),
        "execution_dir":
            str(stores["execution"]),
        "pre_execution_context_dir":
            str(stores["pec"]),
        "repository_identity":
            "j7-test-repo",
    }


def _execute_request(
    root: Path,
) -> dict:
    out = {}

    mapping = {
        "kx108_pre_decision_dir":
            "kxpre",
        "kx108_post_decision_dir":
            "kxpost",
        "test_contract_results_dir":
            "tcr",
        "sealed_receipt_dir":
            "sar",
        "sealed_rollback_evidence_dir":
            "sre",
        "rollback_result_dir":
            "rbk",
    }

    for field, name in mapping.items():
        path = root / name
        path.mkdir(
            parents=True,
            exist_ok=True,
        )
        out[field] = str(path)

    return out


class RelayGovernedExecuteJ7Tests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.tmp = Path(
            tempfile.mkdtemp(
                prefix="j7-relay-"
            )
        )

        self.store = (
            self.tmp / "relay-store"
        )

        self.orig_prepare = (
            J5.prepare_jarvis_governed_mutation
        )

        self.orig_execute = (
            J5.execute_jarvis_governed_mutation
        )

        self.orig_hold = (
            R._RD.respond_to_hold
        )

    def tearDown(self) -> None:
        J5.prepare_jarvis_governed_mutation = (
            self.orig_prepare
        )

        J5.execute_jarvis_governed_mutation = (
            self.orig_execute
        )

        R._RD.respond_to_hold = (
            self.orig_hold
        )

    def _open_j7_hold(self):
        def fake_prepare(
            proposal,
            **kwargs,
        ):
            return {
                "status":
                    DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
                "j5_phase":
                    J5.PREPARE_PHASE,
                "j5_plan_hash":
                    proposal["plan_hash"],
                "execution_authority_hash":
                    _EAH,
                "batch_execution_id":
                    "batch-j7",
                "child_execution_id":
                    "child-j7",
                "target_mutated":
                    False,
                "kx108_invocations":
                    0,
                "human_approval_created":
                    False,
                "human_authorization_consumed":
                    False,
                "jarvis_authority":
                    "NONE",
                "decision_authority":
                    "KX108_ONLY",
            }

        J5.prepare_jarvis_governed_mutation = (
            fake_prepare
        )

        request = _prepare_request(
            self.tmp
        )

        out = R.relay_submit_mission(
            requested_outcome=(
                "prepare governed update"
            ),
            mission_kind=(
                R.KIND_GOVERNED_UPDATE
            ),
            target="target.txt",
            store_dir=self.store,
            governed_update_request=request,
        )

        self.assertEqual(
            out["mission_state"],
            R.MISSION_HOLD,
        )

        self.assertEqual(
            out["execution_authority_hash"],
            _EAH,
        )

        return out, request

    def _fail_if_called(self):
        def fail(*args, **kwargs):
            raise AssertionError(
                "forbidden call"
            )
        return fail

    def _valid_execute_result(self):
        return {
            "status":
                R.GOVERNED_EXECUTION_KEEP_STATUS,
            "j5_phase":
                J5.EXECUTE_PHASE,
            "human_authorization_consumed":
                True,
            "human_authorization_reference":
                "human-j7",
            "jarvis_authority":
                "NONE",
            "decision_authority":
                "KX108_ONLY",
            "kx108_pre_gate":
                "ALLOW",
            "kx108_post_gate":
                "ALLOW",
            "target_mutated":
                True,
        }

    def test_01_missing_eah_rejected_and_hold_preserved(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            self._fail_if_called()
        )

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="human-j7",
            resolution="approved",
            store_dir=self.store,
            governed_execute_request=(
                _execute_request(
                    self.tmp
                )
            ),
        )

        self.assertEqual(
            out["status"],
            "RELAY_REJECTED",
        )

        self.assertEqual(
            out["reason"],
            "HUMAN_AUTHORIZED_EXECUTION_AUTHORITY_HASH_REQUIRED",
        )

        status = R.relay_get_status(
            prepared[
                "relay_mission_id"
            ],
            store_dir=self.store,
        )

        self.assertEqual(
            status["mission_state"],
            R.MISSION_HOLD,
        )

    def test_02_wrong_eah_rejected_before_human_record(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            self._fail_if_called()
        )

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="human-j7",
            resolution="approved",
            store_dir=self.store,
            human_authorized_execution_authority_hash=(
                "f" * 64
            ),
            governed_execute_request=(
                _execute_request(
                    self.tmp
                )
            ),
        )

        self.assertEqual(
            out["reason"],
            "HUMAN_AUTHORIZED_EAH_MISMATCH",
        )

        self.assertEqual(
            R.relay_get_status(
                prepared[
                    "relay_mission_id"
                ],
                store_dir=self.store,
            )["mission_state"],
            R.MISSION_HOLD,
        )

    def test_03_plain_yes_is_not_authority(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            self._fail_if_called()
        )

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        for text in (
            "yes",
            "approve",
            "approved by operator",
        ):
            with self.subTest(
                resolution=text
            ):
                out = (
                    R.relay_respond_to_hold(
                        relay_mission_id=(
                            prepared[
                                "relay_mission_id"
                            ]
                        ),
                        human_decision_ref=(
                            "human-j7"
                        ),
                        resolution=text,
                        store_dir=self.store,
                        governed_execute_request=(
                            _execute_request(
                                self.tmp
                            )
                        ),
                    )
                )

                self.assertEqual(
                    out["status"],
                    "RELAY_REJECTED",
                )

    def test_04_blank_human_ref_rejected(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="   ",
            resolution="approved",
            store_dir=self.store,
            human_authorized_execution_authority_hash=(
                _EAH
            ),
            governed_execute_request=(
                _execute_request(
                    self.tmp
                )
            ),
        )

        self.assertEqual(
            out["reason"],
            "HUMAN_DECISION_REF_REQUIRED",
        )

    def test_05_execute_request_required(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            self._fail_if_called()
        )

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="human-j7",
            resolution="approved",
            store_dir=self.store,
            human_authorized_execution_authority_hash=(
                _EAH
            ),
        )

        self.assertEqual(
            out["reason"],
            "GOVERNED_EXECUTE_REQUEST_REQUIRED",
        )

    def test_06_execute_request_scope_and_authority_injection_rejected(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            self._fail_if_called()
        )

        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        bad_cases = (
            (
                "unknown",
                {
                    **_execute_request(
                        self.tmp / "unknown"
                    ),
                    "shell_command":
                        "whoami",
                },
            ),
            (
                "authority",
                {
                    **_execute_request(
                        self.tmp / "authority"
                    ),
                    "human_authorization_reference":
                        "forged",
                },
            ),
            (
                "approval-store",
                {
                    **_execute_request(
                        self.tmp / "approval-store"
                    ),
                    "approval_dir":
                        str(
                            self.tmp
                            / "separate-approval-store"
                        ),
                },
            ),
        )

        for label, request in bad_cases:
            with self.subTest(
                label=label
            ):
                out = (
                    R.relay_respond_to_hold(
                        relay_mission_id=(
                            prepared[
                                "relay_mission_id"
                            ]
                        ),
                        human_decision_ref=(
                            "human-j7"
                        ),
                        resolution="approved",
                        store_dir=self.store,
                        human_authorized_execution_authority_hash=(
                            _EAH
                        ),
                        governed_execute_request=(
                            request
                        ),
                    )
                )

                self.assertEqual(
                    out["status"],
                    "RELAY_REJECTED",
                )

    def test_07_exact_eah_records_human_response_then_calls_j5_once(
        self,
    ) -> None:
        prepared, request = (
            self._open_j7_hold()
        )

        hold_calls = []
        execute_calls = []

        def fake_hold(**kwargs):
            hold_calls.append(kwargs)
            return {
                "status":
                    "HOLD_RESPONSE_RECORDED_INERT",
                "hold_response_id":
                    "ghold-j7",
                "grants_capability":
                    False,
                "starts_execution":
                    False,
                "cg_b_inert":
                    True,
            }

        def fake_execute(
            prepared_result,
            **kwargs,
        ):
            execute_calls.append(
                (
                    prepared_result,
                    kwargs,
                )
            )
            return (
                self._valid_execute_result()
            )

        R._RD.respond_to_hold = (
            fake_hold
        )

        J5.execute_jarvis_governed_mutation = (
            fake_execute
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="human-j7",
            resolution=(
                "operator approves exact EAH"
            ),
            store_dir=self.store,
            human_authorized_execution_authority_hash=(
                _EAH
            ),
            governed_execute_request=(
                _execute_request(
                    self.tmp
                )
            ),
        )

        self.assertEqual(
            len(hold_calls),
            1,
        )

        self.assertEqual(
            len(execute_calls),
            1,
        )

        self.assertEqual(
            execute_calls[0][1][
                "human_authorized_execution_authority_hash"
            ],
            _EAH,
        )

        self.assertEqual(
            execute_calls[0][1][
                "human_authorization_reference"
            ],
            "human-j7",
        )

        self.assertEqual(
            execute_calls[0][1][
                "execution_dir"
            ],
            request["execution_dir"],
        )

        self.assertEqual(
            execute_calls[0][1][
                "repo_root"
            ],
            request[
                "execution_worktree_path"
            ],
        )

        self.assertEqual(
            out["mission_state"],
            R.MISSION_COMPLETE,
        )

        self.assertIs(
            out[
                "same_mission_resumed"
            ],
            True,
        )

        self.assertIs(
            out["scope_expanded"],
            False,
        )

        self.assertEqual(
            out["kx108_pre_gate"],
            "ALLOW",
        )

        self.assertEqual(
            out["kx108_post_gate"],
            "ALLOW",
        )

        self.assertEqual(
            out["jarvis_authority"],
            "NONE",
        )

        self.assertEqual(
            out["decision_authority"],
            "KX108_ONLY",
        )

    def test_08_non_keep_is_never_false_complete(
        self,
    ) -> None:
        prepared, _ = self._open_j7_hold()

        R._RD.respond_to_hold = (
            lambda **kwargs: {
                "hold_response_id":
                    "ghold-j7-fail"
            }
        )

        J5.execute_jarvis_governed_mutation = (
            lambda prepared_result, **kwargs: {
                "status":
                    "REJECTED_ROLLED_BACK",
                "j5_phase":
                    J5.EXECUTE_PHASE,
                "human_authorization_consumed":
                    True,
                "jarvis_authority":
                    "NONE",
                "decision_authority":
                    "KX108_ONLY",
                "kx108_pre_gate":
                    "ALLOW",
                "kx108_post_gate":
                    "HOLD",
                "target_mutated":
                    False,
            }
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                prepared[
                    "relay_mission_id"
                ]
            ),
            human_decision_ref="human-j7",
            resolution="approved",
            store_dir=self.store,
            human_authorized_execution_authority_hash=(
                _EAH
            ),
            governed_execute_request=(
                _execute_request(
                    self.tmp
                )
            ),
        )

        self.assertEqual(
            out["mission_state"],
            R.MISSION_FAILED,
        )

        self.assertNotEqual(
            out["status"],
            "RELAY_MISSION_"
            + R.MISSION_COMPLETE,
        )

    def test_09_legacy_human_hold_unchanged(
        self,
    ) -> None:
        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        h = R.relay_submit_mission(
            requested_outcome=(
                "authorize production change"
            ),
            mission_kind=(
                R.KIND_HUMAN_DECISION
            ),
            store_dir=self.store,
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                h["relay_mission_id"]
            ),
            human_decision_ref=(
                "human-legacy"
            ),
            resolution="approved",
            store_dir=self.store,
        )

        self.assertEqual(
            out["mission_state"],
            R.MISSION_COMPLETE,
        )

        self.assertIs(
            out[
                "same_mission_resumed"
            ],
            True,
        )

        self.assertIs(
            out["scope_expanded"],
            False,
        )

    def test_10_legacy_governed_hold_without_j6_prepare_does_not_execute(
        self,
    ) -> None:
        J5.execute_jarvis_governed_mutation = (
            self._fail_if_called()
        )

        h = R.relay_submit_mission(
            requested_outcome=(
                "legacy governed hold"
            ),
            mission_kind=(
                R.KIND_GOVERNED_UPDATE
            ),
            store_dir=self.store,
        )

        self.assertIs(
            h["governed_prepare_only"],
            False,
        )

        out = R.relay_respond_to_hold(
            relay_mission_id=(
                h["relay_mission_id"]
            ),
            human_decision_ref=(
                "human-legacy-governed"
            ),
            resolution="legacy resolution",
            store_dir=self.store,
        )

        self.assertEqual(
            out["mission_state"],
            R.MISSION_COMPLETE,
        )

    def test_11_static_relay_has_only_j5_execution_seam(
        self,
    ) -> None:
        src = Path(
            R.__file__
        ).read_text(
            encoding="utf-8-sig"
        )

        self.assertEqual(
            src.count(
                "execute_jarvis_governed_mutation("
            ),
            1,
        )

        for banned in (
            "store_approval_artifact(",
            "run_governed_content_apply(",
            "execute_governed_remediation(",
            "run_tooling_build_pipeline(",
        ):
            self.assertNotIn(
                banned,
                src,
            )


if __name__ == "__main__":
    unittest.main()



def test_j7_keep_status_matches_canonical_driver():
    assert (
        R.GOVERNED_EXECUTION_KEEP_STATUS
        == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    )




# =====================================================================
# J7 REAL E2E
#
# Relay J6 PREPARE
# -> exact EAH
# -> MISSION_HOLD
# -> explicit human resume
# -> J5 EXECUTE
# -> real canonical driver
# -> real KX108_PRE
# -> governed mutation
# -> real KX108_POST
# -> KEEP / COMPLETE
#
# Everything runs in a temporary isolated Git repository/worktree.
# No canonical repo mutation and no Git disposition.
# =====================================================================


def _j7_git(repo: Path, *args: str) -> str:
    import subprocess

    r = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )

    assert r.returncode == 0, (
        f"git {args}: {r.stderr}"
    )

    return r.stdout.strip()


def _j7_real_world(tmp_path: Path) -> dict:
    import obsidia_test_contract as TC

    main = tmp_path / "main"
    exec_wt = tmp_path / "exec-wt"

    target_rel = (
        "periphery/xdomain/"
        "j7_relay_target_v0.txt"
    )

    source_rel = (
        "periphery/xdomain/"
        "j7_relay_source_v0.txt"
    )

    target_a = (
        b"J7_RELAY_REAL_E2E\n"
        b"state: BEFORE\n"
    )

    source_b = (
        b"J7_RELAY_REAL_E2E\n"
        b"state: AFTER_GOVERNED_APPLY\n"
    )

    (
        main / "periphery" / "xdomain"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        main / target_rel
    ).write_bytes(
        target_a
    )

    (
        main / source_rel
    ).write_bytes(
        source_b
    )

    _j7_git(
        main,
        "init",
        "-q",
    )

    _j7_git(
        main,
        "config",
        "user.email",
        "j7@example.com",
    )

    _j7_git(
        main,
        "config",
        "user.name",
        "J7",
    )

    _j7_git(
        main,
        "config",
        "commit.gpgsign",
        "false",
    )

    _j7_git(
        main,
        "add",
        target_rel,
        source_rel,
    )

    _j7_git(
        main,
        "commit",
        "-q",
        "-m",
        "seed j7 real e2e",
    )

    base_sha = _j7_git(
        main,
        "rev-parse",
        "HEAD",
    )

    branch = "j7-real-e2e"

    _j7_git(
        main,
        "worktree",
        "add",
        "-q",
        "-b",
        branch,
        str(exec_wt),
        base_sha,
    )

    stores = {}

    for name in (
        "relay",
        "ledger",
        "selector",
        "execution",
        "pec",
        "kxpre",
        "kxpost",
        "tcr",
        "sar",
        "sre",
        "rollback",
        "approval",
    ):
        path = tmp_path / name

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        stores[name] = path

    checks = [
        TC.build_check(
            "j7-diff-scope",
            TC.CHECK_TYPE_DIFF_SCOPE,
            expected_diff_paths=[
                target_rel
            ],
            required=True,
        ),
        TC.build_check(
            "j7-marker",
            TC.CHECK_TYPE_SUBPROCESS,
            argv=[
                sys.executable,
                "-c",
                (
                    "import pathlib,sys;"
                    "p=pathlib.Path("
                    + repr(target_rel)
                    + ");"
                    "c=p.read_text();"
                    "sys.exit("
                    "0 if "
                    "'AFTER_GOVERNED_APPLY' in c "
                    "and 'state: BEFORE' not in c "
                    "else 1"
                    ")"
                ),
            ],
            expected_exit_code=0,
            required=True,
        ),
    ]

    contract = TC.build_test_contract(
        "j7-real-contract",
        "j7-real-candidate",
        "j7-real-batch",
        target_rel,
        checks,
    )

    proposal = (
        J3.prepare_cognitive_governed_handoff(
            mission_id=(
                "mission-j7-real-e2e"
            ),
            provider_id=(
                "jarvis-openjarvis"
            ),
            capability=(
                J5.CAPABILITY_ID
            ),
            payload={
                "source_git_commit":
                    base_sha,
                "source_historical_path":
                    source_rel,
                "target_path":
                    target_rel,
                "test_contract":
                    contract,
                "objective":
                    (
                        "real governed "
                        "Relay J7 mutation"
                    ),
            },
            domain=(
                "JARVIS_OPENJARVIS"
            ),
            action_id=(
                "action-j7-real-e2e"
            ),
            intent=(
                "apply exact governed "
                "source through Relay"
            ),
            action_type=(
                J5.ACTION_TYPE
            ),
            irreversible=False,
        )
    )

    prepare_request = {
        "proposal":
            proposal,
        "execution_worktree_path":
            str(exec_wt),
        "main_worktree_path":
            str(main),
        "branch_name":
            branch,
        "base_sha":
            base_sha,
        "ledger_dir":
            str(
                stores["ledger"]
            ),
        "selector_dir":
            str(
                stores["selector"]
            ),
        "execution_dir":
            str(
                stores["execution"]
            ),
        "pre_execution_context_dir":
            str(
                stores["pec"]
            ),
        "repository_identity":
            str(
                exec_wt.resolve()
            ),
    }

    execute_request = {
        "kx108_pre_decision_dir":
            str(
                stores["kxpre"]
            ),
        "kx108_post_decision_dir":
            str(
                stores["kxpost"]
            ),
        "test_contract_results_dir":
            str(
                stores["tcr"]
            ),
        "sealed_receipt_dir":
            str(
                stores["sar"]
            ),
        "sealed_rollback_evidence_dir":
            str(
                stores["sre"]
            ),
        "rollback_result_dir":
            str(
                stores["rollback"]
            ),
    }

    return {
        "main":
            main,
        "exec_wt":
            exec_wt,
        "base_sha":
            base_sha,
        "branch":
            branch,
        "target_rel":
            target_rel,
        "source_rel":
            source_rel,
        "target_a":
            target_a,
        "source_b":
            source_b,
        "target_abs":
            exec_wt / target_rel,
        "stores":
            stores,
        "proposal":
            proposal,
        "prepare_request":
            prepare_request,
        "execute_request":
            execute_request,
    }


def test_j7_e2e_real_relay_to_j5_keep(
    tmp_path,
):
    import obsidia_sealed_evidence_v0 as SEV

    world = _j7_real_world(
        tmp_path
    )

    before_head = _j7_git(
        world["exec_wt"],
        "rev-parse",
        "HEAD",
    )

    assert (
        before_head
        == world["base_sha"]
    )

    assert (
        world["target_abs"].read_bytes()
        == world["target_a"]
    )

    # -------------------------------------------------------------
    # J6 PREPARE through the REAL Relay/J5 seam.
    # -------------------------------------------------------------

    prepared = R.relay_submit_mission(
        requested_outcome=(
            "prepare real governed "
            "J7 update"
        ),
        mission_kind=(
            R.KIND_GOVERNED_UPDATE
        ),
        target=(
            world["target_rel"]
        ),
        store_dir=(
            world["stores"]["relay"]
        ),
        governed_update_request=(
            world["prepare_request"]
        ),
    )

    assert (
        prepared["mission_state"]
        == R.MISSION_HOLD
    )

    assert (
        prepared["hold_reason"]
        == "HUMAN_EAH_AUTHORIZATION_REQUIRED"
    )

    assert (
        prepared["governed_prepare_only"]
        is True
    )

    assert (
        prepared["governed_auto_execute"]
        is False
    )

    assert (
        prepared["target_mutated"]
        is False
    )

    assert (
        prepared["kx108_invocations"]
        == 0
    )

    assert (
        prepared["human_approval_created"]
        is False
    )

    eah = (
        prepared[
            "execution_authority_hash"
        ]
    )

    assert (
        isinstance(eah, str)
        and len(eah) == 64
    )

    # PREPARE really did not touch target.
    assert (
        world["target_abs"].read_bytes()
        == world["target_a"]
    )

    # -------------------------------------------------------------
    # Explicit human authorization of THAT EXACT EAH.
    # -------------------------------------------------------------

    executed = R.relay_respond_to_hold(
        relay_mission_id=(
            prepared[
                "relay_mission_id"
            ]
        ),
        human_decision_ref=(
            "human-j7-real-eah"
        ),
        resolution=(
            "operator explicitly "
            "authorizes the exact EAH"
        ),
        store_dir=(
            world["stores"]["relay"]
        ),
        human_authorized_execution_authority_hash=(
            eah
        ),
        governed_execute_request=(
            world["execute_request"]
        ),
    )

    assert (
        executed["mission_state"]
        == R.MISSION_COMPLETE
    ), executed

    assert (
        executed[
            "governed_execution_status"
        ]
        == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    ), executed

    assert (
        executed["kx108_pre_gate"]
        == "ALLOW"
    ), executed

    assert (
        executed["kx108_post_gate"]
        == "ALLOW"
    ), executed

    assert (
        executed[
            "human_authorization_consumed"
        ]
        is True
    )

    assert (
        executed["jarvis_authority"]
        == "NONE"
    )

    assert (
        executed["decision_authority"]
        == "KX108_ONLY"
    )

    # Real governed A -> B.
    assert (
        world["target_abs"].read_bytes()
        == world["source_b"]
    )

    # Same mission contains the REAL J5/driver result.
    mission = R._load(
        world["stores"]["relay"],
        prepared["relay_mission_id"],
    )

    result = mission[
        "governed_execution_result"
    ]

    assert (
        result["status"]
        == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    )

    assert (
        result["kx108_pre_gate"]
        == "ALLOW"
    )

    assert (
        result["kx108_post_gate"]
        == "ALLOW"
    )

    assert (
        result[
            "driver_git_disposition"
        ]
        is False
    )

    # Sealed evidence is real and verifiable.
    rollback_evidence = (
        SEV.load_sealed_rollback_evidence(
            result[
                "sealed_rollback_evidence_id"
            ],
            world["stores"]["sre"],
        )
    )

    apply_receipt = (
        SEV.load_sealed_apply_receipt(
            result[
                "sealed_apply_receipt_id"
            ],
            world["stores"]["sar"],
        )
    )

    assert (
        SEV.verify_sealed_rollback_evidence(
            rollback_evidence
        )[0]
    )

    assert (
        SEV.verify_sealed_apply_receipt(
            apply_receipt
        )[0]
    )

    # No Git disposition.
    assert (
        _j7_git(
            world["exec_wt"],
            "rev-parse",
            "HEAD",
        )
        == world["base_sha"]
    )

    assert (
        _j7_git(
            world["exec_wt"],
            "diff",
            "--name-only",
        )
        == world["target_rel"]
    )


def test_j7_e2e_wrong_eah_stops_before_real_execution(
    tmp_path,
):
    world = _j7_real_world(
        tmp_path
    )

    prepared = R.relay_submit_mission(
        requested_outcome=(
            "prepare real governed "
            "J7 mismatch test"
        ),
        mission_kind=(
            R.KIND_GOVERNED_UPDATE
        ),
        target=(
            world["target_rel"]
        ),
        store_dir=(
            world["stores"]["relay"]
        ),
        governed_update_request=(
            world["prepare_request"]
        ),
    )

    assert (
        prepared["mission_state"]
        == R.MISSION_HOLD
    )

    real_eah = (
        prepared[
            "execution_authority_hash"
        ]
    )

    wrong_eah = (
        ("0" if real_eah[0] != "0" else "1")
        + real_eah[1:]
    )

    assert wrong_eah != real_eah

    out = R.relay_respond_to_hold(
        relay_mission_id=(
            prepared[
                "relay_mission_id"
            ]
        ),
        human_decision_ref=(
            "human-j7-wrong-eah"
        ),
        resolution="approved",
        store_dir=(
            world["stores"]["relay"]
        ),
        human_authorized_execution_authority_hash=(
            wrong_eah
        ),
        governed_execute_request=(
            world["execute_request"]
        ),
    )

    assert (
        out["status"]
        == "RELAY_REJECTED"
    )

    assert (
        out["reason"]
        == "HUMAN_AUTHORIZED_EAH_MISMATCH"
    )

    assert (
        out["mission_state"]
        == R.MISSION_HOLD
    )

    # No real mutation.
    assert (
        world["target_abs"].read_bytes()
        == world["target_a"]
    )

    # No KX PRE/POST decision should exist.
    assert not any(
        world["stores"]["kxpre"].rglob(
            "*.json"
        )
    )

    assert not any(
        world["stores"]["kxpost"].rglob(
            "*.json"
        )
    )

    # HEAD and worktree remain pristine.
    assert (
        _j7_git(
            world["exec_wt"],
            "rev-parse",
            "HEAD",
        )
        == world["base_sha"]
    )

    assert (
        _j7_git(
            world["exec_wt"],
            "diff",
            "--name-only",
        )
        == ""
    )
