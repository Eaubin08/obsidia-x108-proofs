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
OP_WINDOW_FOCUS             = "V2_WINDOW_FOCUS"
OP_APP_OPEN                 = "V2_APP_OPEN"
_CAP_CREATE_PREPARE = "PC_V2_CREATE_FILE_PREPARE"
_CAP_CREATE_EXECUTE = "PC_V2_CREATE_FILE_EXECUTE"
_CAP_MOVE_PREPARE   = "PC_V2_MOVE_FILE_PREPARE"
_CAP_MOVE_EXECUTE   = "PC_V2_MOVE_FILE_EXECUTE"
_CAP_PATCH_PREPARE  = "PC_V2_APPLY_PATCH_PREPARE"
_CAP_PATCH_EXECUTE  = "PC_V2_APPLY_PATCH_EXECUTE"
_CAP_CDIR_PREPARE   = "PC_V2_CREATE_DIR_PREPARE"
_CAP_CDIR_EXECUTE   = "PC_V2_CREATE_DIR_EXECUTE"
_CAP_WFOCUS_PREPARE = "PC_V2_WINDOW_FOCUS_PREPARE"
_CAP_WFOCUS_EXECUTE = "PC_V2_WINDOW_FOCUS_EXECUTE"
_CAP_AOPEN_PREPARE  = "PC_V2_APP_OPEN_PREPARE"
_CAP_AOPEN_EXECUTE  = "PC_V2_APP_OPEN_EXECUTE"
OP_UIA_SET_TEXT             = "V2_UIA_SET_TEXT"
_CAP_UTEXT_PREPARE  = "PC_V2_UIA_SET_TEXT_PREPARE"
_CAP_UTEXT_EXECUTE  = "PC_V2_UIA_SET_TEXT_EXECUTE"
_CAPABILITY_IDS_V2 = (_CAP_CREATE_PREPARE, _CAP_CREATE_EXECUTE, _CAP_MOVE_PREPARE, _CAP_MOVE_EXECUTE, _CAP_PATCH_PREPARE, _CAP_PATCH_EXECUTE, _CAP_CDIR_PREPARE, _CAP_CDIR_EXECUTE, _CAP_WFOCUS_PREPARE, _CAP_WFOCUS_EXECUTE, _CAP_AOPEN_PREPARE, _CAP_AOPEN_EXECUTE, _CAP_UTEXT_PREPARE, _CAP_UTEXT_EXECUTE)
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
def _kx108_pre(v2id, child, eah, apv_id, dh, base_sha, mhash, paths, op, *, kxpre,
               physical_state_anchor="", state_anchor_kind="GIT_HEAD") -> dict:
    xh = _sha256(json.dumps({"v2id":v2id,"child":child,"eah":eah,"apv":apv_id,"op":op}, sort_keys=True).encode())
    kwargs = {
        "session_id": child, "objective": f"V2 governed {op}",
        "base_sha": base_sha, "manifest_hash": mhash, "diff_hash": "",
        "physical_state_anchor": physical_state_anchor, "state_anchor_kind": state_anchor_kind,
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
        *, stores_base_dir, repo_root, session_id=""):
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
        *, stores_base_dir, repo_root, session_id=""):
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
    appl = subprocess.run(["git", "apply", str(pp)], cwd=str(ew), capture_output=True, text=True, timeout=60)
    if appl.returncode != 0: return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "PATCH_APPLY_FAILED:"+appl.stderr.strip()[:200], session_id)
    after = {}
    for rel in targets:
        pa = _canon(rel, ew)
        if pa is None or not pa.exists(): return _exec_rej(OP_APPLY_PATCH, _CAP_PATCH_EXECUTE, "REALIZED_TARGET_MISSING:"+rel, session_id)
        after[rel] = _sha256(pa.read_bytes())
    sre_ids = []
    total_bytes = 0
    for rel in targets:
        bb = before_bytes.get(rel, b"")
        sre_r = _sre(v2id, child+"_"+_sha16(rel), exp_eah, apv_id, kx_id, kx_hash, rel, bb, psha, OP_APPLY_PATCH)
        _SEV.store_sealed_rollback_evidence(sre_r, st["sre"])
        sre_ids.append(sre_r["sealed_rollback_evidence_id"]); total_bytes += len(bb)
    p0 = targets[0]; bb0 = before_bytes.get(p0, b"")
    sre0 = _sre(v2id, child+"_"+_sha16(p0), exp_eah, apv_id, kx_id, kx_hash, p0, bb0, psha, OP_APPLY_PATCH)
    sre0_hash = _sha256(json.dumps(sre0, sort_keys=True, ensure_ascii=False).encode())
    sre0_id = sre_ids[0] if sre_ids else sre0["sealed_rollback_evidence_id"]
    sar_rec = _sar(v2id, child, exp_eah, apv_id, kx_id, kx_hash, sre0_id, sre0_hash, p0,
                  before.get(p0, _EMPTY_SHA256), after.get(p0, ""), psha, total_bytes, OP_APPLY_PATCH)
    _SEV.store_sealed_apply_receipt(sar_rec, st["sar"])
    return {"status": EXECUTED_OK, "j5_phase": "EXECUTE", "operation_type": OP_APPLY_PATCH,
            "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True,
            "target_paths": targets, "after_digests": after,
            "sealed_apply_receipt_id": sar_rec["sealed_apply_receipt_id"],
            "sealed_rollback_evidence_ids": sre_ids,
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



# ====
# GOVERNED_WINDOW_FOCUS (G1-A)
# ====
def pc_v2_window_focus_prepare(
        title, *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(title, str) or not title.strip():
        return _prep_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_PREPARE, "TITLE_REQUIRED", session_id)
    title = title.strip()
    st = _stores(stores_base_dir)
    fw = executor.find_window(title)
    if not fw.get("ok"):
        return _prep_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(fw.get("error", "")), session_id)
    resolved_hwnd = int(fw["hwnd"])
    resolved_title = str(fw["title"])
    _psa_snapshot = {
        "anchor_schema": "WINDOW_FOCUS_PRE_STATE_V0",
        "operation": "WINDOW_FOCUS",
        "hwnd": resolved_hwnd,
        "title": resolved_title,
    }
    physical_state_anchor = _sha256(
        json.dumps(_psa_snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")
    )
    desc = {
        "requested_title": title,
        "resolved_hwnd": resolved_hwnd,
        "resolved_title": resolved_title,
        "session_id": session_id,
        "operation_type": OP_WINDOW_FOCUS,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_WINDOW_FOCUS, desc)
    child = _v2id("chd", eah + title + str(resolved_hwnd))
    v2id = _v2id("v2x", eah + session_id + "WINDOW_FOCUS")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_WINDOW_FOCUS, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_WINDOW_FOCUS, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "requested_title": title,
        "resolved_hwnd": resolved_hwnd, "resolved_title": resolved_title,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_WFOCUS_PREPARE, OP_WINDOW_FOCUS,
                         PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                         execution_authority_hash=eah,
                         requested_title=title,
                         resolved_hwnd=resolved_hwnd, resolved_title=resolved_title),
    }


def pc_v2_window_focus_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah:
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    resolved_hwnd = desc["descriptor"]["resolved_hwnd"]
    resolved_title = desc["descriptor"]["resolved_title"]
    requested_title = desc["descriptor"]["requested_title"]
    stored_psa = desc["descriptor"].get("physical_state_anchor", "")
    if stored_psa:
        _pre_obs = executor.find_window(resolved_title)
        if not _pre_obs.get("ok"):
            return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE,
                             "TARGET_IDENTITY_LOST:" + str(_pre_obs.get("error", "")), session_id)
        _cur_hwnd = int(_pre_obs.get("hwnd", 0))
        _cur_title = str(_pre_obs.get("title", ""))
        if _cur_hwnd != resolved_hwnd:
            return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE,
                             "TARGET_HWND_DRIFTED:expected=%d,got=%d" % (resolved_hwnd, _cur_hwnd), session_id)
        _cur_snap = {"anchor_schema": "WINDOW_FOCUS_PRE_STATE_V0", "operation": "WINDOW_FOCUS",
                     "hwnd": _cur_hwnd, "title": _cur_title}
        _cur_psa = _sha256(json.dumps(_cur_snap, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        if _cur_psa != stored_psa:
            return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE,
                             "PRE_STATE_DRIFTED:anchor_mismatch", session_id)
    cand_seed = requested_title + str(resolved_hwnd)
    apr = _approval(v2id, child, exp_eah, cand_seed)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    scope_id = "OS_WINDOW:" + resolved_title
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_WINDOW_FOCUS,
                    kxpre=st["kxpre"],
                    physical_state_anchor=stored_psa,
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    ex = executor.focus_window_by_hwnd(resolved_hwnd)
    if not ex.get("ok"):
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE,
                         "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error", "")), session_id)
    focused_hwnd = int(ex.get("hwnd", 0))
    focused_title = str(ex.get("title", resolved_title))
    vf = executor.verify_focus(focused_hwnd, resolved_title)
    if not vf.get("ok"):
        return _exec_rej(OP_WINDOW_FOCUS, _CAP_WFOCUS_EXECUTE,
                         "REALIZED_STATE_MISMATCH:" + str(vf.get("error", "")), session_id)
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_WINDOW_FOCUS,
        "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "requested_title": requested_title,
        "focused_hwnd": focused_hwnd, "focused_title": focused_title,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "window.focus",
        "receipt": _rcpt(_CAP_WFOCUS_EXECUTE, OP_WINDOW_FOCUS, EXECUTED_OK, session_id,
                         kx108_pre_gate=gate,
                         requested_title=requested_title,
                         focused_hwnd=focused_hwnd, focused_title=focused_title,
                         executor_provider=executor.EXECUTOR_PROVIDER,
                         executor_backend=executor.EXECUTOR_BACKEND,
                         executor_capability="window.focus"),
    }


# ============================================================
# GOVERNED_APP_OPEN  (G1-B)
# ============================================================

def _is_pid_alive(pid: int) -> bool:
    try:
        import ctypes, ctypes.wintypes
        PROCESS_QUERY_INFORMATION = 0x0400
        STILL_ACTIVE = 259
        h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if not h:
            return False
        code = ctypes.wintypes.DWORD()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return bool(ok) and code.value == STILL_ACTIVE
    except Exception:
        return False


def pc_v2_app_open_prepare(app, *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_APP_OPEN, _CAP_AOPEN_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(app, str) or not app.strip():
        return _prep_rej(OP_APP_OPEN, _CAP_AOPEN_PREPARE, "APP_REQUIRED", session_id)
    app = app.strip()
    st = _stores(stores_base_dir)
    inv = executor.resolve_app(app)
    if not inv.get("ok"):
        return _prep_rej(OP_APP_OPEN, _CAP_AOPEN_PREPARE,
                         "APP_NOT_IN_INVENTORY:" + str(inv.get("error", "")), session_id)
    resolved_name   = inv["name"]
    resolved_target = inv["target"]
    resolved_source = inv["source"]
    _psa_snapshot = {
        "anchor_schema": "APP_OPEN_PRE_STATE_V0",
        "requested_app": app,
        "resolved_target": resolved_target,
        "resolved_source": resolved_source,
        "target_is_file": os.path.isfile(resolved_target),
    }
    physical_state_anchor = _sha256(
        json.dumps(_psa_snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")
    )
    desc = {
        "requested_app": app,
        "resolved_name": resolved_name,
        "resolved_target": resolved_target,
        "resolved_source": resolved_source,
        "session_id": session_id,
        "operation_type": OP_APP_OPEN,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_APP_OPEN, desc)
    child = _v2id("chd", eah + app + resolved_target)
    v2id  = _v2id("v2x", eah + session_id + "APP_OPEN")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_APP_OPEN, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_APP_OPEN, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "requested_app": app,
        "resolved_name": resolved_name,
        "resolved_target": resolved_target,
        "resolved_source": resolved_source,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_AOPEN_PREPARE, OP_APP_OPEN,
                         PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                         execution_authority_hash=eah,
                         requested_app=app,
                         resolved_target=resolved_target,
                         resolved_source=resolved_source,
                         physical_state_anchor=physical_state_anchor),
    }



def pc_v2_app_open_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    requested_app   = desc["descriptor"]["requested_app"]
    resolved_target = desc["descriptor"]["resolved_target"]
    resolved_source = desc["descriptor"]["resolved_source"]
    stored_psa      = desc["descriptor"].get("physical_state_anchor", "")
    cur_inv = executor.resolve_app(requested_app)
    if not cur_inv.get("ok"):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "APP_NOT_IN_INVENTORY:" + str(cur_inv.get("error", "")), session_id)
    if cur_inv["target"] != resolved_target:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "INVENTORY_DRIFT_DETECTED:target_changed", session_id)
    if stored_psa:
        _cur_snap = {
            "anchor_schema": "APP_OPEN_PRE_STATE_V0",
            "requested_app": requested_app,
            "resolved_target": cur_inv["target"],
            "resolved_source": cur_inv["source"],
            "target_is_file": os.path.isfile(cur_inv["target"]),
        }
        _cur_psa = _sha256(json.dumps(_cur_snap, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        if _cur_psa != stored_psa:
            return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                             "PRE_STATE_DRIFTED:anchor_mismatch", session_id)
    cand_seed = requested_app + resolved_target
    apr   = _approval(v2id, child, exp_eah, cand_seed)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    scope_id = "OS_APP:" + resolved_target
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_APP_OPEN,
                    kxpre=st["kxpre"],
                    physical_state_anchor=stored_psa,
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate  = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    if resolved_target.casefold().endswith(".lnk"):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "LNK_DEFERRED:NO_REALIZED_STATE_PROOF", session_id)
    ex = executor.open_app_by_target(resolved_target)
    if not ex.get("ok"):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error", "")), session_id)
    pid = ex.get("pid")
    if pid is None:
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "REALIZED_STATE_MISMATCH:PID_NONE", session_id)
    if not _is_pid_alive(pid):
        return _exec_rej(OP_APP_OPEN, _CAP_AOPEN_EXECUTE,
                         "REALIZED_STATE_MISMATCH:PID_NOT_ALIVE", session_id)
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_APP_OPEN,
        "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "requested_app": requested_app,
        "resolved_target": resolved_target, "resolved_source": resolved_source,
        "launched_pid": pid,
        "pid_verified": True,
        "proof_strength": "STRONG",
        "lnk_policy": "NOT_APPLICABLE",
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "app.open",
        "receipt": _rcpt(_CAP_AOPEN_EXECUTE, OP_APP_OPEN, EXECUTED_OK, session_id,
                         kx108_pre_gate=gate,
                         requested_app=requested_app,
                         resolved_target=resolved_target, resolved_source=resolved_source,
                         launched_pid=pid, pid_verified=True,
                         proof_strength="STRONG",
                         executor_provider=executor.EXECUTOR_PROVIDER,
                         executor_backend=executor.EXECUTOR_BACKEND,
                         executor_capability="app.open"),
    }


# ============================
# G2-A: UIA set_text governed
# ============================
_EDIT_CLASS_NAMES = frozenset({"Edit", "RichEdit20W", "RichEdit20A",
                               "RichTextBox", "TMemo", "TEdit"})


def _find_edit_control(controls, control_name):
    matches = [c for c in controls
               if c.get("name") == control_name
               and c.get("class_name", "") in _EDIT_CLASS_NAMES]
    if len(matches) == 1:
        return matches[0]
    return None


def pc_v2_uia_set_text_prepare(
        window_title, control_name, target_value,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(window_title, str) or not window_title.strip():
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "WINDOW_TITLE_REQUIRED", session_id)
    if not isinstance(control_name, str) or not control_name.strip():
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_NAME_REQUIRED", session_id)
    if not isinstance(target_value, str):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "TARGET_VALUE_REQUIRED", session_id)
    window_title = window_title.strip()
    control_name = control_name.strip()
    st = _stores(stores_base_dir)
    ctrl_list = executor.list_controls(window_title)
    if not ctrl_list.get("ok"):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(ctrl_list.get("error", "")), session_id)
    controls = ctrl_list.get("controls", [])
    ctrl = _find_edit_control(controls, control_name)
    if ctrl is None:
        multi = [c for c in controls if c.get("name") == control_name]
        if len(multi) > 1:
            return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_AMBIGUOUS", session_id)
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_NOT_FOUND", session_id)
    if not ctrl.get("enabled", False):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_DISABLED", session_id)
    if not ctrl.get("visible", False):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_NOT_VISIBLE", session_id)
    pre_read = executor.read_text(window_title, control_name)
    if not pre_read.get("ok"):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE,
                         "PRE_VALUE_READ_FAILED:" + str(pre_read.get("error", "")), session_id)
    pre_value     = pre_read.get("text", "")
    class_name    = ctrl.get("class_name", "")
    automation_id = ctrl.get("automation_id", "")
    bounds        = ctrl.get("bounds", {})
    _psa_snapshot = {
        "anchor_schema": "UIA_SET_TEXT_PRE_STATE_V0",
        "window_title": window_title,
        "control_name": control_name,
        "class_name": class_name,
        "automation_id": automation_id,
        "bounds": bounds,
        "enabled": ctrl.get("enabled", False),
        "visible": ctrl.get("visible", False),
        "pre_value": pre_value,
        "target_value": target_value,
    }
    physical_state_anchor = _sha256(
        json.dumps(_psa_snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")
    )
    desc = {
        "window_title": window_title,
        "control_name": control_name,
        "class_name": class_name,
        "automation_id": automation_id,
        "bounds": bounds,
        "target_value": target_value,
        "pre_value": pre_value,
        "session_id": session_id,
        "operation_type": OP_UIA_SET_TEXT,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_UIA_SET_TEXT, desc)
    child = _v2id("chd", eah + window_title + control_name + target_value)
    v2id  = _v2id("v2x", eah + session_id + "UIA_SET_TEXT")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_UIA_SET_TEXT, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_UIA_SET_TEXT, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "window_title": window_title,
        "control_name": control_name,
        "class_name": class_name,
        "automation_id": automation_id,
        "target_value": target_value,
        "pre_value": pre_value,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_UTEXT_PREPARE, OP_UIA_SET_TEXT,
                         PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                         execution_authority_hash=eah,
                         window_title=window_title, control_name=control_name,
                         class_name=class_name, automation_id=automation_id,
                         target_value=target_value, pre_value=pre_value,
                         physical_state_anchor=physical_state_anchor),
    }


def pc_v2_uia_set_text_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    if not desc or desc.get("eah") != exp_eah:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d             = desc["descriptor"]
    window_title  = d["window_title"]
    control_name  = d["control_name"]
    target_value  = d["target_value"]
    stored_psa    = d.get("physical_state_anchor", "")
    stored_aid    = d.get("automation_id", "")
    stored_cls    = d.get("class_name", "")
    stored_pre    = d.get("pre_value", "")
    ctrl_list = executor.list_controls(window_title)
    if not ctrl_list.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "WINDOW_NOT_FOUND:" + str(ctrl_list.get("error", "")), session_id)
    cur_ctrl = _find_edit_control(ctrl_list.get("controls", []), control_name)
    if cur_ctrl is None:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "CONTROL_NOT_FOUND", session_id)
    cur_aid = cur_ctrl.get("automation_id", "")
    if stored_aid and cur_aid and stored_aid != cur_aid:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "CONTROL_IDENTITY_DRIFTED:automation_id_changed", session_id)
    if stored_cls and cur_ctrl.get("class_name", "") != stored_cls:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "CONTROL_IDENTITY_DRIFTED:class_name_changed", session_id)
    cur_pre = executor.read_text(window_title, control_name)
    if not cur_pre.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "PRE_VALUE_READ_FAILED:" + str(cur_pre.get("error", "")), session_id)
    if cur_pre.get("text", "") != stored_pre:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "PRE_VALUE_DRIFTED", session_id)
    cand_seed = window_title + control_name + target_value
    apr    = _approval(v2id, child, exp_eah, cand_seed)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    scope_id = "UIA_CONTROL:" + window_title + ":" + control_name
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_UIA_SET_TEXT,
                    kxpre=st["kxpre"],
                    physical_state_anchor=stored_psa,
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "KX108_PRE_GATE:" + gate, session_id)
    ex = executor.set_text(window_title, control_name, target_value)
    if not ex.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "EXECUTOR_ERROR:" + str(ex.get("error", "")), session_id)
    post_read = executor.read_text(window_title, control_name)
    if not post_read.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "POST_VALUE_READ_FAILED:" + str(post_read.get("error", "")), session_id)
    post_value = post_read.get("text", "")
    if post_value != target_value:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "REALIZED_STATE_MISMATCH:post_value_differs", session_id)
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_UIA_SET_TEXT,
        "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "window_title": window_title, "control_name": control_name,
        "target_value": target_value, "pre_value": stored_pre, "post_value": post_value,
        "proof_strength": "STRONG", "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "control.set_text",
        "receipt": _rcpt(_CAP_UTEXT_EXECUTE, OP_UIA_SET_TEXT, EXECUTED_OK, session_id,
                         kx108_pre_gate=gate,
                         window_title=window_title, control_name=control_name,
                         target_value=target_value, pre_value=stored_pre,
                         post_value=post_value, proof_strength="STRONG",
                         realized_state_verified=True,
                         executor_provider=executor.EXECUTOR_PROVIDER,
                         executor_backend=executor.EXECUTOR_BACKEND,
                         executor_capability="control.set_text"),
    }





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
        _CAP_WFOCUS_PREPARE: pc_v2_window_focus_prepare,
        _CAP_WFOCUS_EXECUTE: pc_v2_window_focus_execute,
        _CAP_AOPEN_PREPARE:  pc_v2_app_open_prepare,
        _CAP_AOPEN_EXECUTE:  pc_v2_app_open_execute,
        _CAP_UTEXT_PREPARE:  pc_v2_uia_set_text_prepare,
        _CAP_UTEXT_EXECUTE:  pc_v2_uia_set_text_execute,
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
        "operations": [OP_CREATE_FILE, OP_MOVE_FILE, OP_APPLY_PATCH, OP_CREATE_DIR, OP_WINDOW_FOCUS, OP_APP_OPEN, OP_UIA_SET_TEXT],
        "new_parallel_mutation_engine": False,
        "generic_write_file_enabled": False,
        "openjarvis_authority": JARVIS_AUTHORITY,
        "kx108_only": True,
    }
