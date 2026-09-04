from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_forbidden_content.py"


def _run_checker(repo: Path) -> subprocess.CompletedProcess[str]:

    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)

    shutil.copy2(
        CHECKER,
        scripts / "check_forbidden_content.py",
    )

    return subprocess.run(
        [
            sys.executable,
            "scripts/check_forbidden_content.py",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )


def _write(
    root: Path,
    relative: str,
    body: str = "# test fixture\n",
) -> None:

    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def test_exact_brody_defensive_scrubber_path_is_allowed(
    tmp_path: Path,
) -> None:

    _write(
        tmp_path,
        "apps/obsidia_api/brody_secret_scrubber.py",
    )

    result = _run_checker(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout


def test_same_sensitive_basename_elsewhere_is_still_rejected(
    tmp_path: Path,
) -> None:

    _write(
        tmp_path,
        "other/brody_secret_scrubber.py",
    )

    result = _run_checker(tmp_path)

    assert result.returncode == 1
    assert (
        "SUSPICIOUS_FILE:./other/brody_secret_scrubber.py"
        in result.stdout
    )


def test_other_secret_named_file_in_obsidia_api_is_still_rejected(
    tmp_path: Path,
) -> None:

    _write(
        tmp_path,
        "apps/obsidia_api/runtime_secret_dump.py",
    )

    result = _run_checker(tmp_path)

    assert result.returncode == 1
    assert (
        "SUSPICIOUS_FILE:./apps/obsidia_api/runtime_secret_dump.py"
        in result.stdout
    )


def test_other_token_named_file_in_obsidia_api_is_still_rejected(
    tmp_path: Path,
) -> None:

    _write(
        tmp_path,
        "apps/obsidia_api/runtime_token_dump.py",
    )

    result = _run_checker(tmp_path)

    assert result.returncode == 1
    assert (
        "SUSPICIOUS_FILE:./apps/obsidia_api/runtime_token_dump.py"
        in result.stdout
    )


def test_policy_is_exact_path_not_basename_allowlist() -> None:

    source = CHECKER.read_text(encoding="utf-8")

    assert "ALLOWED_EXACT_PATHS" in source
    assert (
        '"apps/obsidia_api/brody_secret_scrubber.py"'
        in source
    )

    # The defensive exception must not be added to the old basename
    # ALLOWED_FILES mechanism.
    allowed_files_section = source.split(
        "ALLOWED_FILES = {",
        1,
    )[1].split("}", 1)[0]

    assert "brody_secret_scrubber.py" not in allowed_files_section
