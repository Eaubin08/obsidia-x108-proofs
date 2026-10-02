"""
obsidia_pc_capabilities_v2.py - PC Capabilities V2
GOVERNED_DELETE_FILE=DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS
OPENJARVIS_AUTHORITY=NONE KX108_ONLY=YES HUMAN_APPROVAL_REQUIRED=YES
"""
from __future__ import annotations
import base64, datetime, hashlib, json, os, re, subprocess, sys
from pathlib import Path
from typing import Optional
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path: sys.path.insert(0, str(_SCRIPTS))
import obsidia_batch_execution as _E
import obsidia_kx108_decision_store as _DS
import obsidia_sealed_evidence_v0 as _SEV
PC_CAPABILITY_V2_VERSION             = "V2"
PC_CAPABILITY_V2_MODE                = "GOVERNED_WRITE"
PC_CAPABILITY_IS_EXECUTION_AUTHORITY = False
PC_CAPABILITY_IS_KX_AUTHORITY        = False
KX_DECISION_AUTHORITY                = "KX108_ONLY"
JARVIS_AUTHORITY                     = "NONE"
HUMAN_APPROVAL_REQUIRED              = True
AUTO_EXECUTE                         = False
MUTATES_FILESYSTEM                   = True
ACCEPTS_ARBITRARY_SHELL              = False
ACCEPTS_ARBITRARY_GIT                = False
GENERIC_SHELL_ENABLED                = False
OP_CREATE_FILE              = "V2_CREATE_FILE"
OP_MOVE_FILE                = "V2_MOVE_FILE"
OP_APPLY_PATCH              = "V2_APPLY_PATCH"
OP_CREATE_DIR               = "V2_CREATE_DIR"
GOVERNED_DELETE_FILE_STATUS = "DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS"
_CAP_CREATE_PREPARE = "PC_V2_CREATE_FILE_PREPARE"
_CAP_CREATE_EXECUTE = "PC_V2_CREATE_FILE_EXECUTE"
_CAP_MOVE_PREPARE   = "PC_V2_MOVE_FILE_PREPARE"
_CAP_MOVE_EXECUTE   = "PC_V2_MOVE_FILE_EXECUTE"
_CAP_PATCH_PREPARE  = "PC_V2_APPLY_PATCH_PREPARE"
_CAP_PATCH_EXECUTE  = "PC_V2_APPLY_PATCH_EXECUTE"
_CAP_CDIR_PREPARE   = "PC_V2_CREATE_DIR_PREPARE"
_CAP_CDIR_EXECUTE   = "PC_V2_CREATE_DIR_EXECUTE"
_CAPABILITY_IDS_V2 = (_CAP_CREATE_PREPARE, _CAP_CREATE_EXECUTE, _CAP_MOVE_PREPARE, _CAP_MOVE_EXECUTE, _CAP_PATCH_PREPARE, _CAP_PATCH_EXECUTE)
PREPARED_AWAITING_HUMAN_APPROVAL = "PREPARED_AWAITING_HUMAN_APPROVAL"
EXECUTED_OK = "EXECUTED_OK"
PREPARE_REJECTED = "PREPARE_REJECTED"
EXECUTE_REJECTED = "EXECUTE_REJECTED"
EAH_MISMATCH = "EAH_MISMATCH"
REALIZED_STATE_MISMATCH = "REALIZED_STATE_MISMATCH"
_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
_PATCH_MAX_BYTES = 1_000_000
_PATCH_MAX_FILES = 20
_UNIFIED_DIFF_HDR = re.compile(r"^--- .+", re.MULTILINE)

def _sha256(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def _sha16(t: str) -> str: return hashlib.sha256(t.encode()).hexdigest()[:16]
def _now() -> str: return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _v2id(prefix: str, seed: str) -> str: return f"{prefix}-{_sha256(seed.encode())[:32]}"
def _stores(stores_base) -> dict:
    base = Path(stores_base)
    dirs = {}
    for n in ("v2exec","approval","kxpre","kxpost","sar","sre","rollback"):
        d = base / n; d.mkdir(parents=True, exist_ok=True); dirs[n] = d
    return dirs

def _check_isolation(exec_wt: Path, main_wt: Path, branch: str, base_sha: str) -> dict:
    def _git(*a):
        r = subprocess.run(["git"]+list(a), cwd=str(exec_wt), capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    rc, out, _ = _git("worktree", "list", "--porcelain")
    if rc != 0: return {"ok": False, "reason": "GIT_WORKTREE_LIST_FAILED"}
    entries, cur = [], {}
    for line in out.split("\n"):
        if line.startswith("worktree "):
            if cur: entries.append(cur)
            cur = {"wt": line[9:].strip()}
        elif line.startswith("branch "): cur["branch"] = line[7:].strip()
        elif line.startswith("HEAD "): cur["HEAD"] = line[5:].strip()
        elif line.strip() == "detached": cur["detached"] = True
    if cur: entries.append(cur)
    def _match(path): return next((e for e in entries if Path(e["wt"]).resolve()==Path(path).resolve()), None)
    em = _match(exec_wt); mm = _match(main_wt)
    if em is None: return {"ok": False, "reason": "EXEC_WORKTREE_NOT_REGISTERED"}
    if mm is None: return {"ok": False, "reason": "MAIN_WORKTREE_NOT_REGISTERED"}
    if exec_wt.resolve() == main_wt.resolve(): return {"ok": False, "reason": "EXEC_IS_MAIN"}
    if em.get("detached"): return {"ok": False, "reason": "EXEC_DETACHED"}
    obs = (em.get("branch") or "").replace("refs/heads/", "")
    if obs != branch: return {"ok": False, "reason": f"BRANCH_MISMATCH:{obs!r}"}
    if mm.get("branch"):
        mbr = mm["branch"].replace("refs/heads/", "")
        if mbr == branch: return {"ok": False, "reason": "BRANCH_NOT_ISOLATED"}
    rc2, head, _ = _git("rev-parse", "HEAD")
    if rc2 != 0 or head != base_sha: return {"ok": False, "reason": f"HEAD_MISMATCH:{head!r}"}
    rc3, st2, _ = _git("status", "--short")
    if rc3 != 0: return {"ok": False, "reason": "GIT_STATUS_FAILED"}
    if st2.strip(): return {"ok": False, "reason": f"WORKTREE_DIRTY:{st2.strip()!r}"}
    return {"ok": True, "worktree_isolated": True, "branch_isolated": True}

def _safe_rel(p: str) -> bool:
    if not p or not p.strip(): return False
    parts = Path(p.replace("\\", "/")).parts
    return bool(parts) and all(x not in (".","..","") and not x.startswith(".git") for x in parts)
def _canon(rel: str, root: Path) -> Optional[Path]:
    try:
        p = (root / rel.replace("\\", "/")).resolve()
        sr = str(root.resolve())
        if str(p) != sr and not str(p).startswith(sr + os.sep): return None
        return p
    except Exception: return None
def _eah(op: str, descriptor: dict) -> str:
    payload = json.dumps({"v2_schema": "PC_CAPABILITIES_V2_EAH_V0", "operation_type": op, "action_descriptor": descriptor}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()
def _persist_desc(v2id: str, op: str, eah: str, descriptor: dict, store: Path) -> str:
    rec = {"v2_exec_id": v2id, "operation_type": op, "eah": eah, "descriptor": descriptor, "decision_authority": KX_DECISION_AUTHORITY, "created_at": _now()}
    raw = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    dh = _sha256(raw.encode())
    (store / f"{v2id}.json").write_text(raw, encoding="utf-8")
    return dh
def _load_desc(v2id: str, store: Path) -> Optional[dict]:
    p = store / f"{v2id}.json"
    if not p.exists(): return None
    try: return json.loads(p.read_text("utf-8"))
    except Exception: return None
def _approval(v2id: str, child: str, eah: str, cand_seed: str) -> dict:
    scope = json.dumps({"v2_exec_id": v2id, "cand": cand_seed}, sort_keys=True)
    rec = {
        "approval_schema_version": _E.SCHEMA_VERSION,
        "approval_id": _v2id("apv", v2id+child+eah),
        "created_at": _now(),
        "batch_execution_id": v2id, "batch_id": v2id,
        "batch_hash": _sha16(v2id),
        "candidate_scope_hash": _sha16(scope),
        "execution_authority_hash": eah,
        "approved_by": _E.APPROVED_BY_HUMAN,
        "approval_status": _E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": KX_DECISION_AUTHORITY,
    }
    rec["approval_record_hash"] = _E.compute_approval_record_hash(rec)
    return rec
def _kx108_pre(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, *, kxpre) -> dict:
    xh = _sha256(json.dumps({"v2id":v2id,"child":child,"eah":eah,"apv":apv_id,"op":op}, sort_keys=True).encode())
    kwargs = {
        "session_id": child, "objective": f"V2 governed {op}",
        "base_sha": base_sha, "manifest_hash": mhash, "diff_hash": "",
        "approved_scope": list(paths),
        "actual_touched_files": [], "new_files": [], "deleted_files": [],
        "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED",
        "obsidure_status": "UNKNOWN",
        "worktree_isolated": True, "branch_isolated": True,
        "auto_commit_disabled": True, "auto_push_disabled": True, "auto_merge_disabled": True,
        "tests_results": "UNKNOWN", "gates_results": "UNKNOWN",
        "first_failure": "", "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED", "merge_status": "NOT_MERGED",
        "unknowns": [], "contradictions": [], "risk_flags": [],
        "decision_authority": KX_DECISION_AUTHORITY,
    }
    binding = {
        "batch_execution_id": v2id, "child_execution_id": child,
        "execution_authority_hash": eah, "approval_id": apv_id,
        "pre_execution_context_id": v2id,
        "pre_execution_context_record_hash": dh,
        "test_contract_hash": mhash,
        "kx108_input_translation_hash": xh,
    }
    return _DS.run_and_persist_kx108_pre_execution_decision(kwargs, binding, store_dir=kxpre)
def _sre(v2id, child, eah, apv_id, kx_id, kx_hash, tpath, before_b, cand_sha, op) -> dict:
    sid = _v2id("sre", v2id+child+tpath+_sha256(before_b))
    return {
        "schema_version": "V0", "sealed": True,
        "sealed_rollback_evidence_id": sid,
        "created_at": _now(),
        "batch_execution_id": v2id, "child_execution_id": child,
        "execution_authority_hash": eah, "approval_id": apv_id,
        "kx108_pre_decision_record_id": kx_id,
        "kx108_pre_decision_record_hash": kx_hash,
        "target_path": tpath,
        "pre_write_sha256": _sha256(before_b),
        "pre_write_size": len(before_b),
        "pre_write_bytes_b64": base64.b64encode(before_b).decode("ascii"),
        "source_content_sha256": cand_sha,
        "source_kind": "V2_OPERATION", "source_identity": op,
        "operation_type": op, "decision_authority": KX_DECISION_AUTHORITY,
    }
def _sar(v2id, child, eah, apv_id, kx_id, kx_hash, sre_id, sre_hash, tpath, pre_sha, post_sha, cand_sha, nbytes, op) -> dict:
    return {
        "schema_version": "V0", "sealed": True,
        "sealed_apply_receipt_id": _v2id("sar", v2id+child+tpath+post_sha),
        "created_at": _now(),
        "batch_execution_id": v2id, "child_execution_id": child,
        "execution_authority_hash": eah, "approval_id": apv_id,
        "kx108_pre_decision_record_id": kx_id,
        "kx108_pre_decision_record_hash": kx_hash,
        "sealed_rollback_evidence_id": sre_id,
        "sealed_rollback_evidence_hash": sre_hash,
        "target_path": tpath,
        "target_pre_sha256": pre_sha, "target_post_sha256": post_sha,
        "source_content_sha256": cand_sha,
        "bytes_written": nbytes,
        "source_kind": "V2_OPERATION", "source_identity": op,
        "operation_type": op, "status": "APPLIED",
        "decision_authority": KX_DECISION_AUTHORITY,
    }
def _rcpt(cap, op, status, sid="", **kw) -> dict:
    r = {
        "receipt_id": f"pcrcp-v2-{_sha16(cap+status+sid+_now())}",
        "capability": cap, "version": PC_CAPABILITY_V2_VERSION,
        "mode": PC_CAPABILITY_V2_MODE, "operation_type": op,
        "session_id": sid, "authority": "NONE",
        "decision_authority": KX_DECISION_AUTHORITY,
        "human_approval_required": True, "auto_execute": False,
        "jarvis_authority": JARVIS_AUTHORITY,
        "result_status": status, "timestamp_utc": _now(),
    }
    r.update(kw); return r
def _prep_rej(op, cap, reason, sid="") -> dict:
    return {"status": PREPARE_REJECTED, "j5_phase": "PREPARE",
            "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY,
            "execution_authority_hash": "", "reason": reason,
            "receipt": _rcpt(cap, op, PREPARE_REJECTED, sid, reason=reason)}
def _exec_rej(op, cap, reason, sid="") -> dict:
    return {"status": EXECUTE_REJECTED, "j5_phase": "EXECUTE",
            "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY,
            "reason": reason,
            "receipt": _rcpt(cap, op, EXECUTE_REJECTED, sid, reason=reason)}

# ============================================================
# GOVERNED_CREATE_FILE
# ============================================================
def pc_v2_create_file_prepare(
        target_path, content, *, execution_worktree_path,
        main_worktree_path, branch_name, base_sha, stores_base_dir, session_id=""):
    ew = Path(execution_worktree_path).resolve()
    mw = Path(main_worktree_path).resolve()
    st = _stores(stores_base_dir)
    if not _safe_rel(target_path): return _prep_rej(OP_CREATE_FILE, _CAP_CREATE_PREPARE, "TARGET_PATH_UNSAFE", session_id)
    ta = _canon(target_path, ew)
    if ta is None: return _prep_rej(OP_CREATE_FILE, _CAP_CREATE_PREPARE, "TARGET_PATH_TRAVERSAL", session_id)
    if ta.exists(): return _prep_rej(OP_CREATE_FILE, _CAP_CREATE_PREPARE, "TARGET_ALREADY_EXISTS", session_id)
    if not isinstance(content, (bytes, bytearray)): return _prep_rej(OP_CREATE_FILE, _CAP_CREATE_PREPARE, "CONTENT_MUST_BE_BYTES", session_id)
    iso = _check_isolation(ew, mw, branch_name, base_sha)
    if not iso["ok"]: return _prep_rej(OP_CREATE_FILE, _CAP_CREATE_PREPARE, "ISOLATION_FAILED:"+iso["reason"], session_id)
    cb = bytes(content); csha = _sha256(cb)
    desc = {"target_path": target_path, "candidate_sha256": csha, "target_pre_sha256": _EMPTY_SHA256,
            "target_expected_absent": True, "execution_worktree": str(ew),
            "branch_name": branch_name, "base_sha": base_sha, "session_id": session_id, "operation_type": OP_CREATE_FILE}
    eah = _eah(OP_CREATE_FILE, desc); child = _v2id("chd", eah+target_path); v2id = _v2id("v2x", eah+base_sha+session_id)
    mh = _sha16(json.dumps(desc, sort_keys=True)); dh = _persist_desc(v2id, OP_CREATE_FILE, eah, desc, st["v2exec"])
    (st["v2exec"] / (v2id+".candidate")).write_bytes(cb)
    return {"status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
            "operation_type": OP_CREATE_FILE, "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY, "execution_authority_hash": eah,
            "target_path": target_path, "candidate_sha256": csha, "target_pre_sha256": _EMPTY_SHA256,
            "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
            "_stores_base_dir": str(stores_base_dir),
            "receipt": _rcpt(_CAP_CREATE_PREPARE, OP_CREATE_FILE, PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                              execution_authority_hash=eah, target_path=target_path, candidate_sha256=csha)}

def pc_v2_create_file_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):
    st = _stores(stores_base_dir); ew = Path(repo_root).resolve()
    if prepared_result.get("j5_phase") != "PREPARE": return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip(): return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    tpath = prepared_result.get("target_path", ""); csha = prepared_result.get("candidate_sha256", "")
    v2id = prepared_result.get("v2_exec_id", ""); child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", ""); dh = prepared_result.get("desc_hash", "")
    desc = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    base_sha = desc["descriptor"]["base_sha"]
    cp = st["v2exec"] / (v2id+".candidate")
    if not cp.exists(): return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "CANDIDATE_BYTES_NOT_FOUND", session_id)
    cb = cp.read_bytes()
    if _sha256(cb) != csha: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "CANDIDATE_BYTES_CHANGED", session_id)
    ta = _canon(tpath, ew)
    if ta is None: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "TARGET_PATH_UNSAFE", session_id)
    if ta.exists(): return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "TARGET_EXISTS_PRECONDITION_FAILED", session_id)
    apr = _approval(v2id, child, exp_eah, csha); apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"): return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "APPROVAL_STORE_FAILED:"+ar.get("status",""), session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, base_sha, mh, [tpath], OP_CREATE_FILE, kxpre=st["kxpre"])
    if not kx.get("verify_ok"): return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", ""); kx_id = kx.get("decision_record_id", ""); kx_hash = kx.get("record", {}).get("decision_record_hash", "")
    if gate != "ALLOW": return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, "KX108_PRE_GATE:"+gate, session_id)
    if executor is not None:
        _ex = executor.create_file(ta, cb)
        if not _ex["ok"]:
            return _exec_rej(
                OP_CREATE_FILE,
                _CAP_CREATE_EXECUTE,
                "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")),
                session_id,
            )
    else:
        ta.parent.mkdir(parents=True, exist_ok=True)
        tmp = ta.parent / ("." + ta.name + "." + str(os.getpid()) + ".v2c.tmp")
        tmp.write_bytes(cb); os.replace(tmp, ta)
    after = ta.read_bytes(); asha = _sha256(after)
    if asha != csha: return _exec_rej(OP_CREATE_FILE, _CAP_CREATE_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    sre_rec = _sre(v2id, child, exp_eah, apv_id, kx_id, kx_hash, tpath, b"", csha, OP_CREATE_FILE)
    _SEV.store_sealed_rollback_evidence(sre_rec, st["sre"])
    sre_id = sre_rec["sealed_rollback_evidence_id"]
    sre_hash = _sha256(json.dumps(sre_rec, sort_keys=True, ensure_ascii=False).encode())
    sar_rec = _sar(v2id, child, exp_eah, apv_id, kx_id, kx_hash, sre_id, sre_hash, tpath, _EMPTY_SHA256, asha, csha, len(cb), OP_CREATE_FILE)
    _SEV.store_sealed_apply_receipt(sar_rec, st["sar"])
    return {"status": EXECUTED_OK, "j5_phase": "EXECUTE", "operation_type": OP_CREATE_FILE,
            "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True,
            "target_path": tpath, "target_post_sha256": asha,
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_rollback_evidence_id": sre_id,
            "executor_provider": executor.EXECUTOR_PROVIDER if executor else "OS_NATIVE",
            "executor_backend": executor.EXECUTOR_BACKEND if executor else "atomic_path_write",
            "receipt": _rcpt(_CAP_CREATE_EXECUTE, OP_CREATE_FILE, EXECUTED_OK, session_id,
                              kx108_pre_gate=gate, target_path=tpath, target_post_sha256=asha,
                              sealed_apply_receipt_id=sar_rec["sealed_apply_receipt_id"],
                              sealed_rollback_evidence_id=sre_id)}

# ============================================================
# GOVERNED_MOVE_FILE
# ============================================================
def pc_v2_move_file_prepare(
        source_path, dest_path, *, execution_worktree_path,
        main_worktree_path, branch_name, base_sha, stores_base_dir, session_id=""):
    ew = Path(execution_worktree_path).resolve(); mw = Path(main_worktree_path).resolve(); st = _stores(stores_base_dir)
    for lbl, rp in (("SOURCE", source_path), ("DEST", dest_path)):
        if not _safe_rel(rp): return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, lbl+"_PATH_UNSAFE", session_id)
    sa = _canon(source_path, ew); da = _canon(dest_path, ew)
    if sa is None: return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "SOURCE_PATH_TRAVERSAL", session_id)
    if da is None: return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "DEST_PATH_TRAVERSAL", session_id)
    if not sa.exists() or not sa.is_file(): return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "SOURCE_NOT_FOUND", session_id)
    if da.exists(): return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "DEST_ALREADY_EXISTS", session_id)
    if sa == da: return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "SOURCE_EQUALS_DEST", session_id)
    iso = _check_isolation(ew, mw, branch_name, base_sha)
    if not iso["ok"]: return _prep_rej(OP_MOVE_FILE, _CAP_MOVE_PREPARE, "ISOLATION_FAILED:"+iso["reason"], session_id)
    sb = sa.read_bytes(); ssha = _sha256(sb)
    desc = {"source_path": source_path, "dest_path": dest_path, "source_sha256": ssha,
            "dest_expected_absent": True, "execution_worktree": str(ew),
            "branch_name": branch_name, "base_sha": base_sha, "session_id": session_id, "operation_type": OP_MOVE_FILE}
    eah = _eah(OP_MOVE_FILE, desc); child = _v2id("chd", eah+source_path+dest_path); v2id = _v2id("v2x", eah+base_sha+session_id)
    mh = _sha16(json.dumps(desc, sort_keys=True)); dh = _persist_desc(v2id, OP_MOVE_FILE, eah, desc, st["v2exec"])
    return {"status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
            "operation_type": OP_MOVE_FILE, "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY, "execution_authority_hash": eah,
            "source_path": source_path, "dest_path": dest_path, "source_sha256": ssha,
            "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
            "_stores_base_dir": str(stores_base_dir),
            "receipt": _rcpt(_CAP_MOVE_PREPARE, OP_MOVE_FILE, PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                              execution_authority_hash=eah, source_path=source_path,
                              dest_path=dest_path, source_sha256=ssha)}
def pc_v2_move_file_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):
    st = _stores(stores_base_dir); ew = Path(repo_root).resolve()
    if prepared_result.get("j5_phase") != "PREPARE": return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip(): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    spath = prepared_result.get("source_path", ""); dpath = prepared_result.get("dest_path", "")
    exp_ss = prepared_result.get("source_sha256", ""); v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", ""); mh = prepared_result.get("manifest_hash", ""); dh = prepared_result.get("desc_hash", "")
    desc = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    base_sha = desc["descriptor"]["base_sha"]
    sa = _canon(spath, ew); da = _canon(dpath, ew)
    if sa is None or da is None: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "PATH_UNSAFE", session_id)
    if not sa.exists() or not sa.is_file(): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "SOURCE_GONE", session_id)
    if da.exists(): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "DEST_EXISTS_PRECONDITION_FAILED", session_id)
    sb = sa.read_bytes(); ssha = _sha256(sb)
    if ssha != exp_ss: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "SOURCE_CHANGED:"+ssha, session_id)
    apr = _approval(v2id, child, exp_eah, ssha); apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, base_sha, mh, [spath, dpath], OP_MOVE_FILE, kxpre=st["kxpre"])
    if not kx.get("verify_ok"): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", ""); kx_id = kx.get("decision_record_id", ""); kx_hash = kx.get("record", {}).get("decision_record_hash", "")
    if gate != "ALLOW": return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "KX108_PRE_GATE:"+gate, session_id)
    if executor is not None:
        _ex = executor.move_file(sa, da)
        if not _ex["ok"]:
            return _exec_rej(
                OP_MOVE_FILE,
                _CAP_MOVE_EXECUTE,
                "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")),
                session_id,
            )
    else:
        da.parent.mkdir(parents=True, exist_ok=True)
        os.replace(sa, da)
    if not da.exists() or sa.exists(): return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "MOVE_REALIZED_STATE_MISMATCH", session_id)
    asha = _sha256(da.read_bytes())
    if asha != ssha: return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE, "CONTENT_MISMATCH_AFTER_MOVE", session_id)
    sre_rec = _sre(v2id, child, exp_eah, apv_id, kx_id, kx_hash, dpath, sb, ssha, OP_MOVE_FILE)
    _SEV.store_sealed_rollback_evidence(sre_rec, st["sre"])
    sre_id = sre_rec["sealed_rollback_evidence_id"]
    sre_hash = _sha256(json.dumps(sre_rec, sort_keys=True, ensure_ascii=False).encode())
    sar_rec = _sar(v2id, child, exp_eah, apv_id, kx_id, kx_hash, sre_id, sre_hash, dpath, _EMPTY_SHA256, asha, ssha, len(sb), OP_MOVE_FILE)
    _SEV.store_sealed_apply_receipt(sar_rec, st["sar"])
    return {"status": EXECUTED_OK, "j5_phase": "EXECUTE", "operation_type": OP_MOVE_FILE,
            "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True,
            "source_path": spath, "dest_path": dpath,
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_rollback_evidence_id": sre_id,
            "executor_provider": executor.EXECUTOR_PROVIDER if executor else "OS_NATIVE",
            "executor_backend": executor.EXECUTOR_BACKEND if executor else "os.replace",
            "receipt": _rcpt(_CAP_MOVE_EXECUTE, OP_MOVE_FILE, EXECUTED_OK, session_id,
                              kx108_pre_gate=gate, source_path=spath, dest_path=dpath,
                              sealed_apply_receipt_id=sar_rec["sealed_apply_receipt_id"],
                              sealed_rollback_evidence_id=sre_id)}

# ============================================================
# GOVERNED_APPLY_PATCH
# ============================================================
def _parse_patch_targets(patch_content, ew):
    targets = []
    for line in patch_content.split("\n"):
        if line.startswith("+++ "):
            raw = line[4:].strip()
            if raw.startswith("b/"): raw = raw[2:]
            if raw in ("/dev/null", "dev/null"): return None, "PATCH_FILE_DELETION_NOT_ALLOWED"
            if not _safe_rel(raw): return None, "PATCH_TARGET_PATH_UNSAFE:"+repr(raw)
            if raw not in targets: targets.append(raw)
    if not targets: return None, "PATCH_NO_TARGETS"
    if len(targets) > _PATCH_MAX_FILES: return None, "PATCH_TOO_MANY_FILES:"+str(len(targets))
    return targets, None

def pc_v2_apply_patch_prepare(
        patch_content, *, execution_worktree_path,
        main_worktree_path, branch_name, base_sha, stores_base_dir, session_id=""):
    ew = Path(execution_worktree_path).resolve(); mw = Path(main_worktree_path).resolve(); st = _stores(stores_base_dir)
    if not isinstance(patch_content, str): return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "PATCH_MUST_BE_STR", session_id)
    pb = patch_content.encode("utf-8")
    if len(pb) > _PATCH_MAX_BYTES: return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "PATCH_TOO_LARGE", session_id)
    if "GIT binary patch" in patch_content or "Binary files" in patch_content:
        return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "BINARY_PATCH_NOT_ALLOWED", session_id)
    if not _UNIFIED_DIFF_HDR.search(patch_content):
        return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "PATCH_NOT_UNIFIED_DIFF", session_id)
    targets, err = _parse_patch_targets(patch_content, ew)
    if err: return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, err, session_id)
    iso = _check_isolation(ew, mw, branch_name, base_sha)
    if not iso["ok"]: return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "ISOLATION_FAILED:"+iso["reason"], session_id)
    before = {}
    for rel in targets:
        pa = _canon(rel, ew)
        if pa is None: return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "TARGET_PATH_TRAVERSAL:"+rel, session_id)
        if not pa.exists(): return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "TARGET_NOT_FOUND:"+rel, session_id)
        before[rel] = _sha256(pa.read_bytes())
    psha = _sha256(pb)
    tmp_patch = st["v2exec"] / ("patch_" + _sha16(base_sha + str(len(pb))) + ".diff")
    tmp_patch.write_bytes(patch_content.encode("utf-8"))
    chk = subprocess.run(["git", "apply", "--check", str(tmp_patch)],
                         cwd=str(ew), capture_output=True, text=True, timeout=30)
    if chk.returncode != 0:
        return _prep_rej(OP_APPLY_PATCH, _CAP_PATCH_PREPARE, "PATCH_DRY_RUN_FAILED:"+chk.stderr.strip()[:200], session_id)
    desc = {"patch_sha256": psha, "target_paths": sorted(targets), "before_digests": before,
            "execution_worktree": str(ew), "branch_name": branch_name, "base_sha": base_sha,
            "session_id": session_id, "operation_type": OP_APPLY_PATCH}
    eah = _eah(OP_APPLY_PATCH, desc); child = _v2id("chd", eah+psha); v2id = _v2id("v2x", eah+base_sha+session_id)
    mh = _sha16(json.dumps(desc, sort_keys=True))
    (st["v2exec"] / (v2id+".patch")).write_bytes(patch_content.encode("utf-8"))
    dh = _persist_desc(v2id, OP_APPLY_PATCH, eah, desc, st["v2exec"])
    return {"status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
            "operation_type": OP_APPLY_PATCH, "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY, "execution_authority_hash": eah,
            "patch_sha256": psha, "target_paths": sorted(targets), "before_digests": before,
            "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
            "_stores_base_dir": str(stores_base_dir),
            "receipt": _rcpt(_CAP_PATCH_PREPARE, OP_APPLY_PATCH, PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                              execution_authority_hash=eah, patch_sha256=psha, target_paths=sorted(targets))}

def pc_v2_apply_patch_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):
    st = _stores(stores_base_dir); ew = Path(repo_root).resolve()
    if prepared_result.get("j5_phase") != "PREPARE": return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip(): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    psha = prepared_result.get("patch_sha256", ""); targets = prepared_result.get("target_paths", [])
    before = prepared_result.get("before_digests", {}); v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", ""); mh = prepared_result.get("manifest_hash", ""); dh = prepared_result.get("desc_hash", "")
    desc = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    base_sha = desc["descriptor"]["base_sha"]
    pp = st["v2exec"] / (v2id+".patch")
    if not pp.exists(): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PATCH_CANDIDATE_NOT_FOUND", session_id)
    pt = pp.read_text("utf-8")
    if _sha256(pt.encode("utf-8")) != psha: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PATCH_MODIFIED_AFTER_PREPARE", session_id)
    for rel, exp_sha in before.items():
        pa = _canon(rel, ew)
        if pa is None or not pa.exists(): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "TARGET_GONE:"+rel, session_id)
        if _sha256(pa.read_bytes()) != exp_sha: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PRE_STATE_CHANGED:"+rel, session_id)
    before_bytes = {}
    for rel in targets:
        pa = _canon(rel, ew)
        if pa and pa.exists(): before_bytes[rel] = pa.read_bytes()
    apr = _approval(v2id, child, exp_eah, psha); apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, base_sha, mh, list(targets), OP_APPLY_PATCH, kxpre=st["kxpre"])
    if not kx.get("verify_ok"): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", ""); kx_id = kx.get("decision_record_id", ""); kx_hash = kx.get("record", {}).get("decision_record_hash", "")
    if gate != "ALLOW": return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "KX108_PRE_GATE:"+gate, session_id)
    if executor is not None:
        _ex = executor.apply_patch(ew, pt, list(targets))
        if not _ex["ok"]:
            return _exec_rej(
                OP_APPLY_PATCH,
                _CAP_PATCH_EXECUTE,
                "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")),
                session_id,
            )
    else:
        appl = subprocess.run(["git", "apply", str(pp)], cwd=str(ew), capture_output=True, text=True, timeout=60)
        if appl.returncode != 0: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PATCH_APPLY_FAILED:"+appl.stderr.strip()[:200], session_id)
    after = {}
    for rel in targets:
        pa = _canon(rel, ew)
        if pa is None or not pa.exists(): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "REALIZED_TARGET_MISSING:"+rel, session_id)
        after[rel] = _sha256(pa.read_bytes())
    sre_ids = []
    sre_records = []
    total_bytes = 0
    for rel in targets:
        bb = before_bytes.get(rel, b"")
        sre_r = _sre(v2id, child+"_"+_sha16(rel), exp_eah, apv_id, kx_id, kx_hash, rel, bb, psha, OP_APPLY_PATCH)
        store_result = _SEV.store_sealed_rollback_evidence(sre_r, st["sre"])
        if store_result.get("status") not in ("STORED", "IDEMPOTENT_EXISTING_IDENTICAL"):
            return _exec_rej(
                OP_APPLY_PATCH,
                _CAP_PATCH_EXECUTE,
                "ROLLBACK_EVIDENCE_STORE_FAILED:" + str(store_result.get("status", "")),
                session_id,
            )
        sre_records.append(sre_r)
        sre_ids.append(sre_r["sealed_rollback_evidence_id"])
        total_bytes += len(bb)
    p0 = targets[0]
    sre0 = sre_records[0]
    sre0_hash = _sha256(json.dumps(sre0, sort_keys=True, ensure_ascii=False).encode())
    sre0_id = sre0["sealed_rollback_evidence_id"]
    sar_rec = _sar(v2id, child, exp_eah, apv_id, kx_id, kx_hash, sre0_id, sre0_hash, p0,
                  before.get(p0, _EMPTY_SHA256), after.get(p0, ""), psha, total_bytes, OP_APPLY_PATCH)
    _SEV.store_sealed_apply_receipt(sar_rec, st["sar"])
    return {"status": EXECUTED_OK, "j5_phase": "EXECUTE", "operation_type": OP_APPLY_PATCH,
            "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True,
            "target_paths": targets, "after_digests": after,
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_rollback_evidence_ids": sre_ids,
            "executor_provider": executor.EXECUTOR_PROVIDER if executor else "OS_NATIVE",
            "executor_backend": executor.EXECUTOR_BACKEND if executor else "git.apply",
            "receipt": _rcpt(_CAP_PATCH_EXECUTE, OP_APPLY_PATCH, EXECUTED_OK, session_id,
                              kx108_pre_gate=gate, target_paths=targets, after_digests=after,
                              sealed_apply_receipt_id=sar_rec["sealed_apply_receipt_id"],
                              sealed_rollback_evidence_ids=sre_ids)}

# ====
# GOVERNED_CREATE_DIR
# ====
def pc_v2_create_dir_prepare(
        dir_path, *, execution_worktree_path, main_worktree_path,
        branch_name, base_sha, stores_base_dir, session_id=""):
    ew = Path(execution_worktree_path).resolve(); mw = Path(main_worktree_path).resolve()
    st = _stores(stores_base_dir)
    if not _safe_rel(dir_path): return _prep_rej(OP_CREATE_DIR, _CAP_CDIR_PREPARE, "DIR_PATH_UNSAFE", session_id)
    da = _canon(dir_path, ew)
    if da is None: return _prep_rej(OP_CREATE_DIR, _CAP_CDIR_PREPARE, "DIR_PATH_TRAVERSAL", session_id)
    if da.exists(): return _prep_rej(OP_CREATE_DIR, _CAP_CDIR_PREPARE, "DIR_ALREADY_EXISTS", session_id)
    iso = _check_isolation(ew, mw, branch_name, base_sha)
    if not iso["ok"]: return _prep_rej(OP_CREATE_DIR, _CAP_CDIR_PREPARE, "ISOLATION_FAILED:"+iso["reason"], session_id)
    desc = {"dir_path": dir_path, "execution_worktree": str(ew), "branch_name": branch_name,
            "base_sha": base_sha, "session_id": session_id, "operation_type": OP_CREATE_DIR}
    eah = _eah(OP_CREATE_DIR, desc); child = _v2id("chd", eah+dir_path); v2id = _v2id("v2x", eah+base_sha+session_id)
    mh = _sha16(json.dumps(desc, sort_keys=True)); dh = _persist_desc(v2id, OP_CREATE_DIR, eah, desc, st["v2exec"])
    return {"status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
            "operation_type": OP_CREATE_DIR, "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY, "execution_authority_hash": eah,
            "dir_path": dir_path, "v2_exec_id": v2id, "child_id": child,
            "manifest_hash": mh, "desc_hash": dh, "_stores_base_dir": str(stores_base_dir),
            "receipt": _rcpt(_CAP_CDIR_PREPARE, OP_CREATE_DIR, PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                              execution_authority_hash=eah, dir_path=dir_path)}

def pc_v2_create_dir_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):
    st = _stores(stores_base_dir); ew = Path(repo_root).resolve()
    if prepared_result.get("j5_phase") != "PREPARE": return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL: return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah: return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip(): return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    dpath = prepared_result.get("dir_path", ""); v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", ""); mh = prepared_result.get("manifest_hash", ""); dh = prepared_result.get("desc_hash", "")
    desc = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah: return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    base_sha = desc["descriptor"]["base_sha"]
    da = _canon(dpath, ew)
    if da is None: return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "DIR_PATH_UNSAFE", session_id)
    if da.exists(): return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "DIR_EXISTS_PRECONDITION_FAILED", session_id)
    apr = _approval(v2id, child, exp_eah, dpath); apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"): return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, base_sha, mh, [dpath], OP_CREATE_DIR, kxpre=st["kxpre"])
    if not kx.get("verify_ok"): return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW": return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "KX108_PRE_GATE:"+gate, session_id)
    if executor is not None:
        _ex = executor.create_dir(da)
        if not _ex["ok"]:
            return _exec_rej(
                OP_CREATE_DIR,
                _CAP_CDIR_EXECUTE,
                "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")),
                session_id,
            )
    else:
        da.mkdir(parents=False, exist_ok=False)
    if not da.exists() or not da.is_dir(): return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE, "CREATE_DIR_REALIZED_STATE_MISMATCH", session_id)
    return {"status": EXECUTED_OK, "j5_phase": "EXECUTE", "operation_type": OP_CREATE_DIR,
            "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True, "dir_path": dpath,
            "executor_provider": executor.EXECUTOR_PROVIDER if executor else "OS_NATIVE",
            "executor_backend": executor.EXECUTOR_BACKEND if executor else "os.replace",
            "receipt": _rcpt(_CAP_CDIR_EXECUTE, OP_CREATE_DIR, EXECUTED_OK, session_id,
                              kx108_pre_gate=gate, dir_path=dpath)}


# ============================
# Dispatcher + self-check
# ============================
def execute_pc_capability_v2(capability_id: str, **kwargs) -> dict:
    _dispatch = {
        _CAP_CREATE_PREPARE: pc_v2_create_file_prepare,
        _CAP_CREATE_EXECUTE: pc_v2_create_file_execute,
        _CAP_MOVE_PREPARE:   pc_v2_move_file_prepare,
        _CAP_MOVE_EXECUTE:   pc_v2_move_file_execute,
        _CAP_PATCH_PREPARE:  pc_v2_apply_patch_prepare,
        _CAP_PATCH_EXECUTE:  pc_v2_apply_patch_execute,
        _CAP_CDIR_PREPARE:   pc_v2_create_dir_prepare,
        _CAP_CDIR_EXECUTE:   pc_v2_create_dir_execute,
    }
    fn = _dispatch.get(capability_id)
    if fn is None: return {"status": "UNKNOWN_CAPABILITY_V2", "capability_id": capability_id, "known": list(_dispatch)}
    return fn(**kwargs)


def self_check_v2() -> dict:
    return {
        "version": PC_CAPABILITY_V2_VERSION,
        "mode": PC_CAPABILITY_V2_MODE,
        "is_execution_authority": PC_CAPABILITY_IS_EXECUTION_AUTHORITY,
        "is_kx_authority": PC_CAPABILITY_IS_KX_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "jarvis_authority": JARVIS_AUTHORITY,
        "human_approval_required": HUMAN_APPROVAL_REQUIRED,
        "auto_execute": AUTO_EXECUTE,
        "mutates_filesystem": MUTATES_FILESYSTEM,
        "accepts_arbitrary_shell": ACCEPTS_ARBITRARY_SHELL,
        "generic_shell_enabled": GENERIC_SHELL_ENABLED,
        "governed_delete_file": GOVERNED_DELETE_FILE_STATUS,
        "capabilities": list(_CAPABILITY_IDS_V2),
        "operations": [OP_CREATE_FILE, OP_MOVE_FILE, OP_APPLY_PATCH, OP_CREATE_DIR],
        "new_parallel_mutation_engine": False,
        "generic_write_file_enabled": False,
        "openjarvis_authority": JARVIS_AUTHORITY,
        "kx108_only": True,
    }
