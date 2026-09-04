"""
Bounded Execution Policy V1
===========================

Obsidia execution must never rely on:

    arbitrary fixed timeout
    OR
    infinite waiting.

The policy distinguishes:

    PASS
    PROCESS_ERROR
    TIMEOUT_NO_PROGRESS
    TIMEOUT_HARD_LIMIT

Two independent boundaries exist:

    idle deadline
        no observable stdout/stderr progress for too long.

    hard deadline
        absolute maximum runtime regardless of progress.

Budgets are command-class specific and environment-overridable.

This module has:
    no decision authority,
    no repo authority,
    no memory authority,
    no WorldAction authority.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence


POLICY_ID = (
    "BOUNDED_EXECUTION_POLICY_V1"
)

DECISION_AUTHORITY = (
    "KX108_ONLY"
)


STATUS_PASS = "PASS"

STATUS_PROCESS_ERROR = (
    "PROCESS_ERROR"
)

STATUS_TIMEOUT_NO_PROGRESS = (
    "TIMEOUT_NO_PROGRESS"
)

STATUS_TIMEOUT_HARD_LIMIT = (
    "TIMEOUT_HARD_LIMIT"
)


EXIT_TIMEOUT_HARD_LIMIT = 124

EXIT_TIMEOUT_NO_PROGRESS = 125


@dataclass(
    frozen=True
)
class ExecutionBudget:

    label: str

    hard_seconds: float

    idle_seconds: float

    poll_seconds: float = 0.20


@dataclass
class BoundedCompletedProcess:

    args: Sequence[str]

    returncode: int

    stdout: str

    stderr: str

    bounded_status: str

    elapsed_seconds: float

    progress_events: int

    budget_label: str

    hard_deadline_seconds: float

    idle_deadline_seconds: float


def _env_float(
    name: str,
    default: float,
) -> float:

    raw = os.environ.get(
        name,
        "",
    ).strip()

    if not raw:
        return float(
            default
        )

    try:
        value = float(
            raw
        )

    except ValueError:
        return float(
            default
        )

    if value <= 0:
        return float(
            default
        )

    return value


def budget_for_test_command(
    command: str,
) -> ExecutionBudget:

    normalized = (
        command
        .replace(
            "\\",
            "/",
        )
        .lower()
    )

    is_pytest = (
        "pytest"
        in normalized
    )

    full_suite = (
        is_pytest
        and (
            " pytest tests/ "
            in (
                " "
                + normalized
                + " "
            )
            or normalized.endswith(
                " pytest tests/"
            )
            or "pytest tests -"
            in normalized
        )
    )


    if full_suite:

        return ExecutionBudget(
            label=(
                "PYTEST_FULL_SUITE"
            ),
            hard_seconds=(
                _env_float(
                    (
                        "OBSIDIA_FULL_TEST_"
                        "HARD_SECONDS"
                    ),
                    7200,
                )
            ),
            idle_seconds=(
                _env_float(
                    (
                        "OBSIDIA_FULL_TEST_"
                        "IDLE_SECONDS"
                    ),
                    600,
                )
            ),
        )


    if is_pytest:

        return ExecutionBudget(
            label=(
                "PYTEST_FOCUSED"
            ),
            hard_seconds=(
                _env_float(
                    (
                        "OBSIDIA_FOCUSED_TEST_"
                        "HARD_SECONDS"
                    ),
                    1800,
                )
            ),
            idle_seconds=(
                _env_float(
                    (
                        "OBSIDIA_FOCUSED_TEST_"
                        "IDLE_SECONDS"
                    ),
                    300,
                )
            ),
        )


    return ExecutionBudget(
        label="GENERIC_COMMAND",
        hard_seconds=(
            _env_float(
                (
                    "OBSIDIA_GENERIC_"
                    "HARD_SECONDS"
                ),
                900,
            )
        ),
        idle_seconds=(
            _env_float(
                (
                    "OBSIDIA_GENERIC_"
                    "IDLE_SECONDS"
                ),
                180,
            )
        ),
    )


def _kill_process_tree(
    process: subprocess.Popen,
) -> None:

    if process.poll() is not None:
        return


    try:

        if os.name == "nt":

            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(
                        process.pid
                    ),
                    "/T",
                    "/F",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                shell=False,
            )

        else:

            try:
                pgid = os.getpgid(
                    process.pid
                )

                os.killpg(
                    pgid,
                    signal.SIGKILL,
                )

            except Exception:

                process.kill()


    except Exception:

        try:
            process.kill()

        except Exception:
            pass


def _timeout_marker(
    *,
    status: str,
    budget: ExecutionBudget,
    elapsed: float,
    progress_events: int,
) -> str:

    return (
        "\n"
        "[OBSIDIA_BOUNDED_EXECUTION]\n"
        f"policy={POLICY_ID}\n"
        f"status={status}\n"
        f"budget={budget.label}\n"
        f"elapsed_seconds={elapsed:.3f}\n"
        f"hard_deadline_seconds={budget.hard_seconds:.3f}\n"
        f"idle_deadline_seconds={budget.idle_seconds:.3f}\n"
        f"progress_events={progress_events}\n"
    )


def _delegated_runner(
    argv: Sequence[str],
    *,
    cwd: Path,
    budget: ExecutionBudget,
    run_callable: Callable[..., Any],
) -> Any:

    start = time.monotonic()

    try:

        result = run_callable(
            list(
                argv
            ),
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=(
                budget.hard_seconds
            ),
        )

    except subprocess.TimeoutExpired as exc:

        elapsed = (
            time.monotonic()
            - start
        )

        stdout = exc.stdout or ""

        stderr = exc.stderr or ""

        if isinstance(
            stdout,
            bytes,
        ):
            stdout = stdout.decode(
                "utf-8",
                errors="replace",
            )

        if isinstance(
            stderr,
            bytes,
        ):
            stderr = stderr.decode(
                "utf-8",
                errors="replace",
            )

        marker = _timeout_marker(
            status=(
                STATUS_TIMEOUT_HARD_LIMIT
            ),
            budget=budget,
            elapsed=elapsed,
            progress_events=0,
        )

        return BoundedCompletedProcess(
            args=list(
                argv
            ),
            returncode=(
                EXIT_TIMEOUT_HARD_LIMIT
            ),
            stdout=str(
                stdout
            ),
            stderr=(
                str(
                    stderr
                )
                + marker
            ),
            bounded_status=(
                STATUS_TIMEOUT_HARD_LIMIT
            ),
            elapsed_seconds=elapsed,
            progress_events=0,
            budget_label=(
                budget.label
            ),
            hard_deadline_seconds=(
                budget.hard_seconds
            ),
            idle_deadline_seconds=(
                budget.idle_seconds
            ),
        )


    # Preserve fake/mocked result compatibility.
    try:
        setattr(
            result,
            "bounded_status",
            (
                STATUS_PASS
                if result.returncode == 0
                else STATUS_PROCESS_ERROR
            ),
        )

        setattr(
            result,
            "elapsed_seconds",
            (
                time.monotonic()
                - start
            ),
        )

        setattr(
            result,
            "progress_events",
            0,
        )

        setattr(
            result,
            "budget_label",
            budget.label,
        )

        setattr(
            result,
            "hard_deadline_seconds",
            budget.hard_seconds,
        )

        setattr(
            result,
            "idle_deadline_seconds",
            budget.idle_seconds,
        )

    except Exception:
        pass

    return result


def run_bounded_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    budget: ExecutionBudget,
    run_callable: Callable[..., Any] | None = None,
) -> Any:

    """
    Run one command with BOTH:

        no-progress deadline
        absolute hard deadline

    The native subprocess path observes stdout/stderr activity.

    Test/mocked runners are delegated so existing Build tests can
    continue intercepting subprocess.run.
    """

    runner = (
        run_callable
        or subprocess.run
    )


    # Existing unit tests commonly monkeypatch subprocess.run.
    # Detect that and preserve the mock boundary instead of spawning
    # an unexpected real child process.
    native_runner = (
        getattr(
            runner,
            "__module__",
            "",
        )
        == "subprocess"
        and getattr(
            runner,
            "__name__",
            "",
        )
        == "run"
    )


    if not native_runner:

        return _delegated_runner(
            argv,
            cwd=cwd,
            budget=budget,
            run_callable=runner,
        )


    creation_kwargs: dict[
        str,
        Any,
    ] = {}


    if os.name == "nt":

        creation_kwargs[
            "creationflags"
        ] = (
            subprocess
            .CREATE_NEW_PROCESS_GROUP
        )

    else:

        creation_kwargs[
            "start_new_session"
        ] = True


    start = time.monotonic()

    last_progress = start

    progress_events = 0

    stdout_parts: list[str] = []

    stderr_parts: list[str] = []

    lock = threading.Lock()


    process = subprocess.Popen(
        list(
            argv
        ),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        shell=False,
        **creation_kwargs,
    )


    def reader(
        stream,
        bucket: list[str],
    ) -> None:

        nonlocal last_progress, progress_events

        if stream is None:
            return

        try:

            for line in iter(
                stream.readline,
                "",
            ):

                bucket.append(
                    line
                )

                with lock:

                    last_progress = (
                        time.monotonic()
                    )

                    progress_events += 1

        finally:

            try:
                stream.close()

            except Exception:
                pass


    stdout_thread = threading.Thread(
        target=reader,
        args=(
            process.stdout,
            stdout_parts,
        ),
        daemon=True,
    )

    stderr_thread = threading.Thread(
        target=reader,
        args=(
            process.stderr,
            stderr_parts,
        ),
        daemon=True,
    )


    stdout_thread.start()

    stderr_thread.start()


    timeout_status = ""


    while True:

        rc = process.poll()

        now = time.monotonic()


        if rc is not None:
            break


        elapsed = (
            now
            - start
        )


        with lock:

            idle_elapsed = (
                now
                - last_progress
            )


        if elapsed >= (
            budget.hard_seconds
        ):

            timeout_status = (
                STATUS_TIMEOUT_HARD_LIMIT
            )

            _kill_process_tree(
                process
            )

            break


        if idle_elapsed >= (
            budget.idle_seconds
        ):

            timeout_status = (
                STATUS_TIMEOUT_NO_PROGRESS
            )

            _kill_process_tree(
                process
            )

            break


        time.sleep(
            budget.poll_seconds
        )


    try:

        process.wait(
            timeout=15
        )

    except Exception:

        _kill_process_tree(
            process
        )


    stdout_thread.join(
        timeout=5
    )

    stderr_thread.join(
        timeout=5
    )


    elapsed = (
        time.monotonic()
        - start
    )


    stdout = "".join(
        stdout_parts
    )

    stderr = "".join(
        stderr_parts
    )


    if timeout_status:

        marker = _timeout_marker(
            status=timeout_status,
            budget=budget,
            elapsed=elapsed,
            progress_events=(
                progress_events
            ),
        )

        stderr += marker


        return BoundedCompletedProcess(
            args=list(
                argv
            ),
            returncode=(
                EXIT_TIMEOUT_HARD_LIMIT
                if timeout_status
                == STATUS_TIMEOUT_HARD_LIMIT
                else EXIT_TIMEOUT_NO_PROGRESS
            ),
            stdout=stdout,
            stderr=stderr,
            bounded_status=(
                timeout_status
            ),
            elapsed_seconds=elapsed,
            progress_events=(
                progress_events
            ),
            budget_label=(
                budget.label
            ),
            hard_deadline_seconds=(
                budget.hard_seconds
            ),
            idle_deadline_seconds=(
                budget.idle_seconds
            ),
        )


    return BoundedCompletedProcess(
        args=list(
            argv
        ),
        returncode=(
            process.returncode
        ),
        stdout=stdout,
        stderr=stderr,
        bounded_status=(
            STATUS_PASS
            if process.returncode == 0
            else STATUS_PROCESS_ERROR
        ),
        elapsed_seconds=elapsed,
        progress_events=(
            progress_events
        ),
        budget_label=(
            budget.label
        ),
        hard_deadline_seconds=(
            budget.hard_seconds
        ),
        idle_deadline_seconds=(
            budget.idle_seconds
        ),
    )


def self_check() -> dict[str, Any]:

    return {
        "policy": POLICY_ID,
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "finite_execution": True,
        "idle_deadline": True,
        "hard_deadline": True,
        "progress_observed": True,
        "timeout_no_progress": (
            STATUS_TIMEOUT_NO_PROGRESS
        ),
        "timeout_hard_limit": (
            STATUS_TIMEOUT_HARD_LIMIT
        ),
        "repo_mutation": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "world_action": False,
    }
