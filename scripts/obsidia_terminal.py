#!/usr/bin/env python3
"""scripts/obsidia_terminal.py — Canonical minimal Terminal Shell (T2).

Standard library only. Never imports scripts/obsidia_cli.py or any
Obsidia runtime component (Gateway, MCP, Brody, Obsidur, Router,
Kernel). No network, no subprocess, no Git call, no service start.
Never decides ACT, HOLD or BLOCK. Default execution mode is READ_ONLY;
the only write-capable command is `init`, bounded to a state directory
and gated by an explicit human decision reference.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

EXIT_SUCCESS = 0
EXIT_INVALID_ARGUMENT = 2
EXIT_SCHEMA_INCOMPATIBLE = 3
EXIT_UNKNOWN_COMMAND = 4
EXIT_AUTHORITY_MISSING = 5
EXIT_POLICY_DENY = 6
EXIT_PATH_OUTSIDE_SCOPE = 7
EXIT_NOT_IMPLEMENTED = 8
EXIT_INTERNAL_ERROR = 9

TERMINAL_SOURCE = "scripts/obsidia_terminal.py"
VERSION = "1.0.0"
STATE_FILENAME = "terminal_state.json"

REGISTERED_COMMANDS = ("commands", "envelope validate", "help", "init", "status", "version")

# Commands known from BUILD_TERMINAL_COMMANDES.csv (future paliers T3+),
# recognized so they fail closed with NOT_IMPLEMENTED_IN_T2 rather than
# a generic UNKNOWN_COMMAND.
FUTURE_KNOWN_COMMANDS = frozenset({
    "mission", "workspace", "branch", "baseline", "mode", "ask", "brody",
    "obsidur", "route", "ir", "memory", "graphiti", "files", "symbols",
    "deps", "git", "diff", "test", "lean", "kernel", "shadow", "sandbox",
    "promote", "hold", "discard", "receipt", "risk", "permissions",
    "agents", "tools", "explain", "sources", "gateway", "mcp",
})

ENVELOPE_SCHEMA_VERSION = "TERMINAL_COMMAND_ENVELOPE_V1"
ENVELOPE_REQUIRED_FIELDS = (
    "schema_version", "command_id", "command_name", "command_args",
    "requested_output_format", "requested_execution_mode",
    "correlation_id", "issued_at", "working_directory_ref", "state_dir_ref",
)
ENVELOPE_OPTIONAL_FIELDS = (
    "mission_contract_ref", "mission_revision", "human_decision_ref",
    "capability_request_refs", "context_request_ref",
)
ENVELOPE_ALL_FIELDS = frozenset(ENVELOPE_REQUIRED_FIELDS + ENVELOPE_OPTIONAL_FIELDS)
VALID_OUTPUT_FORMATS = frozenset({"HUMAN", "JSON"})
VALID_EXECUTION_MODES = frozenset({"READ_ONLY", "INTERNAL_OPERATIONAL_WRITE"})

SECRET_KEY_HINTS = ("password", "secret", "token", "api_key", "credential", "bearer")


class TerminalError(Exception):
    def __init__(self, exit_code: int, reason_code: str, message: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.reason_code = reason_code
        self.message = message


def _json_dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Path containment (resolver is injectable for deterministic testing)
# ---------------------------------------------------------------------------

def default_resolver(path):
    return Path(path).resolve(strict=False)


def check_path_containment(path_str, allowed_roots, resolver=None):
    """Returns (ok: bool, reason_code: str|None). No I/O beyond path resolution.

    The injectable `resolver` is applied only to the untrusted candidate
    path (it simulates symlink/junction resolution for testing). The
    trusted `allowed_roots` are always resolved with the real filesystem
    resolver, so a spoofed resolver cannot make the roots "follow" the
    escape and mask it."""
    candidate_resolver = resolver or default_resolver
    if not path_str:
        return False, "PATH_OUTSIDE_SCOPE"
    try:
        resolved = candidate_resolver(path_str)
    except Exception:
        return False, "PATH_OUTSIDE_SCOPE"
    resolved_str = str(resolved)
    for root in allowed_roots or []:
        try:
            root_resolved = str(default_resolver(root))
        except Exception:
            continue
        try:
            common = os.path.commonpath([root_resolved, resolved_str])
        except ValueError:
            continue
        if common == root_resolved:
            return True, None
    return False, "PATH_ESCAPE_REJECTED" if allowed_roots else "PATH_OUTSIDE_SCOPE"


# ---------------------------------------------------------------------------
# Envelope validation (pure function — no I/O)
# ---------------------------------------------------------------------------

def _looks_like_inline_secret(value) -> bool:
    if not isinstance(value, str):
        return False
    return "BEGIN PRIVATE KEY" in value or "BEGIN RSA PRIVATE KEY" in value or "BEGIN OPENSSH PRIVATE KEY" in value


def validate_envelope(envelope):
    """Returns (ok: bool, exit_code: int, reason_code: str|None, detail: str|None)."""
    if not isinstance(envelope, dict):
        return False, EXIT_INVALID_ARGUMENT, "INVALID_JSON", "envelope is not a JSON object"

    unknown = set(envelope.keys()) - ENVELOPE_ALL_FIELDS
    if unknown:
        return False, EXIT_INVALID_ARGUMENT, "FORBIDDEN_ARGUMENT", f"unknown fields: {sorted(unknown)}"

    missing = [f for f in ENVELOPE_REQUIRED_FIELDS if f not in envelope]
    if missing:
        return False, EXIT_INVALID_ARGUMENT, "REQUIRED_FIELD_MISSING", f"missing fields: {missing}"

    if envelope["schema_version"] != ENVELOPE_SCHEMA_VERSION:
        return False, EXIT_SCHEMA_INCOMPATIBLE, "UNKNOWN_SCHEMA_VERSION", (
            f"schema_version {envelope['schema_version']!r} incompatible"
        )

    if envelope["requested_output_format"] not in VALID_OUTPUT_FORMATS:
        return False, EXIT_INVALID_ARGUMENT, "INVALID_VALUE", "requested_output_format invalid"

    if envelope["requested_execution_mode"] not in VALID_EXECUTION_MODES:
        return False, EXIT_INVALID_ARGUMENT, "INVALID_VALUE", "requested_execution_mode invalid"

    command_name = envelope.get("command_name")
    if not isinstance(command_name, str) or not command_name.strip():
        return False, EXIT_INVALID_ARGUMENT, "INVALID_VALUE", "command_name invalid"

    command_args = envelope.get("command_args")
    if not isinstance(command_args, dict):
        return False, EXIT_INVALID_ARGUMENT, "INVALID_VALUE", "command_args must be an object"
    for key, value in command_args.items():
        if any(hint in key.lower() for hint in SECRET_KEY_HINTS) and isinstance(value, str) and len(value) >= 8:
            return False, EXIT_POLICY_DENY, "SECRET_INLINE_FORBIDDEN", "inline secret-like value in command_args"
        if _looks_like_inline_secret(value):
            return False, EXIT_POLICY_DENY, "SECRET_INLINE_FORBIDDEN", "inline secret-like value in command_args"

    if envelope["requested_execution_mode"] == "INTERNAL_OPERATIONAL_WRITE":
        hdr = envelope.get("human_decision_ref")
        if not hdr or not isinstance(hdr, str) or not hdr.strip():
            return False, EXIT_AUTHORITY_MISSING, "HUMAN_DECISION_REF_MISSING", (
                "mutating command requires human_decision_ref"
            )

    verb = command_name.strip().split()[0].lower()
    registered_verbs = {"help", "version", "commands", "status", "init", "envelope"}
    if verb not in registered_verbs:
        if verb in FUTURE_KNOWN_COMMANDS:
            return False, EXIT_NOT_IMPLEMENTED, "NOT_IMPLEMENTED_IN_T2", f"{verb} not implemented in T2"
        return False, EXIT_UNKNOWN_COMMAND, "COMMAND_NOT_REGISTERED", f"{verb} not registered"

    return True, EXIT_SUCCESS, None, None


# ---------------------------------------------------------------------------
# State (init / status)
# ---------------------------------------------------------------------------

def _valid_state_shape(state) -> bool:
    if not isinstance(state, dict):
        return False
    required = (
        "schema_version", "terminal_source", "history_initialized", "history",
        "initialization_authority", "initialization_decision_ref_sha256",
        "network_used", "subprocess_used", "runtime_components_called",
    )
    if any(k not in state for k in required):
        return False
    if state.get("schema_version") != "TERMINAL_STATE_V1":
        return False
    if state.get("terminal_source") != TERMINAL_SOURCE:
        return False
    if state.get("history_initialized") is not True:
        return False
    if not isinstance(state.get("history"), list):
        return False
    return True


def load_state(state_dir):
    path = Path(state_dir) / STATE_FILENAME
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path, obj) -> None:
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    data = _json_dumps(obj)
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def cmd_init(state_dir, human_decision_ref, environ, allowed_write_roots, resolver):
    ok, reason = check_path_containment(state_dir, allowed_write_roots, resolver)
    if not ok:
        raise TerminalError(EXIT_PATH_OUTSIDE_SCOPE, reason, "state-dir outside allowed write scope")

    authorized_ref = environ.get("OBSIDIA_T2_AUTHORIZED_DECISION_REF")
    if not authorized_ref:
        raise TerminalError(EXIT_AUTHORITY_MISSING, "AUTHORIZED_DECISION_REF_UNAVAILABLE",
                             "OBSIDIA_T2_AUTHORIZED_DECISION_REF not set")

    if not human_decision_ref or not str(human_decision_ref).strip():
        raise TerminalError(EXIT_AUTHORITY_MISSING, "HUMAN_DECISION_REF_MISSING",
                             "--human-decision-ref required for init")

    if human_decision_ref != authorized_ref:
        raise TerminalError(EXIT_AUTHORITY_MISSING, "HUMAN_DECISION_REF_MISMATCH",
                             "human-decision-ref does not match authorized reference")

    state_path = Path(state_dir)
    existing = load_state(state_dir) if state_path.exists() else None

    new_state = {
        "schema_version": "TERMINAL_STATE_V1",
        "terminal_source": TERMINAL_SOURCE,
        "history_initialized": True,
        "history": [],
        "initialization_authority": "BOUNDED_REFERENCE_MATCH_ONLY",
        "initialization_decision_ref_sha256": sha256_text(human_decision_ref),
        "network_used": False,
        "subprocess_used": False,
        "runtime_components_called": [],
    }

    if existing is not None:
        if _valid_state_shape(existing):
            return {"status": "ALREADY_INITIALIZED"}
        raise TerminalError(EXIT_POLICY_DENY, "EXISTING_STATE_INVALID",
                             "existing state file invalid or incompatible")

    state_path.mkdir(parents=True, exist_ok=True)
    atomic_write_json(state_path / STATE_FILENAME, new_state)
    return {"status": "SUCCESS"}


def cmd_status(state_dir, allowed_read_roots, resolver):
    ok, reason = check_path_containment(state_dir, allowed_read_roots, resolver)
    if not ok:
        raise TerminalError(EXIT_PATH_OUTSIDE_SCOPE, reason, "state-dir outside allowed read scope")

    state = load_state(state_dir)
    if state is None or not _valid_state_shape(state):
        raise TerminalError(EXIT_POLICY_DENY, "EXISTING_STATE_INVALID", "state not initialized or invalid")

    return {
        "schema_version": "TERMINAL_STATUS_V1",
        "status": "OK",
        "terminal_source": TERMINAL_SOURCE,
        "execution_mode": "READ_ONLY",
        "network_used": state["network_used"],
        "subprocess_used": state["subprocess_used"],
        "runtime_components_called": state["runtime_components_called"],
        "history_initialized": state["history_initialized"],
        "state_dir_contained": True,
        "encoding": "UTF-8",
    }


def _validate_envelope_from_file(input_file, vector_id, allowed_read_roots, resolver):
    ok, reason = check_path_containment(input_file, allowed_read_roots, resolver)
    if not ok:
        raise TerminalError(EXIT_PATH_OUTSIDE_SCOPE, reason, "input file outside allowed read scope")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        raise TerminalError(EXIT_INVALID_ARGUMENT, "INVALID_JSON", "cannot read/parse input file")

    vectors = data.get("envelope_vectors", {})
    if vector_id not in vectors:
        raise TerminalError(EXIT_INVALID_ARGUMENT, "INVALID_VALUE", f"unknown vector_id {vector_id}")

    envelope = vectors[vector_id]
    valid, code, reason_code, detail = validate_envelope(envelope)
    if not valid:
        raise TerminalError(code, reason_code, detail or "envelope invalid")


# ---------------------------------------------------------------------------
# argv parsing (stdlib only, no argparse subparser dependency required)
# ---------------------------------------------------------------------------

def _parse_kv_args(args):
    out = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            key = a[2:]
            if "=" in key:
                k, v = key.split("=", 1)
                out[k] = v
                i += 1
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                out[key] = args[i + 1]
                i += 2
            else:
                out[key] = True
                i += 1
        else:
            out.setdefault("_positional", []).append(a)
            i += 1
    return out


def _help_text() -> str:
    return (
        f"{TERMINAL_SOURCE} -- canonical minimal Terminal Shell (T2)\n"
        "Commands: help, version, commands, status, envelope validate, init\n"
        "Standard library only. No network. No subprocess. No runtime component calls.\n"
    )


def _emit(stdout, fmt, payload, human_text) -> None:
    if fmt == "JSON":
        stdout.write(_json_dumps(payload) + "\n")
    else:
        stdout.write(human_text + "\n")


def _emit_error(stderr, fmt, error: TerminalError) -> None:
    payload = {"schema_version": "TERMINAL_ERROR_V1", "exit_code": error.exit_code, "reason_code": error.reason_code}
    if fmt == "JSON":
        stderr.write(_json_dumps(payload) + "\n")
    else:
        stderr.write(f"ERROR {error.reason_code}\n")


def run(argv, environ, stdin, stdout, stderr, path_resolver=None,
        allowed_write_roots=None, allowed_read_roots=None) -> int:
    """Pure-ish entry point: all external dependencies are injected so the
    shell can be exercised deterministically without touching the real
    environment, filesystem beyond the given roots, or process streams."""
    resolver = path_resolver or default_resolver
    allowed_write_roots = list(allowed_write_roots or [])
    allowed_read_roots = list(allowed_read_roots or []) + allowed_write_roots

    fmt = "HUMAN"
    try:
        if not argv or argv[0] in ("-h", "--help"):
            stdout.write(_help_text())
            return EXIT_SUCCESS

        command = argv[0]
        rest = argv[1:]
        kv = _parse_kv_args(rest)
        if "format" in kv:
            fmt = str(kv["format"]).upper()

        if command == "version":
            payload = {"schema_version": "TERMINAL_VERSION_V1", "terminal_source": TERMINAL_SOURCE, "version": VERSION}
            _emit(stdout, fmt, payload, f"{TERMINAL_SOURCE} version {VERSION}")
            return EXIT_SUCCESS

        if command == "commands":
            payload = {"schema_version": "TERMINAL_COMMANDS_V1", "commands": sorted(REGISTERED_COMMANDS)}
            _emit(stdout, fmt, payload, "\n".join(sorted(REGISTERED_COMMANDS)))
            return EXIT_SUCCESS

        if command == "init":
            state_dir = kv.get("state-dir")
            hdr = kv.get("human-decision-ref")
            if not state_dir:
                raise TerminalError(EXIT_INVALID_ARGUMENT, "REQUIRED_FIELD_MISSING", "--state-dir required")
            payload = cmd_init(state_dir, hdr, environ, allowed_write_roots, resolver)
            _emit(stdout, fmt, payload, str(payload.get("status")))
            return EXIT_SUCCESS

        if command == "status":
            state_dir = kv.get("state-dir")
            if not state_dir:
                raise TerminalError(EXIT_INVALID_ARGUMENT, "REQUIRED_FIELD_MISSING", "--state-dir required")
            payload = cmd_status(state_dir, allowed_read_roots, resolver)
            _emit(stdout, fmt, payload, str(payload.get("status")))
            return EXIT_SUCCESS

        if command == "envelope":
            if not rest or rest[0] != "validate":
                raise TerminalError(EXIT_UNKNOWN_COMMAND, "COMMAND_NOT_REGISTERED", "envelope subcommand unknown")
            input_file = kv.get("input-file")
            vector_id = kv.get("vector-id")
            if not input_file or not vector_id:
                raise TerminalError(EXIT_INVALID_ARGUMENT, "REQUIRED_FIELD_MISSING",
                                     "--input-file and --vector-id required")
            _validate_envelope_from_file(input_file, vector_id, allowed_read_roots, resolver)
            payload = {"schema_version": "TERMINAL_ENVELOPE_VALIDATION_V1", "valid": True}
            _emit(stdout, fmt, payload, "VALID")
            return EXIT_SUCCESS

        verb = command.lower()
        if verb in FUTURE_KNOWN_COMMANDS:
            raise TerminalError(EXIT_NOT_IMPLEMENTED, "NOT_IMPLEMENTED_IN_T2", f"{verb} not implemented in T2")

        raise TerminalError(EXIT_UNKNOWN_COMMAND, "COMMAND_NOT_REGISTERED", f"{command} not registered")

    except TerminalError as e:
        _emit_error(stderr, fmt, e)
        return e.exit_code
    except Exception:
        _emit_error(stderr, fmt, TerminalError(EXIT_INTERNAL_ERROR, "INTERNAL_ERROR_REDACTED", "internal error"))
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    _repo_root = str(Path(__file__).resolve().parent.parent)
    _write_root = os.environ.get("OBSIDIA_T2_WRITE_ROOT")
    _extra_read_roots = os.environ.get("OBSIDIA_T2_READ_ROOTS", "")

    _write_roots = [_write_root] if _write_root else []
    _read_roots = [_repo_root] + [p for p in _extra_read_roots.split(";") if p]

    sys.exit(run(
        sys.argv[1:], os.environ, sys.stdin, sys.stdout, sys.stderr,
        allowed_write_roots=_write_roots, allowed_read_roots=_read_roots,
    ))
