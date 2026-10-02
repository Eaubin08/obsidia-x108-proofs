from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import obsidia_pc_capabilities_v2 as PC2
from jarjar_executor_bridge_v0 import make_executor
from jarjar_governed_patch_rollback_bridge_v0 import (
    PREPARED_AWAITING_HUMAN_APPROVAL,
    ROLLBACK_EXECUTED_OK,
    governed_rollback_patch_execute,
    governed_rollback_patch_prepare,
)


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    jarjar_src = os.environ.get("JARJAR_SRC_PATH", "").strip()
    if not jarjar_src:
        raise RuntimeError("JARJAR_SRC_PATH_REQUIRED")

    root = Path(tempfile.mkdtemp(prefix="jarjar-g5-physical-")).resolve()
    main_repo = root / "main"
    exec_wt = root / "exec"
    stores = root / "stores"
    main_repo.mkdir(parents=True)

    before = b"g5 physical before\n"
    after = b"g5 physical after\n"
    target_rel = "target.txt"
    (main_repo / target_rel).write_bytes(before)

    try:
        _git(main_repo, "init", "-q")
        _git(main_repo, "config", "user.email", "g5-physical@local.invalid")
        _git(main_repo, "config", "user.name", "G5 Physical")
        _git(main_repo, "config", "commit.gpgsign", "false")
        _git(main_repo, "add", target_rel)
        _git(main_repo, "commit", "-q", "-m", "seed")
        base_sha = _git(main_repo, "rev-parse", "HEAD")
        _git(main_repo, "worktree", "add", str(exec_wt), "-b", "g5-physical", base_sha)

        patch = (
            "--- a/target.txt\n"
            "+++ b/target.txt\n"
            "@@ -1 +1 @@\n"
            "-g5 physical before\n"
            "+g5 physical after\n"
        )

        executor = make_executor(exec_wt, jarjar_src=Path(jarjar_src))

        prep = PC2.pc_v2_apply_patch_prepare(
            patch,
            execution_worktree_path=exec_wt,
            main_worktree_path=main_repo,
            branch_name="g5-physical",
            base_sha=base_sha,
            stores_base_dir=stores,
            session_id="g5-physical-apply",
        )
        if prep.get("status") != PC2.PREPARED_AWAITING_HUMAN_APPROVAL:
            raise RuntimeError("APPLY_PREPARE_FAILED:" + json.dumps(prep, ensure_ascii=False))

        applied = PC2.pc_v2_apply_patch_execute(
            prep,
            prep["execution_authority_hash"],
            "HUMAN_G5_PHYSICAL_APPLY",
            stores_base_dir=stores,
            repo_root=exec_wt,
            session_id="g5-physical-apply",
            executor=executor,
        )
        if applied.get("status") != PC2.EXECUTED_OK:
            raise RuntimeError("APPLY_EXECUTE_FAILED:" + json.dumps(applied, ensure_ascii=False))

        target = exec_wt / target_rel
        realized_after = target.read_bytes()
        if realized_after != after:
            raise RuntimeError("APPLY_REALIZED_BYTES_MISMATCH")

        sre_ids = applied.get("sealed_rollback_evidence_ids") or []
        if len(sre_ids) != 1:
            raise RuntimeError("EXPECTED_EXACTLY_ONE_SRE")
        sre_id = sre_ids[0]
        sar_id = applied["sealed_apply_receipt_id"]

        rb_prep = governed_rollback_patch_prepare(
            sre_id,
            sar_id,
            sre_dir=stores / "sre",
            sar_dir=stores / "sar",
            v2exec_dir=stores / "v2exec",
            repo_root=exec_wt,
            session_id="g5-physical-rollback",
        )
        if rb_prep.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
            raise RuntimeError("ROLLBACK_PREPARE_FAILED:" + json.dumps(rb_prep, ensure_ascii=False))

        rolled = governed_rollback_patch_execute(
            rb_prep,
            rb_prep["rollback_authority_hash"],
            "HUMAN_G5_PHYSICAL_ROLLBACK",
            sre_dir=stores / "sre",
            sar_dir=stores / "sar",
            v2exec_dir=stores / "v2exec",
            executor=executor,
            repo_root=exec_wt,
            session_id="g5-physical-rollback",
        )
        if rolled.get("status") != ROLLBACK_EXECUTED_OK:
            raise RuntimeError("ROLLBACK_EXECUTE_FAILED:" + json.dumps(rolled, ensure_ascii=False))

        restored = target.read_bytes()
        if restored != before:
            raise RuntimeError("ROLLBACK_RESTORED_BYTES_MISMATCH")

        proof = {
            "status": "G5_PHYSICAL_PROOF_PASS",
            "operation": "V2_APPLY_PATCH",
            "rollback": "SINGLE_TARGET_EXACT_PREIMAGE_RESTORE",
            "executor_provider": rolled.get("executor_provider"),
            "executor_backend": executor.EXECUTOR_BACKEND,
            "decision_authority": rolled.get("decision_authority"),
            "kx108_invocations_during_rollback": rolled.get("kx108_invocations_during_rollback"),
            "human_authorization_consumed": rolled.get("human_authorization_consumed"),
            "pre_sha256": _sha(before),
            "post_sha256": _sha(after),
            "restored_sha256": _sha(restored),
            "restored_matches_preimage": _sha(restored) == _sha(before),
            "sealed_rollback_evidence_id": sre_id,
            "sealed_apply_receipt_id": sar_id,
            "temp_root": str(root),
        }
        print(json.dumps(proof, indent=2, ensure_ascii=False))
        return 0
    finally:
        try:
            _git(main_repo, "worktree", "remove", "--force", str(exec_wt))
        except Exception:
            pass
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
