"""test_obsidia_session_inspect_cli — Tests TERMINAL_SESSION_INSPECT_V0.

Couvre :
  T01-T10  : parser Python (invocations invalides)
  T11-T20  : résultats adapter
  T21-T29  : stdout / stderr
  T30-T34  : sérialisation lock_record
  T35-T38  : effets de bord (mutations fichier, receipts)
  T39-T46  : AST (imports et appels interdits)
  T47-T55  : intégration PowerShell
  + intégrité blob des fichiers protégés
"""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType

import pytest

# ---------------------------------------------------------------------------
# Chemins canoniques
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CLI = _REPO_ROOT / "scripts" / "obsidia_session_inspect_cli.py"
_PS = _REPO_ROOT / "scripts" / "obsidia.ps1"
_PYTHON = sys.executable

# ---------------------------------------------------------------------------
# Helpers subprocess
# ---------------------------------------------------------------------------

def _run(args: list, *, timeout: int = 30):
    r = subprocess.run(
        [_PYTHON, str(_CLI)] + list(args),
        capture_output=True, text=True, encoding="utf-8", timeout=timeout,
    )
    return r.stdout, r.stderr, r.returncode


def _make_valid_lock(path: Path) -> dict:
    record = {
        "session_id": "sess-test-001",
        "lock_version": "V2",
        "created_at": 1700000000.0,
        "heartbeat_at": 1700000001.0,
    }
    path.write_bytes(json.dumps(record).encode("utf-8"))
    return record


def _make_schema_invalid_lock(path: Path) -> None:
    data = {"session_id": "x", "lock_version": "V1", "created_at": 1000.0}
    path.write_bytes(json.dumps(data).encode("utf-8"))


def _make_json_invalid_lock(path: Path) -> None:
    path.write_bytes(b"not-valid-json{{{")


def _load_cli():
    """Charge le module CLI dans un espace de noms propre."""
    spec = importlib.util.spec_from_file_location("_cli_under_test", str(_CLI))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
# T01-T10 : parser Python — invocations invalides
# ============================================================

def test_t01_no_args_exit_2():
    _, stderr, code = _run([])
    assert code == 2
    assert stderr == ""


def test_t02_lock_path_absent_exit_2():
    _, stderr, code = _run(["--unknown"])
    assert code == 2
    assert stderr == ""


def test_t03_missing_value_exit_2():
    _, stderr, code = _run(["--lock-path"])
    assert code == 2
    assert stderr == ""


def test_t04_empty_value_exit_2():
    _, stderr, code = _run(["--lock-path", ""])
    assert code == 2
    assert stderr == ""


def test_t05_unknown_option_exit_2():
    _, stderr, code = _run(["--auto"])
    assert code == 2
    assert stderr == ""


def test_t06_duplicate_lock_path_exit_2(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    _, stderr, code = _run(["--lock-path", str(lock), "--lock-path", str(lock)])
    assert code == 2
    assert stderr == ""


def test_t07_positional_arg_exit_2(tmp_path):
    lock = tmp_path / "lock.json"
    _, stderr, code = _run([str(lock)])
    assert code == 2
    assert stderr == ""


def test_t08_extra_positional_after_value_exit_2(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    _, stderr, code = _run(["--lock-path", str(lock), "extra"])
    assert code == 2
    assert stderr == ""


def test_t09_equals_form_rejected():
    _, stderr, code = _run(["--lock-path=/tmp/x.json"])
    assert code == 2
    assert stderr == ""


def test_t10_adapter_not_called_on_invalid_invocation(monkeypatch):
    cli = _load_cli()
    calls: list = []
    orig = cli.TerminalSessionAdapter

    class Spy:
        def inspect_lock(self, *a, **kw):
            calls.append(1)
            return orig().inspect_lock(*a, **kw)

    monkeypatch.setattr(cli, "TerminalSessionAdapter", Spy)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        code = cli.main([])
    finally:
        sys.stdout = old
    assert code == 2
    assert calls == []


# ============================================================
# T11-T20 : résultats adapter
# ============================================================

def test_t11_absent_path_exit_3(tmp_path):
    missing = tmp_path / "nonexistent.json"
    stdout, stderr, code = _run(["--lock-path", str(missing)])
    assert code == 3
    assert stderr == ""
    data = json.loads(stdout)
    assert data["ok"] is False


def test_t12_not_file_exit_3(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    stdout, stderr, code = _run(["--lock-path", str(d)])
    assert code == 3
    assert stderr == ""
    data = json.loads(stdout)
    assert data["ok"] is False


def test_t13_invalid_json_exit_3(tmp_path):
    lock = tmp_path / "bad.json"
    _make_json_invalid_lock(lock)
    stdout, stderr, code = _run(["--lock-path", str(lock)])
    assert code == 3
    assert stderr == ""
    data = json.loads(stdout)
    assert data["ok"] is False


def test_t14_invalid_schema_exit_3(tmp_path):
    lock = tmp_path / "schema.json"
    _make_schema_invalid_lock(lock)
    stdout, stderr, code = _run(["--lock-path", str(lock)])
    assert code == 3
    assert stderr == ""
    data = json.loads(stdout)
    assert data["ok"] is False


def test_t15_valid_lock_exit_0(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, stderr, code = _run(["--lock-path", str(lock)])
    assert code == 0
    assert stderr == ""
    data = json.loads(stdout)
    assert data["ok"] is True


def test_t16_session_id_mapped(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert data["session_id"] == "sess-test-001"


def test_t17_adapter_code_mapped(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert data["adapter_code"] == "OK"


def test_t18_authority_constants(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run(["--lock-path", str(lock)])
    data = json.loads(stdout)
    assert data["authority"] == "NONE"
    assert data["sovereign"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["kx108_decision_present"] is False
    assert data["simulated"] is False
    assert data["isolated"] is True
    assert data["mutation_scope"] == "NONE"
    assert data["operation"] == "INSPECT_LOCK"
    assert data["command"] == "obsidia session inspect"


def test_t19_wired_true_in_public_envelope(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run(["--lock-path", str(lock)])
    data = json.loads(stdout)
    assert data["wired"] is True


def test_t20_adapter_internal_result_not_mutated(tmp_path):
    """L'adapter interne retourne wired=False ; le résultat frozen ne peut être muté."""
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    sys.path.insert(0, str(_REPO_ROOT))
    from periphery.session_lock.terminal_session_adapter import TerminalSessionAdapter
    result = TerminalSessionAdapter().inspect_lock(str(lock))
    assert result.wired is False
    with pytest.raises((AttributeError, TypeError)):
        result.wired = True  # type: ignore[misc]  # frozen dataclass → FrozenInstanceError


# ============================================================
# T21-T29 : stdout / stderr
# ============================================================

def test_t21_stdout_single_json(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run(["--lock-path", str(lock)])
    data = json.loads(stdout.strip())
    assert isinstance(data, dict)


def test_t22_at_most_one_trailing_newline(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run(["--lock-path", str(lock)])
    stripped = stdout.rstrip("\n")
    assert "\n" not in stripped


def test_t23_stderr_empty_on_success(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    _, stderr, code = _run(["--lock-path", str(lock)])
    assert code == 0
    assert stderr == ""


def test_t24_stderr_empty_on_invalid():
    _, stderr, code = _run([])
    assert code == 2
    assert stderr == ""


def test_t25_stderr_empty_on_adapter_fail(tmp_path):
    _, stderr, code = _run(["--lock-path", str(tmp_path / "miss.json")])
    assert code == 3
    assert stderr == ""


def test_t26_no_ansi_sequences(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run(["--lock-path", str(lock)])
    assert "\x1b" not in stdout


def test_t27_no_traceback(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, stderr, _ = _run(["--lock-path", str(lock)])
    assert "Traceback" not in stdout
    assert "Traceback" not in stderr


def test_t28_internal_error_exit_1(tmp_path, monkeypatch):
    """Exception inattendue → exit 1, JSON avec adapter_code=INTERNAL_ERROR."""
    cli = _load_cli()

    def bad_adapter():
        raise RuntimeError("injected_failure")

    monkeypatch.setattr(cli, "TerminalSessionAdapter", bad_adapter)
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        code = cli.main(["--lock-path", str(lock)])
        captured = buf.getvalue()
    finally:
        sys.stdout = old
    assert code == 1
    data = json.loads(captured.strip())
    assert data["ok"] is False
    assert data["adapter_code"] == "INTERNAL_ERROR"


def test_t29_internal_error_message_not_exposed(tmp_path, monkeypatch):
    """Le message de l'exception interne ne doit pas apparaître dans la sortie."""
    cli = _load_cli()
    SECRET = "this_secret_must_not_appear_xyz987abc"

    def bad_adapter():
        raise RuntimeError(SECRET)

    monkeypatch.setattr(cli, "TerminalSessionAdapter", bad_adapter)
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    buf_out, buf_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf_out, buf_err
    try:
        cli.main(["--lock-path", str(lock)])
        out, err = buf_out.getvalue(), buf_err.getvalue()
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    assert SECRET not in out
    assert SECRET not in err


# ============================================================
# T30-T34 : sérialisation lock_record
# ============================================================

def test_t30_mapping_proxy_to_json_object(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert isinstance(data["lock_record"], dict)


def test_t31_nested_list_to_json_array(tmp_path):
    lock = tmp_path / "lock.json"
    record = {
        "session_id": "s1", "lock_version": "V2",
        "created_at": 1000.0, "heartbeat_at": 1000.0,
        "tags": [1, 2, 3],
    }
    lock.write_bytes(json.dumps(record).encode())
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert isinstance(data["lock_record"]["tags"], list)
    assert data["lock_record"]["tags"] == [1, 2, 3]


def test_t32_nested_dict_preserved(tmp_path):
    lock = tmp_path / "lock.json"
    record = {
        "session_id": "s1", "lock_version": "V2",
        "created_at": 1000.0, "heartbeat_at": 1000.0,
        "meta": {"k": "v"},
    }
    lock.write_bytes(json.dumps(record).encode())
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert data["lock_record"]["meta"] == {"k": "v"}


def test_t33_extra_fields_preserved(tmp_path):
    lock = tmp_path / "lock.json"
    record = {
        "session_id": "s1", "lock_version": "V2",
        "created_at": 1000.0, "heartbeat_at": 1000.0,
        "custom": "val", "deep": {"x": 42},
    }
    lock.write_bytes(json.dumps(record).encode())
    stdout, _, code = _run(["--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout)
    assert data["lock_record"]["custom"] == "val"
    assert data["lock_record"]["deep"]["x"] == 42


def test_t34_internal_source_not_mutated(tmp_path):
    """Le lock_record retourné par l'adapter (MappingProxyType) ne peut pas être muté."""
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    sys.path.insert(0, str(_REPO_ROOT))
    from periphery.session_lock.terminal_session_adapter import TerminalSessionAdapter
    result = TerminalSessionAdapter().inspect_lock(str(lock))
    assert isinstance(result.lock_record, MappingProxyType)
    with pytest.raises(TypeError):
        result.lock_record["injected"] = 99  # type: ignore[index]


# ============================================================
# T35-T38 : effets de bord
# ============================================================

def test_t35_lock_byte_identical_after_success(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    before = lock.read_bytes()
    _run(["--lock-path", str(lock)])
    assert lock.read_bytes() == before


def test_t36_lock_byte_identical_after_schema_error(tmp_path):
    lock = tmp_path / "bad.json"
    _make_schema_invalid_lock(lock)
    before = lock.read_bytes()
    _run(["--lock-path", str(lock)])
    assert lock.read_bytes() == before


def test_t37_no_extra_files_created(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    files_before = set(tmp_path.iterdir())
    _run(["--lock-path", str(lock)])
    assert set(tmp_path.iterdir()) == files_before


def test_t38_no_receipt_jsonl_written(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    local_dir = _REPO_ROOT / ".local_obsidia"
    before = set(local_dir.glob("**/*.jsonl")) if local_dir.exists() else set()
    _run(["--lock-path", str(lock)])
    after = set(local_dir.glob("**/*.jsonl")) if local_dir.exists() else set()
    assert after == before


# ============================================================
# T39-T46 : AST — imports et appels interdits dans le CLI
# ============================================================

_CLI_SRC = _CLI.read_text(encoding="utf-8")
_CLI_TREE = ast.parse(_CLI_SRC)

_FORBIDDEN_IMPORT_TOPS = frozenset({
    "subprocess", "threading", "asyncio", "multiprocessing",
    "socket", "requests", "httpx", "signal",
})

_FORBIDDEN_CALL_ATTRS = frozenset({
    "simulate_bounded_session", "HeartbeatLockManager", "SynchronousHeartbeatCaller",
    "bootstrap", "tick", "request_stop", "request_abort",
    "consume_and_terminate", "release", "run_bounded",
    "classify_lock", "prepare_reclaim_proposal", "execute_reclaim",
})

_FORBIDDEN_OS_ATTRS = frozenset({"getenv", "environ", "system", "popen"})
_FORBIDDEN_FILE_WRITE = frozenset({"write_text", "write_bytes", "unlink", "remove", "rmdir", "rename", "replace"})


def test_t39_no_forbidden_imports():
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _FORBIDDEN_IMPORT_TOPS:
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in _FORBIDDEN_IMPORT_TOPS:
                bad.append(node.module)
    assert bad == [], f"Imports interdits : {bad}"


def test_t40_no_forbidden_calls():
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_CALL_ATTRS:
                bad.append(func.attr)
            if isinstance(func, ast.Name) and func.id in _FORBIDDEN_CALL_ATTRS:
                bad.append(func.id)
    assert bad == [], f"Appels interdits : {bad}"


def test_t41_no_reclaim_calls():
    reclaim = {"classify_lock", "prepare_reclaim_proposal", "execute_reclaim"}
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Call):
            func = node.func
            attr = func.attr if isinstance(func, ast.Attribute) else None
            name = func.id if isinstance(func, ast.Name) else None
            if attr in reclaim or name in reclaim:
                bad.append(attr or name)
    assert bad == [], f"Reclaim interdit : {bad}"


def test_t42_no_git_access():
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "git" in alias.name.lower():
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if "git" in node.module.lower():
                bad.append(node.module)
    assert bad == [], f"Accès Git interdit : {bad}"


def test_t43_no_env_access():
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Attribute):
            if (isinstance(node.value, ast.Name) and node.value.id == "os"
                    and node.attr in _FORBIDDEN_OS_ATTRS):
                bad.append(f"os.{node.attr}")
    assert bad == [], f"Accès environnement interdit : {bad}"


def test_t44_no_network_imports():
    net = {"socket", "requests", "httpx", "urllib"}
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in net:
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in net:
                bad.append(node.module)
    assert bad == [], f"Réseau interdit : {bad}"


def test_t45_no_subprocess_thread_asyncio():
    forbidden = {"subprocess", "threading", "asyncio", "multiprocessing"}
    bad = []
    for node in ast.walk(_CLI_TREE):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden:
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in forbidden:
                bad.append(node.module)
    assert bad == [], f"Interdit : {bad}"


def test_t46_no_file_write_or_delete():
    bad = []
    for node in ast.walk(_CLI_TREE):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr not in _FORBIDDEN_FILE_WRITE:
            continue
        # sys.stdout.write est autorisé (sortie JSON)
        if isinstance(func.value, ast.Attribute) and func.value.attr == "stdout":
            continue
        bad.append(func.attr)
    assert bad == [], f"Écriture/suppression de fichier interdite : {bad}"


# ============================================================
# T47-T55 : intégration PowerShell
# ============================================================

def _ps_available() -> bool:
    try:
        r = subprocess.run(
            ["powershell", "-Command", "Write-Output OK"],
            capture_output=True, text=True, timeout=10,
        )
        return "OK" in r.stdout
    except Exception:
        return False


_PS_AVAILABLE = _ps_available()


def _run_ps(args: list, *, timeout: int = 30):
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS)] + list(args),
        capture_output=True, text=True, encoding="utf-8", timeout=timeout,
    )
    return r.stdout, r.stderr, r.returncode


def test_t47_ps_route_session_inspect_present():
    src = _PS.read_text(encoding="utf-8")
    assert "session" in src.lower()
    assert "inspect" in src.lower()
    assert "obsidia_session_inspect_cli.py" in src


def test_t48_ps_dedicated_script_referenced():
    src = _PS.read_text(encoding="utf-8")
    assert "obsidia_session_inspect_cli.py" in src


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t49_ps_args_transmitted_without_transformation(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, stderr, code = _run_ps(["session", "inspect", "--lock-path", str(lock)])
    assert code == 0, f"code={code} stderr={stderr!r}"
    data = json.loads(stdout.strip())
    assert data["ok"] is True
    assert data["lock_path"] == str(lock)


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t50_ps_exit_code_propagated_exit_3(tmp_path):
    missing = tmp_path / "nonexistent.json"
    _, _, code = _run_ps(["session", "inspect", "--lock-path", str(missing)])
    assert code == 3


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t51_ps_stdout_is_single_json(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, code = _run_ps(["session", "inspect", "--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout.strip())
    assert isinstance(data, dict)
    assert data["command"] == "obsidia session inspect"


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t52_ps_no_boot_on_session_inspect(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, _ = _run_ps(["session", "inspect", "--lock-path", str(lock)])
    assert "COCKPIT" not in stdout
    assert "BOOT" not in stdout
    assert "Neo4j" not in stdout
    assert "Ragnarok" not in stdout


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t53_ps_no_obsidia_cli_on_session_inspect(tmp_path):
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    stdout, _, code = _run_ps(["session", "inspect", "--lock-path", str(lock)])
    assert code == 0
    data = json.loads(stdout.strip())
    # obsidia_cli.py produirait un format complètement différent
    assert data["command"] == "obsidia session inspect"
    assert "adapter_code" in data


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t54_ps_session_simulate_not_exposed():
    """session simulate ne doit pas être une route reconnue dans le wrapper."""
    src = _PS.read_text(encoding="utf-8")
    # Vérifier qu'il n'y a pas de branche elseif/if routant vers simulate
    lines_with_simulate_route = [
        l for l in src.splitlines()
        if "simulate" in l.lower() and ("elseif" in l.lower() or ("if" in l.lower() and "eq" in l.lower()))
    ]
    assert lines_with_simulate_route == [], (
        f"Route simulate détectée dans obsidia.ps1 : {lines_with_simulate_route}"
    )


def test_t55_ps_existing_commands_still_present():
    src = _PS.read_text(encoding="utf-8")
    for cmd in ["start", "restart", "stop", "open", "--print-start-plan", "chat"]:
        assert cmd in src, f"Commande existante manquante : {cmd!r}"


# ============================================================
# Intégrité blob des fichiers protégés
# ============================================================

def _git_hash_object(path: Path) -> str:
    r = subprocess.run(
        ["git", "hash-object", str(path)],
        capture_output=True, text=True, cwd=str(_REPO_ROOT),
    )
    return r.stdout.strip()


def _git_ls_tree_blob(commit: str, rel_path: str) -> str | None:
    r = subprocess.run(
        ["git", "ls-tree", commit, rel_path],
        capture_output=True, text=True, cwd=str(_REPO_ROOT),
    )
    parts = r.stdout.strip().split()
    return parts[2] if len(parts) >= 3 else None


_ADAPTER_COMMIT = "0ef8c5131952317faa6b585ab07d16ffdfcb4cea"
_CALLER_COMMIT = "b2011885bd7f9b52ce486983034f5046f2e56ea6"
_MANAGER_COMMIT = "69b8985ab21eb678ab7ed507e67c5c41e3441eaa"

# Blobs connus (pre-calculés lors de la revalidation REV01)
_KNOWN_BLOBS: dict[str, str] = {
    "periphery/session_lock/heartbeat_lock_manager.py": "fbc441f77c707fbd3c272e5ec02f004c338bb49c",
    "periphery/session_lock/__init__.py": "043b748d75721d50fd39b0bf178c20a7247e8318",
    "periphery/tests/test_heartbeat_lock_manager.py": "09257c862af35a0d4e4f6f9273e6ac0911cf384c",
    "periphery/session_lock/heartbeat_caller.py": "593662000355af48f258cbe2086331ac84f87a73",
    "periphery/tests/test_heartbeat_caller.py": "fa5c91d780b21472773a10dcdc7443515df977d2",
    "periphery/session_lock/terminal_session_adapter.py": "7ee56c76600ca26830ce5799b19fe4442e8c281e",
    "periphery/tests/test_terminal_session_adapter.py": "cd2f47120af9d10eba52fbd05da67a932af5d0e2",
    "scripts/obsidia_cli.py": "bd2cbd9156885303abad3d70cebe3e251fcd7aa5",
    "scripts/obsidia_registry.yaml": "9bd824078065f39cb6dc3bb995a1defc2c5ffc5c",
}


@pytest.mark.parametrize("rel_path,expected_blob", list(_KNOWN_BLOBS.items()))
def test_protected_blob_integrity(rel_path: str, expected_blob: str):
    actual = _git_hash_object(_REPO_ROOT / rel_path)
    assert actual == expected_blob, (
        f"Fichier protégé modifié : {rel_path}\n"
        f"  attendu : {expected_blob}\n"
        f"  actuel  : {actual}"
    )


def test_ps_diff_limited_to_session_inspect():
    """Le diff de obsidia.ps1 depuis la base est strictement la route session inspect."""
    result = subprocess.run(
        ["git", "diff", _ADAPTER_COMMIT, "--", "scripts/obsidia.ps1"],
        capture_output=True, text=True, cwd=str(_REPO_ROOT),
    )
    diff = result.stdout
    if not diff:
        pytest.skip("Aucun diff détecté pour obsidia.ps1 — vérifier manuellement")
    added_lines = [
        l[1:].strip()
        for l in diff.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]
    allowed_keywords = {
        "session", "inspect", "obsidia_session_inspect_cli",
        "terminal_session_inspect_v0", "lock_mutation", "real_execution",
        "reclaim", "forbidden", "decision_authority", "wired", "kx108",
        "remaining", "psscriptroot", "exit", "lastexitcode", "if", "args",
        "count", "ceq", "#", "",
    }
    unexpected = [
        l for l in added_lines
        if l and not any(kw in l.lower() for kw in allowed_keywords)
    ]
    assert unexpected == [], f"Lignes ajoutées inattendues dans obsidia.ps1 : {unexpected}"


# ============================================================
# T56-T59 : _try_emit — canal stdout défaillant
# ============================================================

class _BrokenStdout:
    """Canal stdout simulant une défaillance dès la première écriture."""
    def write(self, s: str) -> None:
        raise BrokenPipeError("simulated broken pipe")

    def flush(self) -> None:
        raise BrokenPipeError("simulated broken pipe")


class _FlushFailStdout:
    """Canal stdout dont write réussit mais flush lève."""
    def __init__(self) -> None:
        self.written: list[str] = []

    def write(self, s: str) -> None:
        self.written.append(s)

    def flush(self) -> None:
        raise OSError("simulated flush failure")


def test_t56_broken_pipe_on_invalid_invocation_returns_1(monkeypatch):
    """Invocation invalide + stdout cassé → exit 1 sans exception échappée, stderr vide."""
    cli = _load_cli()
    buf_err = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", _BrokenStdout())
    monkeypatch.setattr(cli.sys, "stderr", buf_err)

    code = cli.main([])
    assert code == 1, f"attendu 1 (broken pipe), got {code}"
    assert buf_err.getvalue() == ""


def test_t57_broken_pipe_after_adapter_success_returns_1(tmp_path, monkeypatch):
    """Adapter ok + stdout cassé au moment de l'émission → exit 1, adapter appelé une fois."""
    cli = _load_cli()
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)

    call_count: list[int] = []
    orig = cli.TerminalSessionAdapter

    class _SpyAdapter:
        def inspect_lock(self, path: str):
            call_count.append(1)
            return orig().inspect_lock(path)

    buf_err = io.StringIO()
    monkeypatch.setattr(cli, "TerminalSessionAdapter", _SpyAdapter)
    monkeypatch.setattr(cli.sys, "stdout", _BrokenStdout())
    monkeypatch.setattr(cli.sys, "stderr", buf_err)

    code = cli.main(["--lock-path", str(lock)])
    assert code == 1, f"attendu 1 (broken pipe), got {code}"
    assert len(call_count) == 1, "adapter doit être appelé exactement une fois"
    assert buf_err.getvalue() == ""


def test_t58_os_error_during_internal_error_emit_returns_1(tmp_path, monkeypatch):
    """Exception adapter + stdout cassé pour l'émission INTERNAL_ERROR → exit 1 sans exception."""
    cli = _load_cli()
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)

    class _FailAdapter:
        def inspect_lock(self, path: str):
            raise RuntimeError("injected adapter failure")

    buf_err = io.StringIO()
    monkeypatch.setattr(cli, "TerminalSessionAdapter", _FailAdapter)
    monkeypatch.setattr(cli.sys, "stdout", _BrokenStdout())
    monkeypatch.setattr(cli.sys, "stderr", buf_err)

    code = cli.main(["--lock-path", str(lock)])
    assert code == 1, f"attendu 1 (broken pipe sur INTERNAL_ERROR), got {code}"
    assert buf_err.getvalue() == ""


def test_t59_flush_failure_returns_1(tmp_path, monkeypatch):
    """write réussit mais flush lève → exit 1 sans exception échappée, stderr vide."""
    cli = _load_cli()
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)

    flush_fail = _FlushFailStdout()
    buf_err = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", flush_fail)
    monkeypatch.setattr(cli.sys, "stderr", buf_err)

    code = cli.main(["--lock-path", str(lock)])
    assert code == 1, f"attendu 1 (flush failure), got {code}"
    assert buf_err.getvalue() == ""


# ============================================================
# T60-T62 : routage PS exact — correction B
# ============================================================

def _ps_route_block() -> str:
    """Extrait le bloc ROUTE SESSION INSPECT (commentaire + if) de obsidia.ps1."""
    lines = _PS.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if "ROUTE SESSION INSPECT" in l)
    # Le bloc se termine à la prochaine section majeure
    end = next(
        i for i, l in enumerate(lines[start + 1:], start + 1)
        if "POINT D'ENTREE PRINCIPAL" in l or "POINT D" in l and "ENTREE" in l
    )
    return "\n".join(lines[start:end])


def test_t60_ps_route_uses_ceq_not_tolower_trim():
    """La route PS utilise -ceq et ne contient plus .ToLower() ni .Trim()."""
    block = _ps_route_block()
    assert '-ceq "session"' in block, "Route manque -ceq \"session\""
    assert '-ceq "inspect"' in block, "Route manque -ceq \"inspect\""
    assert ".ToLower()" not in block, ".ToLower() encore présent dans la route"
    assert ".Trim()" not in block, ".Trim() encore présent dans la route"


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t61_ps_uppercase_session_inspect_not_routed(tmp_path):
    """SESSION INSPECT (majuscules) ne déclenche pas la route session inspect."""
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    # Lecture en bytes pour éviter les erreurs d'encodage du fallthrough PS
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS),
         "SESSION", "INSPECT", "--lock-path", str(lock)],
        capture_output=True, timeout=30,
    )
    is_session_inspect = (
        b'"command"' in r.stdout and b'"obsidia session inspect"' in r.stdout
    )
    assert not is_session_inspect, "Route SESSION INSPECT déclenchée alors qu'elle est interdite"


@pytest.mark.skipif(not _PS_AVAILABLE, reason="PowerShell non disponible")
def test_t62_ps_mixedcase_session_inspect_not_routed(tmp_path):
    """Session Inspect (casse mixte) ne déclenche pas la route session inspect."""
    lock = tmp_path / "lock.json"
    _make_valid_lock(lock)
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_PS),
         "Session", "Inspect", "--lock-path", str(lock)],
        capture_output=True, timeout=30,
    )
    is_session_inspect = (
        b'"command"' in r.stdout and b'"obsidia session inspect"' in r.stdout
    )
    assert not is_session_inspect, "Route Session Inspect déclenchée alors qu'elle est interdite"
