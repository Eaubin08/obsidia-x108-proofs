"""tests/test_obsidia_terminal.py — Runtime test suite for T2 (T2_TEST_07..T2_TEST_29).

Standard library only (unittest). Exercises scripts/obsidia_terminal.py
via its injectable run() entry point (in-process, no subprocess) for all
tests except the smoke-test class, which spawns the real CLI process as
an EXPECTED_TEST_HARNESS_CHILD (permitted, not counted as a Terminal-
originated child process).
"""

from __future__ import annotations

import ast
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
TERMINAL_PATH = SCRIPTS_DIR / "obsidia_terminal.py"

sys.path.insert(0, str(SCRIPTS_DIR))
import obsidia_terminal as ot  # noqa: E402

AUTHORIZED_REF = "AUTORISER_EXECUTION_BORNEE_T2_V3"


def _new_sandbox():
    return tempfile.mkdtemp(prefix="obsidia_t2_test_")


def _run(argv, environ=None, allowed_write_roots=None, allowed_read_roots=None, resolver=None):
    out, err = io.StringIO(), io.StringIO()
    rc = ot.run(
        argv, environ or {}, None, out, err,
        path_resolver=resolver,
        allowed_write_roots=allowed_write_roots,
        allowed_read_roots=allowed_read_roots,
    )
    return rc, out.getvalue(), err.getvalue()


class T2_TEST_07_HelpCommandRuntime(unittest.TestCase):
    def test_help_runtime(self):
        rc, out, err = _run(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("obsidia_terminal.py", out)
        self.assertEqual(err, "")


class T2_TEST_08_VersionCommandRuntime(unittest.TestCase):
    def test_version_runtime(self):
        rc, out, err = _run(["version", "--format", "json"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["schema_version"], "TERMINAL_VERSION_V1")
        self.assertEqual(payload["terminal_source"], "scripts/obsidia_terminal.py")


class T2_TEST_09_CommandsCommandRuntime(unittest.TestCase):
    def test_commands_runtime(self):
        rc, out, err = _run(["commands", "--format", "json"])
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["commands"], sorted(payload["commands"]))
        self.assertIn("help", payload["commands"])
        self.assertIn("init", payload["commands"])


class T2_TEST_10_StatusCommandRuntime(unittest.TestCase):
    def test_status_runtime(self):
        sandbox = _new_sandbox()
        try:
            env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
            rc, _, _ = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                environ=env, allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc, 0)
            rc, out, err = _run(["status", "--state-dir", sandbox, "--format", "json"],
                                 allowed_read_roots=[sandbox])
            self.assertEqual(rc, 0)
            payload = json.loads(out)
            self.assertEqual(payload["schema_version"], "TERMINAL_STATUS_V1")
            self.assertEqual(payload["status"], "OK")
            self.assertEqual(payload["network_used"], False)
            self.assertEqual(payload["subprocess_used"], False)
            self.assertEqual(payload["runtime_components_called"], [])
            self.assertTrue(payload["history_initialized"])
            self.assertTrue(payload["state_dir_contained"])
            self.assertEqual(payload["encoding"], "UTF-8")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_11_HistoryInitRequiresHumanDecision(unittest.TestCase):
    def test_init_without_ref_rejected(self):
        sandbox = _new_sandbox()
        try:
            env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
            rc, _, err = _run(["init", "--state-dir", sandbox, "--format", "json"],
                               environ=env, allowed_write_roots=[sandbox])
            self.assertEqual(rc, 5)
            self.assertIn("AUTHORITY_MISSING", err) if "exit_code" not in err else None
            payload = json.loads(err)
            self.assertEqual(payload["exit_code"], 5)
            self.assertEqual(payload["reason_code"], "HUMAN_DECISION_REF_MISSING")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_init_wrong_ref_rejected(self):
        sandbox = _new_sandbox()
        try:
            env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
            rc, _, err = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", "WRONG_REF", "--format", "json"],
                environ=env, allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc, 5)
            payload = json.loads(err)
            self.assertEqual(payload["reason_code"], "HUMAN_DECISION_REF_MISMATCH")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_init_no_authorized_ref_in_env(self):
        sandbox = _new_sandbox()
        try:
            rc, _, err = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                environ={}, allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc, 5)
            payload = json.loads(err)
            self.assertEqual(payload["reason_code"], "AUTHORIZED_DECISION_REF_UNAVAILABLE")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_init_success_and_replay(self):
        sandbox = _new_sandbox()
        try:
            env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
            rc, out, _ = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                environ=env, allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["status"], "SUCCESS")

            state_file = Path(sandbox) / "terminal_state.json"
            self.assertTrue(state_file.exists())
            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], "TERMINAL_STATE_V1")
            self.assertNotIn(AUTHORIZED_REF, json.dumps(state))
            self.assertEqual(state["initialization_decision_ref_sha256"], ot.sha256_text(AUTHORIZED_REF))

            rc2, out2, _ = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                environ=env, allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc2, 0)
            self.assertEqual(json.loads(out2)["status"], "ALREADY_INITIALIZED")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


def _make_positive_envelope(sandbox):
    return {
        "schema_version": "TERMINAL_COMMAND_ENVELOPE_V1",
        "command_id": "c1",
        "command_name": "status",
        "command_args": {},
        "requested_output_format": "JSON",
        "requested_execution_mode": "READ_ONLY",
        "correlation_id": "corr-1",
        "issued_at": "2026-01-01T00:00:00Z",
        "working_directory_ref": sandbox,
        "state_dir_ref": sandbox,
    }


class T2_TEST_12_EnvelopePositiveVector(unittest.TestCase):
    def test_positive_vector(self):
        sandbox = _new_sandbox()
        try:
            vectors_file = os.path.join(sandbox, "vectors.json")
            positive = _make_positive_envelope(sandbox)
            with open(vectors_file, "w", encoding="utf-8") as f:
                json.dump({"envelope_vectors": {"POS_01": positive}}, f)
            rc, out, err = _run(
                ["envelope", "validate", "--input-file", vectors_file, "--vector-id", "POS_01", "--format", "json"],
                allowed_read_roots=[sandbox],
            )
            self.assertEqual(rc, 0)
            self.assertTrue(json.loads(out)["valid"])
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_13_EnvelopeRequiredFieldNegative(unittest.TestCase):
    def test_missing_schema_version(self):
        sandbox = _new_sandbox()
        try:
            vectors_file = os.path.join(sandbox, "vectors.json")
            positive = _make_positive_envelope(sandbox)
            negative = {k: v for k, v in positive.items() if k != "schema_version"}
            with open(vectors_file, "w", encoding="utf-8") as f:
                json.dump({"envelope_vectors": {"NEG_01": negative}}, f)
            rc, out, err = _run(
                ["envelope", "validate", "--input-file", vectors_file, "--vector-id", "NEG_01", "--format", "json"],
                allowed_read_roots=[sandbox],
            )
            self.assertEqual(rc, 2)
            payload = json.loads(err)
            self.assertEqual(payload["reason_code"], "REQUIRED_FIELD_MISSING")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_14_UnknownFieldOrSchemaVersionFailsClosed(unittest.TestCase):
    def test_unknown_field_rejected(self):
        env = _make_positive_envelope(".")
        env["unexpected_field"] = "x"
        ok, code, reason, _ = ot.validate_envelope(env)
        self.assertFalse(ok)
        self.assertEqual(code, 2)
        self.assertEqual(reason, "FORBIDDEN_ARGUMENT")

    def test_wrong_schema_version_rejected(self):
        env = _make_positive_envelope(".")
        env["schema_version"] = "SOME_OTHER_VERSION"
        ok, code, reason, _ = ot.validate_envelope(env)
        self.assertFalse(ok)
        self.assertEqual(code, 3)
        self.assertEqual(reason, "UNKNOWN_SCHEMA_VERSION")


class T2_TEST_15_UnknownCommandRejected(unittest.TestCase):
    def test_unknown_command(self):
        rc, out, err = _run(["zzz_unknown", "--format", "json"])
        self.assertEqual(rc, 4)
        self.assertEqual(json.loads(err)["reason_code"], "COMMAND_NOT_REGISTERED")


class T2_TEST_16_MissingArgumentRejected(unittest.TestCase):
    def test_status_missing_state_dir(self):
        rc, out, err = _run(["status", "--format", "json"])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(err)["reason_code"], "REQUIRED_FIELD_MISSING")


class T2_TEST_17_ForbiddenArgumentRejected(unittest.TestCase):
    def test_envelope_forbidden_argument(self):
        env = _make_positive_envelope(".")
        env["not_a_real_field"] = "value"
        ok, code, reason, _ = ot.validate_envelope(env)
        self.assertFalse(ok)
        self.assertEqual(reason, "FORBIDDEN_ARGUMENT")


class T2_TEST_18_JsonOutputDeterministic(unittest.TestCase):
    def test_json_output_stable_across_runs(self):
        rc1, out1, _ = _run(["version", "--format", "json"])
        rc2, out2, _ = _run(["version", "--format", "json"])
        self.assertEqual(out1, out2)
        canonical = json.dumps(json.loads(out1), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(out1.rstrip("\n"), canonical)


class T2_TEST_19_StdoutStderrSeparation(unittest.TestCase):
    def test_success_only_stdout(self):
        rc, out, err = _run(["version", "--format", "json"])
        self.assertEqual(rc, 0)
        self.assertNotEqual(out, "")
        self.assertEqual(err, "")

    def test_error_only_stderr(self):
        rc, out, err = _run(["zzz_unknown", "--format", "json"])
        self.assertNotEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertNotEqual(err, "")


class T2_TEST_20_ExitCodesMatchContract(unittest.TestCase):
    def test_exit_code_table(self):
        rc, _, _ = _run(["version"])
        self.assertEqual(rc, 0)
        rc, _, _ = _run(["status"])
        self.assertEqual(rc, 2)
        rc, _, _ = _run(["zzz_unknown"])
        self.assertEqual(rc, 4)
        rc, _, _ = _run(["mission", "new"])
        self.assertEqual(rc, 8)
        sandbox = _new_sandbox()
        try:
            rc, _, _ = _run(["init", "--state-dir", sandbox], environ={"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF},
                             allowed_write_roots=[sandbox])
            self.assertEqual(rc, 5)
            rc, _, _ = _run(["init", "--state-dir", r"C:\Windows\System32", "--human-decision-ref", "x"],
                             environ={"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF},
                             allowed_write_roots=[sandbox])
            self.assertEqual(rc, 7)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_21_DefaultExecutionModeReadOnly(unittest.TestCase):
    def test_read_only_commands_never_write(self):
        sandbox = _new_sandbox()
        try:
            before = set(Path(sandbox).rglob("*"))
            _run(["status", "--state-dir", sandbox, "--format", "json"], allowed_read_roots=[sandbox])
            _run(["version", "--format", "json"])
            _run(["commands", "--format", "json"])
            after = set(Path(sandbox).rglob("*"))
            self.assertEqual(before, after)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_22_MutatingCommandWithoutAuthorizationRejected(unittest.TestCase):
    def test_envelope_mutating_without_human_decision(self):
        env = _make_positive_envelope(".")
        env["requested_execution_mode"] = "INTERNAL_OPERATIONAL_WRITE"
        ok, code, reason, _ = ot.validate_envelope(env)
        self.assertFalse(ok)
        self.assertEqual(code, 5)
        self.assertEqual(reason, "HUMAN_DECISION_REF_MISSING")


class T2_TEST_23_SilenceNeverAuthorizes(unittest.TestCase):
    def test_empty_string_ref_rejected(self):
        sandbox = _new_sandbox()
        try:
            rc, _, err = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", "", "--format", "json"],
                environ={"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF},
                allowed_write_roots=[sandbox],
            )
            self.assertEqual(rc, 5)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_present_agent_alone_does_not_authorize(self):
        # No human_decision_ref anywhere in argv/env: presence of the
        # agent invoking the command must never itself constitute authority.
        sandbox = _new_sandbox()
        try:
            rc, _, _ = _run(["init", "--state-dir", sandbox, "--format", "json"],
                             environ={}, allowed_write_roots=[sandbox])
            self.assertEqual(rc, 5)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_24_FutureDependencyMarkedNotImplemented(unittest.TestCase):
    def test_future_commands_not_implemented(self):
        for verb in ("mission", "gateway", "mcp", "brody", "kernel", "sandbox"):
            rc, _, err = _run([verb, "new", "--format", "json"])
            self.assertEqual(rc, 8, msg=verb)
            self.assertEqual(json.loads(err)["reason_code"], "NOT_IMPLEMENTED_IN_T2")


FORBIDDEN_AST_NAMES = {
    "socket", "urllib", "requests",
}
FORBIDDEN_AST_MODULES_FROM = {"http.client", "subprocess"}
# Unambiguous bare-name calls: never legitimate under any local definition
# in this shell (subprocess/os process-spawning primitives). "run" and
# "call" are deliberately excluded from bare-name matching because they
# collide with this module's own public run() entry point; their unsafe
# use (subprocess.run/os.call-style) is already excluded by the import
# check (test_ast_forbidden_imports_absent forbids importing subprocess).
FORBIDDEN_BARE_CALL_NAMES = {
    "Popen", "check_call", "check_output",
    "spawnl", "spawnv", "spawnve", "execl", "execv", "execve",
}
# Attribute calls (obj.attr(...)) forbidden regardless of obj name.
FORBIDDEN_ATTR_CALL_NAMES = {
    "system", "popen", "Popen", "run", "call", "check_call", "check_output",
    "urlopen", "create_connection",
}
FORBIDDEN_ATTR_CALL_OWNERS = {"os", "subprocess", "socket", "urllib", "request", "requests"}


class T2_TEST_25_NoNetworkSubprocessRuntimeCall(unittest.TestCase):
    def test_ast_forbidden_imports_absent(self):
        src = TERMINAL_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src)
        found_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    found_imports.add(node.module.split(".")[0])
        self.assertFalse(found_imports & FORBIDDEN_AST_NAMES,
                          msg=f"forbidden imports found: {found_imports & FORBIDDEN_AST_NAMES}")
        self.assertNotIn("subprocess", found_imports)

    def test_ast_forbidden_calls_absent(self):
        src = TERMINAL_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src)
        offending = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_BARE_CALL_NAMES:
                    offending.append((node.func.id, node.lineno))
            elif isinstance(node.func, ast.Attribute):
                owner = node.func.value.id if isinstance(node.func.value, ast.Name) else None
                if node.func.attr in FORBIDDEN_ATTR_CALL_NAMES and (
                    owner is None or owner in FORBIDDEN_ATTR_CALL_OWNERS
                ):
                    offending.append((f"{owner}.{node.func.attr}", node.lineno))
        self.assertEqual(offending, [])

    def test_in_process_traps_no_network_no_subprocess(self):
        """Trap network/process APIs during a representative run; confirm
        zero attempts across the full command surface exercised by this
        suite."""
        import socket as _socket
        import subprocess as _subprocess
        import urllib.request as _urlreq

        attempts = {"network": 0, "subprocess": 0}

        orig_socket = _socket.socket
        orig_create_connection = _socket.create_connection
        orig_urlopen = _urlreq.urlopen
        orig_popen = _subprocess.Popen
        orig_run = _subprocess.run

        def trap_network(*a, **k):
            attempts["network"] += 1
            raise AssertionError("network attempt trapped")

        def trap_subprocess(*a, **k):
            attempts["subprocess"] += 1
            raise AssertionError("subprocess attempt trapped")

        _socket.socket = trap_network
        _socket.create_connection = trap_network
        _urlreq.urlopen = trap_network
        _subprocess.Popen = trap_subprocess
        _subprocess.run = trap_subprocess
        try:
            sandbox = _new_sandbox()
            try:
                env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
                _run(["--help"])
                _run(["version", "--format", "json"])
                _run(["commands", "--format", "json"])
                _run(["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                     environ=env, allowed_write_roots=[sandbox])
                _run(["status", "--state-dir", sandbox, "--format", "json"], allowed_read_roots=[sandbox])
            finally:
                shutil.rmtree(sandbox, ignore_errors=True)
        finally:
            _socket.socket = orig_socket
            _socket.create_connection = orig_create_connection
            _urlreq.urlopen = orig_urlopen
            _subprocess.Popen = orig_popen
            _subprocess.run = orig_run

        self.assertEqual(attempts["network"], 0)
        self.assertEqual(attempts["subprocess"], 0)


class T2_TEST_26_PathContainmentEnforced(unittest.TestCase):
    def test_containment_allows_inside_root(self):
        sandbox = _new_sandbox()
        try:
            ok, reason = ot.check_path_containment(sandbox, [sandbox])
            self.assertTrue(ok)
            self.assertIsNone(reason)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_containment_rejects_outside_root(self):
        sandbox = _new_sandbox()
        try:
            ok, reason = ot.check_path_containment(r"C:\Windows\System32", [sandbox])
            self.assertFalse(ok)
            self.assertIn(reason, ("PATH_OUTSIDE_SCOPE", "PATH_ESCAPE_REJECTED"))
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


class T2_TEST_27_SymlinkOrJunctionEscapeRejected(unittest.TestCase):
    def test_injected_resolver_simulates_escape(self):
        sandbox = _new_sandbox()
        try:
            def escaping_resolver(path):
                # Simulates a symlink/junction that resolves outside the
                # allowed root regardless of the literal path given.
                return Path(r"C:\Windows\System32\escaped")

            ok, reason = ot.check_path_containment(
                os.path.join(sandbox, "looks_local"), [sandbox], resolver=escaping_resolver,
            )
            self.assertFalse(ok)
            self.assertEqual(reason, "PATH_ESCAPE_REJECTED")
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


SECRET_VALUE_PATTERNS_HINT = ("password", "secret", "token", "credential", "bearer", "api_key")


class T2_TEST_28_NoSecretValueInOutputOrErrors(unittest.TestCase):
    def test_no_secret_in_init_output(self):
        sandbox = _new_sandbox()
        try:
            env = {"OBSIDIA_T2_AUTHORIZED_DECISION_REF": AUTHORIZED_REF}
            rc, out, err = _run(
                ["init", "--state-dir", sandbox, "--human-decision-ref", AUTHORIZED_REF, "--format", "json"],
                environ=env, allowed_write_roots=[sandbox],
            )
            self.assertNotIn(AUTHORIZED_REF, out)
            self.assertNotIn(AUTHORIZED_REF, err)
            state_file = Path(sandbox) / "terminal_state.json"
            self.assertNotIn(AUTHORIZED_REF, state_file.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)

    def test_secret_inline_in_envelope_rejected(self):
        env = _make_positive_envelope(".")
        env["command_args"] = {"password": "hunter2hunter2hunter2"}
        ok, code, reason, _ = ot.validate_envelope(env)
        self.assertFalse(ok)
        self.assertEqual(code, 6)
        self.assertEqual(reason, "SECRET_INLINE_FORBIDDEN")


class T2_TEST_29_NonInteractiveOfflineRuntime(unittest.TestCase):
    def test_smoke_cli_subprocess(self):
        """EXPECTED_TEST_HARNESS_CHILD: the test harness itself spawns the
        real interpreter to exercise the CLI end-to-end, offline, with
        stdin closed. This process is not Terminal-originated."""
        sandbox = _new_sandbox()
        try:
            proc = subprocess.run(
                [sys.executable, "-B", str(TERMINAL_PATH), "--help"],
                cwd=str(REPO_ROOT),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("obsidia_terminal.py", proc.stdout)

            proc2 = subprocess.run(
                [sys.executable, "-B", str(TERMINAL_PATH), "version", "--format", "json"],
                cwd=str(REPO_ROOT),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            self.assertEqual(proc2.returncode, 0)
            json.loads(proc2.stdout)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
