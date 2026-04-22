from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def emit(obj: dict) -> None:
    print(json.dumps(obj, indent=2))
    raise SystemExit(0)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")


def same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except Exception:
        return str(a) == str(b)


def copy_if_needed(src: Path, dst: Path) -> None:
    if not same_path(src, dst):
        shutil.copy2(src, dst)


def main() -> None:
    if len(sys.argv) < 5:
        emit(
            {
                "decision_id": None,
                "target": None,
                "status": "incomplete",
                "verified": False,
                "trace_path": None,
                "vars_path": None,
                "stdout_path": None,
                "stderr_path": None,
                "reason": "Usage: verify_tla.py <decision_id> <trace_path> <vars_path> <target>",
                "dependency_test": {
                    "with_instance_returncode": None,
                    "without_instance_returncode": None,
                    "spec_depends_on_instance": False,
                },
            }
        )

    decision_id = sys.argv[1]
    trace_arg = sys.argv[2]
    vars_arg = sys.argv[3]
    target = sys.argv[4]

    trace_in = Path(trace_arg)
    vars_in = Path(vars_arg)

    out_dir = Path("traces") / "tla" / decision_id
    out_dir.mkdir(parents=True, exist_ok=True)

    stable_trace = out_dir / "trace.json"
    stable_vars = out_dir / "vars.json"
    stdout_path = out_dir / "tlc.stdout.log"
    stderr_path = out_dir / "tlc.stderr.log"

    result = {
        "decision_id": decision_id,
        "target": target,
        "status": "incomplete",
        "verified": False,
        "trace_path": str(stable_trace.resolve()),
        "vars_path": str(stable_vars.resolve()),
        "stdout_path": str(stdout_path.resolve()),
        "stderr_path": str(stderr_path.resolve()),
        "reason": "",
        "dependency_test": {
            "with_instance_returncode": None,
            "without_instance_returncode": None,
            "spec_depends_on_instance": False,
        },
    }

    if not trace_in.exists() or not vars_in.exists():
        result["reason"] = "Trace or vars file not found"
        emit(result)

    try:
        copy_if_needed(trace_in, stable_trace)
        copy_if_needed(vars_in, stable_vars)
    except PermissionError as e:
        result["reason"] = f"Trace or vars file locked: {e}"
        emit(result)
    except Exception as e:
        result["reason"] = f"Trace staging failed: {e}"
        emit(result)

    enabled = os.getenv("OBSIDIA_TLA_ENABLED", "").strip().lower() == "true"
    if not enabled:
        result["reason"] = "TLA verification disabled (OBSIDIA_TLA_ENABLED not set)"
        emit(result)

    tlc_cmd = os.getenv("OBSIDIA_TLA_TLC_CMD", "").strip()
    if not tlc_cmd:
        result["reason"] = "TLC command not configured"
        emit(result)

    tla_root = Path(
        os.getenv("OBSIDIA_TLA_ROOT", str((Path.cwd() / "proofs" / "tla").resolve()))
    )
    if not tla_root.exists():
        result["reason"] = f"TLA root not found: {tla_root}"
        emit(result)

    spec_file = Path(target).name
    cfg_file = spec_file.replace(".tla", ".cfg")

    spec_path = tla_root / spec_file
    cfg_path = tla_root / cfg_file

    if not spec_path.exists():
        result["reason"] = f"Spec not found: {spec_path}"
        emit(result)

    if not cfg_path.exists():
        result["reason"] = f"Config not found: {cfg_path}"
        emit(result)

    timeout_ms = int(os.getenv("OBSIDIA_TLA_TIMEOUT", "300000"))
    if spec_file.lower().startswith("distributed") and timeout_ms < 300000:
        timeout_ms = 300000

    command = f'{tlc_cmd} -cleanup -deadlock -config "{cfg_file}" "{spec_file}"'

    try:
        run = subprocess.run(
            command,
            cwd=str(tla_root),
            capture_output=True,
            text=True,
            timeout=timeout_ms / 1000.0,
            shell=True,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired as e:
        write_text(stdout_path, e.stdout or "")
        write_text(stderr_path, e.stderr or "")
        result["reason"] = f"TLC timeout after {timeout_ms}ms"
        emit(result)
    except Exception as e:
        write_text(stdout_path, "")
        write_text(stderr_path, str(e))
        result["reason"] = f"TLC launch exception: {e}"
        emit(result)

    write_text(stdout_path, run.stdout or "")
    write_text(stderr_path, run.stderr or "")

    result["dependency_test"]["with_instance_returncode"] = run.returncode

    if run.returncode == 0:
        result["status"] = "verified"
        result["verified"] = True
        result["reason"] = "TLC verification passed"
        emit(result)

    stderr_lower = (run.stderr or "").lower()
    stdout_lower = (run.stdout or "").lower()

    if "classnotfoundexception" in stderr_lower or "could not find or load main class" in stderr_lower:
        result["reason"] = "TLC launcher misconfigured"
    elif "timeout" in stderr_lower:
        result["reason"] = "TLC timeout"
    elif "invariant" in stderr_lower or "invariant" in stdout_lower:
        result["reason"] = "Invariant/property check failed"
    else:
        result["reason"] = "Spec verification failed even WITH instance"

    result["status"] = "failed"
    result["verified"] = False
    emit(result)


if __name__ == "__main__":
    main()
