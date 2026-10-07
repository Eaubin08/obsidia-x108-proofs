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
OP_AUDIO_VOLUME             = "V2_AUDIO_VOLUME"
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
_CAP_AVOL_PREPARE   = "PC_V2_AUDIO_VOLUME_PREPARE"
_CAP_AVOL_EXECUTE   = "PC_V2_AUDIO_VOLUME_EXECUTE"
OP_UIA_SET_TEXT             = "V2_UIA_SET_TEXT"
_CAP_UTEXT_PREPARE  = "PC_V2_UIA_SET_TEXT_PREPARE"
_CAP_UTEXT_EXECUTE  = "PC_V2_UIA_SET_TEXT_EXECUTE"
_CAP_SCHK_PREPARE   = "PC_V2_UIA_SET_CHECKED_PREPARE"
_CAP_SCHK_EXECUTE   = "PC_V2_UIA_SET_CHECKED_EXECUTE"
_CAP_SRAD_PREPARE   = "PC_V2_UIA_SELECT_RADIO_PREPARE"
_CAP_SRAD_EXECUTE   = "PC_V2_UIA_SELECT_RADIO_EXECUTE"
OP_UIA_SELECT_RADIO = "V2_UIA_SELECT_RADIO"
OP_UIA_SELECT_TAB   = "V2_UIA_SELECT_TAB"
_CAP_STAB_PREPARE   = "PC_V2_UIA_SELECT_TAB_PREPARE"
_CAP_STAB_EXECUTE   = "PC_V2_UIA_SELECT_TAB_EXECUTE"
OP_BROWSER_NAVIGATE = "V2_BROWSER_NAVIGATE"
_CAP_BNAV_PREPARE   = "PC_V2_BROWSER_NAVIGATE_PREPARE"
_CAP_BNAV_EXECUTE   = "PC_V2_BROWSER_NAVIGATE_EXECUTE"

OP_BROWSER_READ    = "V2_BROWSER_READ"
_CAP_BRAD_PREPARE  = "PC_V2_BROWSER_READ_PREPARE"
_CAP_BRAD_EXECUTE  = "PC_V2_BROWSER_READ_EXECUTE"

OP_BROWSER_ACTIVATE_LINK = "V2_BROWSER_ACTIVATE_LINK"
_CAP_BLINK_PREPARE = "PC_V2_BROWSER_ACTIVATE_LINK_PREPARE"
_CAP_BLINK_EXECUTE = "PC_V2_BROWSER_ACTIVATE_LINK_EXECUTE"

OP_BROWSER_SET_DISCLOSURE = "V2_BROWSER_SET_DISCLOSURE"
_CAP_BDISC_PREPARE = "PC_V2_BROWSER_SET_DISCLOSURE_PREPARE"
_CAP_BDISC_EXECUTE = "PC_V2_BROWSER_SET_DISCLOSURE_EXECUTE"

OP_BROWSER_SET_CHECKED = "V2_BROWSER_SET_CHECKED"
_CAP_BCHK_PREPARE = "PC_V2_BROWSER_SET_CHECKED_PREPARE"
_CAP_BCHK_EXECUTE = "PC_V2_BROWSER_SET_CHECKED_EXECUTE"

OP_BROWSER_SELECT_RADIO = "V2_BROWSER_SELECT_RADIO"
_CAP_BRDO_PREPARE = "PC_V2_BROWSER_SELECT_RADIO_PREPARE"
_CAP_BRDO_EXECUTE = "PC_V2_BROWSER_SELECT_RADIO_EXECUTE"

OP_BROWSER_SELECT_OPTION = "V2_BROWSER_SELECT_OPTION"
_CAP_BOPT_PREPARE = "PC_V2_BROWSER_SELECT_OPTION_PREPARE"
_CAP_BOPT_EXECUTE = "PC_V2_BROWSER_SELECT_OPTION_EXECUTE"

OP_BROWSER_SET_FIELD_VALUE = "V2_BROWSER_SET_FIELD_VALUE"
_CAP_BFLD_PREPARE = "PC_V2_BROWSER_SET_FIELD_VALUE_PREPARE"
_CAP_BFLD_EXECUTE = "PC_V2_BROWSER_SET_FIELD_VALUE_EXECUTE"

_SENSITIVE_SELECTOR_PATTERNS = (
    "type=password", 'type="password"', "type=hidden", 'type="hidden"',
)

def _is_sensitive_selector(selector: str) -> bool:
    sl = selector.lower().replace(" ", "")
    return any(p.replace(" ", "") in sl for p in _SENSITIVE_SELECTOR_PATTERNS)
OP_UIA_SET_CHECKED  = "V2_UIA_SET_CHECKED"
_CAPABILITY_IDS_V2 = (_CAP_CREATE_PREPARE, _CAP_CREATE_EXECUTE, _CAP_MOVE_PREPARE, _CAP_MOVE_EXECUTE, _CAP_PATCH_PREPARE, _CAP_PATCH_EXECUTE, _CAP_CDIR_PREPARE, _CAP_CDIR_EXECUTE, _CAP_WFOCUS_PREPARE, _CAP_WFOCUS_EXECUTE, _CAP_AOPEN_PREPARE, _CAP_AOPEN_EXECUTE, _CAP_AVOL_PREPARE, _CAP_AVOL_EXECUTE, _CAP_UTEXT_PREPARE, _CAP_UTEXT_EXECUTE, _CAP_SCHK_PREPARE, _CAP_SCHK_EXECUTE, _CAP_SRAD_PREPARE, _CAP_SRAD_EXECUTE, _CAP_STAB_PREPARE, _CAP_STAB_EXECUTE, _CAP_BNAV_PREPARE, _CAP_BNAV_EXECUTE, _CAP_BRAD_PREPARE, _CAP_BRAD_EXECUTE, _CAP_BLINK_PREPARE, _CAP_BLINK_EXECUTE, _CAP_BDISC_PREPARE, _CAP_BDISC_EXECUTE, _CAP_BCHK_PREPARE, _CAP_BCHK_EXECUTE, _CAP_BRDO_PREPARE, _CAP_BRDO_EXECUTE, _CAP_BOPT_PREPARE, _CAP_BOPT_EXECUTE, _CAP_BFLD_PREPARE, _CAP_BFLD_EXECUTE)
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
# G2-A-R: the governed target is a stable UIA identity (JarJar G2-0), never a window
# title / control name (an Edit's name IS its mutable content). Values are only hashed in
# anchors and receipts; the exact target text lives only in the persisted descriptor.
_UIA_TEXT_CONTROL_TYPES = frozenset({"Edit", "Document"})
_UIA_IDENTITY_PRIMARY = ("window_hwnd", "process_id", "runtime_id")
_UIA_IDENTITY_GUARDS = ("native_handle", "automation_id", "control_type", "class_name",
                        "framework_id", "parent_runtime_id")


def _sha256_text(text: str) -> str:
    return _sha256(text.encode("utf-8"))


def _uia_identity_ok(identity) -> bool:
    if not isinstance(identity, dict):
        return False
    hwnd, pid, rid = identity.get("window_hwnd"), identity.get("process_id"), identity.get("runtime_id")
    return (isinstance(hwnd, int) and hwnd > 0 and isinstance(pid, int) and pid > 0
            and isinstance(rid, list) and len(rid) > 0 and all(isinstance(x, int) for x in rid))


def _uia_identity_matches(bound: dict, live: dict) -> bool:
    """Exact: every primary field equal, every bound (non-empty) guard equal. No fuzzy match."""
    if any(bound.get(k) != live.get(k) for k in _UIA_IDENTITY_PRIMARY):
        return False
    return all(live.get(k) == bound.get(k) for k in _UIA_IDENTITY_GUARDS if bound.get(k))


def _uia_scope_id(identity: dict) -> str:
    rid = ".".join(str(x) for x in identity["runtime_id"])
    return "UIA_CONTROL:%d:%d:%s" % (identity["window_hwnd"], identity["process_id"], rid)


def _uia_pre_state(identity: dict, control: dict, pre_value_sha256: str) -> tuple[dict, str]:
    """PHYSICAL_PRE_STATE V1: observed pre-state only (never the target value)."""
    snapshot = {
        "anchor_schema": "UIA_SET_TEXT_PRE_STATE_V1",
        "identity": {k: identity.get(k) for k in _UIA_IDENTITY_PRIMARY + _UIA_IDENTITY_GUARDS},
        "enabled": bool(control.get("enabled")),
        "is_password": bool(control.get("is_password")),
        "is_read_only": control.get("is_read_only"),
        "pre_value_sha256": pre_value_sha256,
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _uia_writable_reason(control: dict):
    ident = control.get("identity", {})
    if ident.get("control_type") not in _UIA_TEXT_CONTROL_TYPES:
        return "UNSUPPORTED_CONTROL_TYPE"
    if control.get("is_password"):
        return "PASSWORD_FIELD_REJECTED"
    if control.get("is_read_only") is None or "value" not in (control.get("patterns") or []):
        return "VALUE_PATTERN_REQUIRED"
    if control.get("is_read_only"):
        return "READONLY_FIELD_REJECTED"
    if not control.get("enabled", False):
        return "CONTROL_DISABLED"
    return None


def pc_v2_uia_set_text_prepare(
        window_hwnd, target_identity, target_value,
        *, stores_base_dir, session_id="", executor=None, window_title="", control_label=""):
    if executor is None:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(window_hwnd, int) or isinstance(window_hwnd, bool) or window_hwnd <= 0:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "WINDOW_HWND_REQUIRED", session_id)
    if not _uia_identity_ok(target_identity) or target_identity.get("window_hwnd") != window_hwnd:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "STABLE_TARGET_IDENTITY_REQUIRED", session_id)
    if not isinstance(target_value, str):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "TARGET_VALUE_REQUIRED", session_id)
    st = _stores(stores_base_dir)
    listing = executor.list_controls_uia(window_hwnd)
    if not listing.get("ok"):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(listing.get("error", "")), session_id)
    matches = [c for c in listing.get("controls", [])
               if c.get("identity", {}).get("runtime_id") == target_identity["runtime_id"]]
    if not matches:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_NOT_FOUND", session_id)
    if len(matches) > 1:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_AMBIGUOUS", session_id)
    control = matches[0]
    identity = dict(control["identity"])
    if not _uia_identity_ok(identity) or not _uia_identity_matches(target_identity, identity):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, "CONTROL_IDENTITY_MISMATCH", session_id)
    reason = _uia_writable_reason(control)
    if reason:
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE, reason, session_id)
    pre = executor.read_value_by_identity(identity)
    if not pre.get("ok") or not pre.get("value_sha256"):
        return _prep_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_PREPARE,
                         "PRE_VALUE_READ_FAILED:" + str(pre.get("error", "")), session_id)
    pre_hash = pre["value_sha256"]
    target_hash = _sha256_text(target_value)
    _, physical_state_anchor = _uia_pre_state(identity, control, pre_hash)
    desc = {
        "operation_type": OP_UIA_SET_TEXT,
        "target_identity": identity,
        "target_value": target_value,          # exact text: persisted descriptor only
        "target_value_sha256": target_hash,
        "window_title": window_title,          # display / provenance only
        "control_label": control_label,        # display / provenance only
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_UIA_SET_TEXT, desc)
    scope = _uia_scope_id(identity)
    child = _v2id("chd", eah + scope + target_hash)
    v2id  = _v2id("v2x", eah + session_id + "UIA_SET_TEXT")
    mh    = _sha16(json.dumps({k: v for k, v in desc.items() if k != "target_value"}, sort_keys=True))
    dh    = _persist_desc(v2id, OP_UIA_SET_TEXT, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_UIA_SET_TEXT, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "target_identity": identity, "scope_id": scope,
        "window_title": window_title, "control_label": control_label,
        "target_value_sha256": target_hash, "pre_value_sha256": pre_hash,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_UTEXT_PREPARE, OP_UIA_SET_TEXT,
                         PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                         execution_authority_hash=eah, target_identity=identity, scope_id=scope,
                         target_value_sha256=target_hash, pre_value_sha256=pre_hash,
                         physical_state_anchor=physical_state_anchor,
                         state_anchor_kind="PHYSICAL_PRE_STATE"),
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
    if not desc or desc.get("eah") != exp_eah or _eah(OP_UIA_SET_TEXT, desc.get("descriptor", {})) != exp_eah:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d            = desc["descriptor"]
    identity     = d.get("target_identity")
    target_value = d.get("target_value")
    target_hash  = d.get("target_value_sha256", "")
    stored_psa   = d.get("physical_state_anchor", "")
    if not _uia_identity_ok(identity) or not isinstance(target_value, str) \
            or _sha256_text(target_value) != target_hash:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "DESCRIPTOR_INVALID", session_id)
    # TOCTOU: reacquire ONLY the prepared identity (no title / name / class fallback)
    found = executor.find_control_by_identity(identity)
    if not found.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "TARGET_IDENTITY_NOT_REACQUIRED:" + str(found.get("error", "")), session_id)
    if not _uia_identity_matches(identity, found.get("identity", {})):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "CONTROL_IDENTITY_DRIFTED", session_id)
    reason = _uia_writable_reason(found)
    if reason:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, reason, session_id)
    pre = executor.read_value_by_identity(identity)
    if not pre.get("ok") or not pre.get("value_sha256"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "PRE_VALUE_READ_FAILED:" + str(pre.get("error", "")), session_id)
    _, current_psa = _uia_pre_state(identity, found, pre["value_sha256"])
    if current_psa != stored_psa:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _uia_scope_id(identity)
    apr    = _approval(v2id, child, exp_eah, scope_id + target_hash)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
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
    ex = executor.set_text_by_identity(identity, target_value)
    if not ex.get("ok"):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE,
                         "EXECUTOR_ERROR:" + str(ex.get("error", "")), session_id)
    if ex.get("value_match") is not True or ex.get("readback_text_sha256") != target_hash \
            or ex.get("requested_text_sha256") != target_hash \
            or not _uia_identity_matches(identity, ex.get("target_identity") or {}):
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
    # independent post-write observation of the SAME identity (executor success is not proof)
    post = executor.read_value_by_identity(identity)
    if not post.get("ok") or post.get("value_sha256") != target_hash:
        return _exec_rej(OP_UIA_SET_TEXT, _CAP_UTEXT_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_UIA_SET_TEXT,
        "jarvis_authority": JARVIS_AUTHORITY, "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "target_identity": identity, "scope_id": scope_id,
        "target_value_sha256": target_hash, "pre_value_sha256": pre["value_sha256"],
        "readback_value_sha256": post["value_sha256"],
        "proof_strength": "STRONG", "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "control.set_text_by_identity",
        "receipt": _rcpt(_CAP_UTEXT_EXECUTE, OP_UIA_SET_TEXT, EXECUTED_OK, session_id,
                         kx108_pre_gate=gate, target_identity=identity, scope_id=scope_id,
                         target_value_sha256=target_hash, pre_value_sha256=pre["value_sha256"],
                         readback_value_sha256=post["value_sha256"], proof_strength="STRONG",
                         realized_state_verified=True,
                         physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE",
                         executor_provider=executor.EXECUTOR_PROVIDER,
                         executor_backend=executor.EXECUTOR_BACKEND,
                         executor_capability="control.set_text_by_identity"),
    }



def _uia_pre_state_checked(identity: dict, toggle_state: int, enabled: bool):
    # Observed pre-state only: the target state is intent and lives in the EAH, never in the PSA.
    snapshot = {
        "anchor_schema": "UIA_SET_CHECKED_PRE_STATE_V0",
        "identity": {k: identity.get(k) for k in _UIA_IDENTITY_PRIMARY + _UIA_IDENTITY_GUARDS},
        "enabled": bool(enabled),
        "pre_toggle_state": int(toggle_state),
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


_UIA_CHECKBOX_PATTERN = "toggle"


def pc_v2_uia_set_checked_prepare(
        window_hwnd, target_identity, target_checked,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(window_hwnd, int) or isinstance(window_hwnd, bool) or window_hwnd <= 0:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "WINDOW_HWND_REQUIRED", session_id)
    if not _uia_identity_ok(target_identity) or target_identity.get("window_hwnd") != window_hwnd:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "STABLE_TARGET_IDENTITY_REQUIRED", session_id)
    if not isinstance(target_checked, bool):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "TARGET_CHECKED_MUST_BE_BOOL", session_id)
    st = _stores(stores_base_dir)
    listing = executor.list_controls_uia(window_hwnd)
    if not listing.get("ok"):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(listing.get("error", "")), session_id)
    matches = [c for c in listing.get("controls", [])
               if c.get("identity", {}).get("runtime_id") == target_identity["runtime_id"]]
    if not matches:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "CONTROL_NOT_FOUND", session_id)
    if len(matches) > 1:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "CONTROL_AMBIGUOUS", session_id)
    ctrl = matches[0]
    identity = dict(ctrl["identity"])
    if not _uia_identity_ok(identity) or not _uia_identity_matches(target_identity, identity):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "CONTROL_IDENTITY_MISMATCH", session_id)
    if identity.get("control_type") != "CheckBox":
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "UNSUPPORTED_CONTROL_TYPE", session_id)
    if not ctrl.get("enabled"):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "CONTROL_DISABLED", session_id)
    if _UIA_CHECKBOX_PATTERN not in (ctrl.get("patterns") or []):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "TOGGLE_PATTERN_REQUIRED", session_id)
    pre_r = executor.read_checked_by_identity(identity)
    if not pre_r.get("ok"):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE,
                         "PRE_STATE_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    pre_toggle = pre_r.get("toggle_state")
    if pre_toggle == 2:
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE, "CONTROL_INDETERMINATE", session_id)
    if pre_toggle not in (0, 1):
        return _prep_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_PREPARE,
                         "UNEXPECTED_TOGGLE_STATE:" + str(pre_toggle), session_id)
    target_toggle = 1 if target_checked else 0
    _, physical_state_anchor = _uia_pre_state_checked(
        identity, pre_toggle, bool(ctrl.get("enabled")))
    desc = {
        "operation_type": OP_UIA_SET_CHECKED,
        "target_identity": identity,
        "target_checked": target_checked,
        "target_toggle_state": target_toggle,
        "pre_toggle_state": pre_toggle,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_UIA_SET_CHECKED, desc)
    scope = _uia_scope_id(identity)
    child = _v2id("chd", eah + scope + str(target_toggle))
    v2id  = _v2id("v2x", eah + session_id + "UIA_SET_CHECKED")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_UIA_SET_CHECKED, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_UIA_SET_CHECKED, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "target_identity": identity, "scope_id": scope,
        "target_checked": target_checked, "target_toggle_state": target_toggle,
        "pre_toggle_state": pre_toggle,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_SCHK_PREPARE, OP_UIA_SET_CHECKED,
                          PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                          execution_authority_hash=eah, target_identity=identity,
                          scope_id=scope, target_checked=target_checked,
                          target_toggle_state=target_toggle, pre_toggle_state=pre_toggle,
                          physical_state_anchor=physical_state_anchor,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


def pc_v2_uia_set_checked_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc and desc.get("eah") == exp_eah
                   and _eah(OP_UIA_SET_CHECKED, desc.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d              = desc["descriptor"]
    identity       = d.get("target_identity")
    target_checked = d.get("target_checked")
    target_toggle  = d.get("target_toggle_state")
    stored_psa     = d.get("physical_state_anchor", "")
    desc_valid = (_uia_identity_ok(identity) and isinstance(target_checked, bool)
                  and target_toggle in (0, 1))
    if not desc_valid:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "DESCRIPTOR_INVALID", session_id)
    pre_r = executor.read_checked_by_identity(identity)
    if not pre_r.get("ok"):
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "TOCTOU_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    current_toggle = pre_r.get("toggle_state")
    _, current_psa = _uia_pre_state_checked(identity, current_toggle, True)
    if current_psa != stored_psa:
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _uia_scope_id(identity)
    apr    = _approval(v2id, child, exp_eah, scope_id + str(target_toggle))
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_UIA_SET_CHECKED,
                    kxpre=st["kxpre"], physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    if current_toggle == target_toggle:
        post_r = executor.read_checked_by_identity(identity)
        if not post_r.get("ok"):
            return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE,
                             "TOCTOU_POST_READ_FAILED:" + str(post_r.get("error", "")), session_id)
        post_toggle = post_r.get("toggle_state")
        if post_toggle != target_toggle:
            return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = False
    else:
        ex = executor.set_checked_by_identity(identity, target_checked)
        if not ex.get("ok"):
            return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "EXECUTOR_ERROR:" + str(ex.get("error", "")), session_id)
        post_toggle = ex.get("post_toggle_state")
        if not ex.get("realized_state_verified") or post_toggle != target_toggle:
            return _exec_rej(OP_UIA_SET_CHECKED, _CAP_SCHK_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = ex.get("mutation_performed")
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_UIA_SET_CHECKED, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "target_identity": identity, "scope_id": scope_id,
        "target_checked": target_checked, "target_toggle_state": target_toggle,
        "pre_toggle_state": current_toggle, "post_toggle_state": post_toggle,
        "mutation_performed": mutation_flag,
        "proof_strength": "STRONG", "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "control.set_checked_by_identity",
        "receipt": _rcpt(_CAP_SCHK_EXECUTE, OP_UIA_SET_CHECKED, EXECUTED_OK, session_id,
                          kx108_pre_gate=gate, target_identity=identity, scope_id=scope_id,
                          target_checked=target_checked, target_toggle_state=target_toggle,
                          pre_toggle_state=current_toggle, post_toggle_state=post_toggle,
                          proof_strength="STRONG", realized_state_verified=True,
                          physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE",
                          executor_provider=executor.EXECUTOR_PROVIDER,
                          executor_backend=executor.EXECUTOR_BACKEND,
                          executor_capability="control.set_checked_by_identity"),
    }








_UIA_RADIO_PATTERN = "selection_item"


def _uia_pre_state_selected(identity: dict, is_selected: bool, enabled: bool):
    snapshot = {
        "anchor_schema": "UIA_SELECT_RADIO_PRE_STATE_V0",
        "identity": {k: identity.get(k) for k in _UIA_IDENTITY_PRIMARY + _UIA_IDENTITY_GUARDS},
        "enabled": bool(enabled),
        "pre_is_selected": bool(is_selected),
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def pc_v2_uia_select_radio_prepare(
        window_hwnd, target_identity,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(window_hwnd, int) or isinstance(window_hwnd, bool) or window_hwnd <= 0:
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "WINDOW_HWND_REQUIRED", session_id)
    if not _uia_identity_ok(target_identity) or target_identity.get("window_hwnd") != window_hwnd:
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "STABLE_TARGET_IDENTITY_REQUIRED", session_id)
    st = _stores(stores_base_dir)
    listing = executor.list_controls_uia(window_hwnd)
    if not listing.get("ok"):
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(listing.get("error", "")), session_id)
    matches = [c for c in listing.get("controls", [])
               if c.get("identity", {}).get("runtime_id") == target_identity["runtime_id"]]
    if not matches:
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "CONTROL_NOT_FOUND", session_id)
    if len(matches) > 1:
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "CONTROL_AMBIGUOUS", session_id)
    ctrl = matches[0]
    identity = dict(ctrl["identity"])
    if not _uia_identity_ok(identity) or not _uia_identity_matches(target_identity, identity):
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "CONTROL_IDENTITY_MISMATCH", session_id)
    if identity.get("control_type") != "RadioButton":
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "UNSUPPORTED_CONTROL_TYPE", session_id)
    if not ctrl.get("enabled"):
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "CONTROL_DISABLED", session_id)
    if _UIA_RADIO_PATTERN not in (ctrl.get("patterns") or []):
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE, "SELECTION_ITEM_PATTERN_REQUIRED", session_id)
    pre_r = executor.read_selected_by_identity(identity)
    if not pre_r.get("ok"):
        return _prep_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_PREPARE,
                         "PRE_STATE_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    pre_is_selected = bool(pre_r.get("is_selected"))
    _, physical_state_anchor = _uia_pre_state_selected(
        identity, pre_is_selected, bool(ctrl.get("enabled")))
    desc = {
        "operation_type": OP_UIA_SELECT_RADIO,
        "target_identity": identity,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_selected,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_UIA_SELECT_RADIO, desc)
    scope = _uia_scope_id(identity)
    child = _v2id("chd", eah + scope + "SELECTED")
    v2id  = _v2id("v2x", eah + session_id + "UIA_SELECT_RADIO")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_UIA_SELECT_RADIO, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_UIA_SELECT_RADIO, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "target_identity": identity, "scope_id": scope,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_selected,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_SRAD_PREPARE, OP_UIA_SELECT_RADIO,
                          PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                          execution_authority_hash=eah, target_identity=identity,
                          scope_id=scope, desired_state="SELECTED",
                          pre_is_selected=pre_is_selected,
                          physical_state_anchor=physical_state_anchor,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


def pc_v2_uia_select_radio_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc and desc.get("eah") == exp_eah
                   and _eah(OP_UIA_SELECT_RADIO, desc.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d            = desc["descriptor"]
    identity     = d.get("target_identity")
    stored_psa   = d.get("physical_state_anchor", "")
    pre_is_sel   = d.get("pre_is_selected")
    desc_valid = (_uia_identity_ok(identity) and isinstance(pre_is_sel, bool)
                  and d.get("desired_state") == "SELECTED")
    if not desc_valid:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "DESCRIPTOR_INVALID", session_id)
    pre_r = executor.read_selected_by_identity(identity)
    if not pre_r.get("ok"):
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "TOCTOU_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    current_is_selected = bool(pre_r.get("is_selected"))
    _, current_psa = _uia_pre_state_selected(identity, current_is_selected, True)
    if current_psa != stored_psa:
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _uia_scope_id(identity)
    apr    = _approval(v2id, child, exp_eah, scope_id + "SELECTED")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_UIA_SELECT_RADIO,
                    kxpre=st["kxpre"], physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    if current_is_selected:
        post_r = executor.read_selected_by_identity(identity)
        if not post_r.get("ok"):
            return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE,
                             "TOCTOU_POST_READ_FAILED:" + str(post_r.get("error", "")), session_id)
        post_is_selected = bool(post_r.get("is_selected"))
        if not post_is_selected:
            return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = False
    else:
        ex = executor.select_radio_by_identity(identity)
        if not ex.get("ok"):
            return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "EXECUTOR_ERROR:" + str(ex.get("error", "")), session_id)
        post_is_selected = bool(ex.get("post_is_selected"))
        if not ex.get("realized_state_verified") or not post_is_selected:
            return _exec_rej(OP_UIA_SELECT_RADIO, _CAP_SRAD_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = ex.get("mutation_performed")
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_UIA_SELECT_RADIO, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "target_identity": identity, "scope_id": scope_id,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_sel, "post_is_selected": post_is_selected,
        "mutation_performed": mutation_flag,
        "proof_strength": "STRONG", "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "control.select_radio_by_identity",
        "receipt": _rcpt(_CAP_SRAD_EXECUTE, OP_UIA_SELECT_RADIO, EXECUTED_OK, session_id,
                          kx108_pre_gate=gate, target_identity=identity, scope_id=scope_id,
                          desired_state="SELECTED",
                          pre_is_selected=pre_is_sel, post_is_selected=post_is_selected,
                          proof_strength="STRONG", realized_state_verified=True,
                          physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE",
                          executor_provider=executor.EXECUTOR_PROVIDER,
                          executor_backend=executor.EXECUTOR_BACKEND,
                          executor_capability="control.select_radio_by_identity"),
    }




_UIA_TAB_PATTERN = "selection_item"


def pc_v2_uia_select_tab_prepare(
        window_hwnd, target_identity,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(window_hwnd, int) or isinstance(window_hwnd, bool) or window_hwnd <= 0:
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "WINDOW_HWND_REQUIRED", session_id)
    if not _uia_identity_ok(target_identity) or target_identity.get("window_hwnd") != window_hwnd:
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "STABLE_TARGET_IDENTITY_REQUIRED", session_id)
    st = _stores(stores_base_dir)
    listing = executor.list_controls_uia(window_hwnd)
    if not listing.get("ok"):
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE,
                         "WINDOW_NOT_FOUND:" + str(listing.get("error", "")), session_id)
    matches = [c for c in listing.get("controls", [])
               if c.get("identity", {}).get("runtime_id") == target_identity["runtime_id"]]
    if not matches:
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "CONTROL_NOT_FOUND", session_id)
    if len(matches) > 1:
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "CONTROL_AMBIGUOUS", session_id)
    ctrl = matches[0]
    identity = dict(ctrl["identity"])
    if not _uia_identity_ok(identity) or not _uia_identity_matches(target_identity, identity):
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "CONTROL_IDENTITY_MISMATCH", session_id)
    if identity.get("control_type") != "TabItem":
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "UNSUPPORTED_CONTROL_TYPE", session_id)
    if not ctrl.get("enabled"):
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "CONTROL_DISABLED", session_id)
    if _UIA_TAB_PATTERN not in (ctrl.get("patterns") or []):
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE, "SELECTION_ITEM_PATTERN_REQUIRED", session_id)
    pre_r = executor.read_selected_by_identity(identity)
    if not pre_r.get("ok"):
        return _prep_rej(OP_UIA_SELECT_TAB, _CAP_STAB_PREPARE,
                         "PRE_STATE_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    pre_is_selected = bool(pre_r.get("is_selected"))
    _, physical_state_anchor = _uia_pre_state_selected(
        identity, pre_is_selected, bool(ctrl.get("enabled")))
    desc = {
        "operation_type": OP_UIA_SELECT_TAB,
        "target_identity": identity,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_selected,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_UIA_SELECT_TAB, desc)
    scope = _uia_scope_id(identity)
    child = _v2id("chd", eah + scope + "SELECTED")
    v2id  = _v2id("v2x", eah + session_id + "UIA_SELECT_TAB")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_UIA_SELECT_TAB, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_UIA_SELECT_TAB, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "target_identity": identity, "scope_id": scope,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_selected,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_STAB_PREPARE, OP_UIA_SELECT_TAB,
                          PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                          execution_authority_hash=eah, target_identity=identity,
                          scope_id=scope, desired_state="SELECTED",
                          pre_is_selected=pre_is_selected,
                          physical_state_anchor=physical_state_anchor,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


def pc_v2_uia_select_tab_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc and desc.get("eah") == exp_eah
                   and _eah(OP_UIA_SELECT_TAB, desc.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d            = desc["descriptor"]
    identity     = d.get("target_identity")
    stored_psa   = d.get("physical_state_anchor", "")
    pre_is_sel   = d.get("pre_is_selected")
    desc_valid = (_uia_identity_ok(identity) and isinstance(pre_is_sel, bool)
                  and d.get("desired_state") == "SELECTED")
    if not desc_valid:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "DESCRIPTOR_INVALID", session_id)
    pre_r = executor.read_selected_by_identity(identity)
    if not pre_r.get("ok"):
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "TOCTOU_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    current_is_selected = bool(pre_r.get("is_selected"))
    _, current_psa = _uia_pre_state_selected(identity, current_is_selected, True)
    if current_psa != stored_psa:
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _uia_scope_id(identity)
    apr    = _approval(v2id, child, exp_eah, scope_id + "SELECTED")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_UIA_SELECT_TAB,
                    kxpre=st["kxpre"], physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    if current_is_selected:
        post_r = executor.read_selected_by_identity(identity)
        if not post_r.get("ok"):
            return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE,
                             "TOCTOU_POST_READ_FAILED:" + str(post_r.get("error", "")), session_id)
        post_is_selected = bool(post_r.get("is_selected"))
        if not post_is_selected:
            return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = False
    else:
        ex = executor.select_tab_by_identity(identity)
        if not ex.get("ok"):
            return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "EXECUTOR_ERROR:" + str(ex.get("error", "")), session_id)
        post_is_selected = bool(ex.get("post_is_selected"))
        if not ex.get("realized_state_verified") or not post_is_selected:
            return _exec_rej(OP_UIA_SELECT_TAB, _CAP_STAB_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        mutation_flag = ex.get("mutation_performed")
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_UIA_SELECT_TAB, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "target_identity": identity, "scope_id": scope_id,
        "desired_state": "SELECTED",
        "pre_is_selected": pre_is_sel, "post_is_selected": post_is_selected,
        "mutation_performed": mutation_flag,
        "proof_strength": "STRONG", "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "control.select_tab_by_identity",
        "receipt": _rcpt(_CAP_STAB_EXECUTE, OP_UIA_SELECT_TAB, EXECUTED_OK, session_id,
                          kx108_pre_gate=gate, target_identity=identity, scope_id=scope_id,
                          desired_state="SELECTED",
                          pre_is_selected=pre_is_sel, post_is_selected=post_is_selected,
                          proof_strength="STRONG", realized_state_verified=True,
                          physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE",
                          executor_provider=executor.EXECUTOR_PROVIDER,
                          executor_backend=executor.EXECUTOR_BACKEND,
                          executor_capability="control.select_tab_by_identity"),
    }



from urllib.parse import urljoin, urlparse, urlunparse

_DEFAULT_PORTS = {"http": 80, "https": 443}
OP_BROWSER_NAVIGATE = "V2_BROWSER_NAVIGATE"
_CAP_BNAV_PREPARE   = "PC_V2_BROWSER_NAVIGATE_PREPARE"
_CAP_BNAV_EXECUTE   = "PC_V2_BROWSER_NAVIGATE_EXECUTE"

OP_BROWSER_READ    = "V2_BROWSER_READ"
_CAP_BRAD_PREPARE  = "PC_V2_BROWSER_READ_PREPARE"
_CAP_BRAD_EXECUTE  = "PC_V2_BROWSER_READ_EXECUTE"

OP_BROWSER_ACTIVATE_LINK = "V2_BROWSER_ACTIVATE_LINK"
_CAP_BLINK_PREPARE = "PC_V2_BROWSER_ACTIVATE_LINK_PREPARE"
_CAP_BLINK_EXECUTE = "PC_V2_BROWSER_ACTIVATE_LINK_EXECUTE"

OP_BROWSER_SET_DISCLOSURE = "V2_BROWSER_SET_DISCLOSURE"
_CAP_BDISC_PREPARE = "PC_V2_BROWSER_SET_DISCLOSURE_PREPARE"
_CAP_BDISC_EXECUTE = "PC_V2_BROWSER_SET_DISCLOSURE_EXECUTE"

_BLOCKED_BROWSER_LINK_SCHEMES = {"javascript", "data", "file", "mailto", "tel"}

_SENSITIVE_SELECTOR_PATTERNS = (
    "type=password", 'type="password"', "type=hidden", 'type="hidden"',
)

def _is_sensitive_selector(selector: str) -> bool:
    sl = selector.lower().replace(" ", "")
    return any(p.replace(" ", "") in sl for p in _SENSITIVE_SELECTOR_PATTERNS)


def _canon_url(url: str) -> str:
    """Canonical URL: lower scheme+host, strip default port, ensure non-empty path."""
    try:
        p = urlparse(url.strip())
        scheme = p.scheme.lower()
        host   = p.hostname or ""
        port   = p.port
        if port and _DEFAULT_PORTS.get(scheme) == port:
            netloc = host
        elif port:
            netloc = f"{host}:{port}"
        else:
            netloc = host
        path = p.path or "/"
        return urlunparse((scheme, netloc, path, p.params, p.query, p.fragment))
    except Exception:
        return url.strip()


def _url_origin(url: str) -> str:
    try:
        p = urlparse(url.strip())
        return f"{p.scheme.lower()}://{(p.hostname or '').lower()}"
    except Exception:
        return ""


def _browser_pre_state_anchor(pre_url: str, pre_origin: str, browser_session_id: str = "", page_id: str = ""):
    snapshot = {
        "anchor_schema": "BROWSER_NAVIGATE_PRE_STATE_V1",
        "browser_session_id": browser_session_id,
        "page_id": page_id,
        "pre_url": pre_url,
        "pre_origin": pre_origin,
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def pc_v2_browser_navigate_prepare(
        requested_url, redirect_policy="STRICT_EXACT_URL",
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(requested_url, str) or not requested_url.strip():
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE, "REQUESTED_URL_REQUIRED", session_id)
    if redirect_policy != "STRICT_EXACT_URL":
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE, "UNSUPPORTED_REDIRECT_POLICY", session_id)
    requested_url = requested_url.strip()
    st = _stores(stores_base_dir)
    pre_r = executor.read_browser_state()
    if not pre_r.get("ok"):
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE,
                         "PRE_STATE_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    browser_session_id = str(pre_r.get("browser_session_id") or "")
    page_id            = str(pre_r.get("page_id") or "")
    if not browser_session_id:
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE,
                         "PAGE_IDENTITY_MISSING:browser_session_id", session_id)
    if not page_id:
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE,
                         "PAGE_IDENTITY_MISSING:page_id", session_id)
    if pre_r.get("closed"):
        return _prep_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_PREPARE, "PAGE_CLOSED", session_id)
    pre_url    = str(pre_r.get("url") or "")
    pre_origin = str(pre_r.get("origin") or _url_origin(pre_url))
    canon_req  = _canon_url(requested_url)
    _, physical_state_anchor = _browser_pre_state_anchor(
        pre_url, pre_origin, browser_session_id, page_id)
    desc = {
        "operation_type": OP_BROWSER_NAVIGATE,
        "browser_session_id": browser_session_id,
        "page_id": page_id,
        "requested_url": requested_url,
        "canon_requested_url": canon_req,
        "requested_origin": _url_origin(requested_url),
        "redirect_policy": redirect_policy,
        "pre_url": pre_url,
        "pre_origin": pre_origin,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_BROWSER_NAVIGATE, desc)
    scope = _sha16(f"BROWSER:{canon_req}")
    child = _v2id("chd", eah + scope + "NAVIGATE")
    v2id  = _v2id("v2x", eah + session_id + "BROWSER_NAVIGATE")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_BROWSER_NAVIGATE, eah, desc, st["v2exec"])
    req_origin = _url_origin(requested_url)
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_NAVIGATE, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "requested_url": requested_url, "canon_requested_url": canon_req,
        "requested_origin": req_origin,
        "redirect_policy": redirect_policy,
        "browser_session_id": browser_session_id, "page_id": page_id,
        "pre_url": pre_url, "pre_origin": pre_origin,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_BNAV_PREPARE, OP_BROWSER_NAVIGATE,
                          PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                          execution_authority_hash=eah,
                          browser_session_id=browser_session_id, page_id=page_id,
                          requested_url=requested_url, canon_requested_url=canon_req,
                          requested_origin=req_origin,
                          redirect_policy=redirect_policy,
                          pre_url=pre_url, pre_origin=pre_origin,
                          physical_state_anchor=physical_state_anchor,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


def pc_v2_browser_navigate_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc and desc.get("eah") == exp_eah
                   and _eah(OP_BROWSER_NAVIGATE, desc.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d                  = desc["descriptor"]
    requested_url      = d.get("requested_url", "")
    canon_req          = d.get("canon_requested_url", "")
    stored_psa         = d.get("physical_state_anchor", "")
    stored_pre_url     = d.get("pre_url", "")
    stored_session_id  = d.get("browser_session_id", "")
    stored_page_id     = d.get("page_id", "")
    if not requested_url or not canon_req:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "DESCRIPTOR_INVALID", session_id)
    toctou_r = executor.read_browser_state()
    if not toctou_r.get("ok"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE,
                         "TOCTOU_READ_FAILED:" + str(toctou_r.get("error", "")), session_id)
    if toctou_r.get("closed"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "PAGE_CLOSED_AT_EXECUTE", session_id)
    current_url        = str(toctou_r.get("url") or "")
    current_origin     = str(toctou_r.get("origin") or _url_origin(current_url))
    current_session_id = str(toctou_r.get("browser_session_id") or "")
    current_page_id    = str(toctou_r.get("page_id") or "")
    _, current_psa     = _browser_pre_state_anchor(
        current_url, current_origin, current_session_id, current_page_id)
    if current_psa != stored_psa:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _sha16(f"BROWSER:{canon_req}")
    apr    = _approval(v2id, child, exp_eah, scope_id + "NAVIGATE")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_NAVIGATE,
                    kxpre=st["kxpre"], physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    # NO-OP: already on target URL
    if _canon_url(current_url) == canon_req:
        post_r = executor.read_browser_state()
        if not post_r.get("ok"):
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE,
                             "NOOP_POST_READ_FAILED:" + str(post_r.get("error", "")), session_id)
        post_url     = str(post_r.get("url") or "")
        post_session_id = str(post_r.get("browser_session_id") or "")
        post_page_id = str(post_r.get("page_id") or "")
        if _canon_url(post_url) != canon_req:
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
        if not post_session_id:
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
        if not post_page_id:
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
        if post_session_id != stored_session_id:
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
        if post_page_id != stored_page_id:
            return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
        return {
            "status": EXECUTED_OK, "j5_phase": "EXECUTE",
            "operation_type": OP_BROWSER_NAVIGATE, "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": KX_DECISION_AUTHORITY,
            "kx108_pre_gate": gate, "human_authorization_consumed": True,
            "requested_url": requested_url, "canon_requested_url": canon_req,
            "pre_url": stored_pre_url, "post_url": post_url,
            "post_origin": _url_origin(post_url),
            "nav_url": None, "nav_status": None, "mutation_performed": False,
            "proof_strength": "STRONG", "realized_state_verified": True,
            "independent_post_read": True,
            "executor_provider": executor.EXECUTOR_PROVIDER,
            "executor_backend": executor.EXECUTOR_BACKEND,
            "receipt": _rcpt(_CAP_BNAV_EXECUTE, OP_BROWSER_NAVIGATE, EXECUTED_OK, session_id,
                              kx108_pre_gate=gate, requested_url=requested_url,
                              canon_requested_url=canon_req, pre_url=stored_pre_url,
                              post_url=post_url, mutation_performed=False,
                              proof_strength="STRONG", realized_state_verified=True,
                              independent_post_read=True,
                              physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE"),
        }
    # MUTATE: navigate then independent post-read
    nav_r = executor.navigate(requested_url)
    if not nav_r.get("ok"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE,
                         "NAVIGATE_FAILED:" + str(nav_r.get("error", "")), session_id)
    nav_url    = nav_r.get("nav_url")
    nav_status = nav_r.get("nav_status")
    post_r = executor.read_browser_state()
    if not post_r.get("ok"):
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE,
                         "POST_READ_FAILED:" + str(post_r.get("error", "")), session_id)
    post_url     = str(post_r.get("url") or "")
    post_session_id = str(post_r.get("browser_session_id") or "")
    post_page_id = str(post_r.get("page_id") or "")
    if _canon_url(post_url) != canon_req:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)
    if not post_session_id:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_page_id:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_session_id != stored_session_id:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_page_id != stored_page_id:
        return _exec_rej(OP_BROWSER_NAVIGATE, _CAP_BNAV_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_NAVIGATE, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "requested_url": requested_url, "canon_requested_url": canon_req,
        "pre_url": stored_pre_url, "post_url": post_url,
        "post_origin": _url_origin(post_url),
        "nav_url": nav_url, "nav_status": nav_status, "mutation_performed": True,
        "proof_strength": "STRONG", "realized_state_verified": True,
        "independent_post_read": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(_CAP_BNAV_EXECUTE, OP_BROWSER_NAVIGATE, EXECUTED_OK, session_id,
                          kx108_pre_gate=gate, requested_url=requested_url,
                          canon_requested_url=canon_req, pre_url=stored_pre_url,
                          post_url=post_url, nav_url=nav_url, nav_status=nav_status,
                          mutation_performed=True,
                          proof_strength="STRONG", realized_state_verified=True,
                          independent_post_read=True,
                          physical_state_anchor=stored_psa, state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


def _browser_link_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "selector",
        "element_count", "tag_name", "role", "href", "resolved_href",
        "name", "aria_label", "text_sha256", "metadata_sha256",
        "visible", "enabled", "closed", "main_frame", "link_class",
    )
    return {k: inspected.get(k) for k in keys}


def _browser_link_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_ACTIVATE_LINK_PRE_STATE_V1",
        "browser_session_id": identity.get("browser_session_id") or "",
        "page_id": identity.get("page_id") or "",
        "pre_url": identity.get("url") or "",
        "pre_origin": identity.get("origin") or "",
        "selector": identity.get("selector") or "",
        "resolved_href": identity.get("resolved_href") or "",
        "metadata_sha256": identity.get("metadata_sha256") or "",
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_link_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "PAGE_IDENTITY_MISSING:browser_session_id"
    if not identity.get("page_id"):
        return "PAGE_IDENTITY_MISSING:page_id"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("element_count") != 1:
        return "SELECTOR_COUNT_NOT_EXACTLY_ONE"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("main_frame") is False:
        return "IFRAME_UNSUPPORTED"
    href = str(identity.get("href") or "").strip()
    resolved_href = str(identity.get("resolved_href") or "").strip()
    if not href:
        return "HREF_REQUIRED"
    if not resolved_href:
        return "RESOLVED_HREF_REQUIRED"
    scheme = urlparse(resolved_href).scheme.lower()
    if scheme in _BLOCKED_BROWSER_LINK_SCHEMES or scheme not in {"http", "https"}:
        return "BLOCKED_LINK_SCHEME:" + (scheme or "missing")
    if not (identity.get("tag_name") == "a" or identity.get("role") == "link"
            or identity.get("link_class") == "href_link"):
        return "NOT_LINK"
    if _canon_url(str(identity.get("url") or "")) == _canon_url(resolved_href):
        return "SAME_URL_LINK_DEFERRED"
    return ""


def _same_link_identity(a: dict, b: dict) -> bool:
    for key in ("browser_session_id", "page_id", "url", "origin", "selector",
                "href", "resolved_href", "metadata_sha256", "tag_name", "role",
                "link_class"):
        if str(a.get(key) or "") != str(b.get(key) or ""):
            return False
    return (a.get("element_count") == b.get("element_count")
            and a.get("visible") is b.get("visible")
            and a.get("enabled") is b.get("enabled")
            and bool(a.get("closed")) is bool(b.get("closed")))


def pc_v2_browser_activate_link_prepare(
        selector, navigation_policy="STRICT_EXACT_URL",
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(selector, str) or not selector.strip():
        return _prep_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_PREPARE, "SELECTOR_REQUIRED", session_id)
    if navigation_policy != "STRICT_EXACT_URL":
        return _prep_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_PREPARE, "UNSUPPORTED_NAVIGATION_POLICY", session_id)
    selector = selector.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_link(selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_PREPARE,
                         "INSPECT_LINK_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_link_identity(inspected)
    if not identity.get("resolved_href") and identity.get("href"):
        identity["resolved_href"] = _canon_url(urljoin(str(identity.get("url") or ""), str(identity.get("href") or "")))
    else:
        identity["resolved_href"] = _canon_url(str(identity.get("resolved_href") or ""))
    reason = _validate_link_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_PREPARE, reason, session_id)
    _, physical_state_anchor = _browser_link_pre_state_anchor(identity)
    resolved_href = str(identity.get("resolved_href") or "")
    desc = {
        "operation_type": OP_BROWSER_ACTIVATE_LINK,
        "public_action": "BROWSER_ACTIVATE_LINK",
        "navigation_policy": navigation_policy,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "element_identity": identity,
        "resolved_href": resolved_href,
        "target_origin": _url_origin(resolved_href),
        "popup_policy": "FAIL_CLOSED",
        "new_page_policy": "FAIL_CLOSED",
        "download_policy": "FAIL_CLOSED",
        "main_frame_only": True,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_BROWSER_ACTIVATE_LINK, desc)
    scope = _sha16(f"BROWSER_ACTIVATE_LINK:{selector}:{resolved_href}:{identity.get('metadata_sha256')}")
    child = _v2id("chd", eah + scope + "BROWSER_ACTIVATE_LINK")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_ACTIVATE_LINK")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_ACTIVATE_LINK, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_ACTIVATE_LINK,
        "public_action": "BROWSER_ACTIVATE_LINK",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "href": identity["href"],
        "resolved_href": resolved_href,
        "element_identity": identity,
        "navigation_policy": navigation_policy,
        "main_frame_only": True,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_BLINK_PREPARE, OP_BROWSER_ACTIVATE_LINK,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            browser_session_id=identity["browser_session_id"],
            page_id=identity["page_id"],
            selector=selector,
            resolved_href=resolved_href,
            metadata_sha256=identity.get("metadata_sha256"),
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_activate_link_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_ACTIVATE_LINK, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    identity = dict(d.get("element_identity") or {})
    selector = d.get("selector", "")
    resolved_href = d.get("resolved_href", "")
    toctou = executor.inspect_link(selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_link_identity(toctou)
    current_identity["resolved_href"] = _canon_url(str(current_identity.get("resolved_href") or ""))
    reason = _validate_link_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, reason, session_id)
    if not _same_link_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "ELEMENT_IDENTITY_DRIFT", session_id)
    _, current_psa = _browser_link_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _sha16(f"BROWSER_ACTIVATE_LINK:{selector}:{resolved_href}:{identity.get('metadata_sha256')}")
    apr = _approval(v2id, child, exp_eah, scope_id + "BROWSER_ACTIVATE_LINK")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_ACTIVATE_LINK,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.activate_link(identity)
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE,
                         "ACTIVATE_LINK_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, reason_code, session_id)
    post = executor.read_browser_state()
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE,
                         "POST_READ_FAILED:" + str(post.get("error", "")), session_id)
    post_url = str(post.get("url") or "")
    post_session_id = str(post.get("browser_session_id") or "")
    post_page_id = str(post.get("page_id") or "")
    if post.get("closed"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "POST_PAGE_CLOSED", session_id)
    if _canon_url(post_url) != _canon_url(resolved_href):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    if not post_session_id:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_page_id:
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_session_id != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_page_id != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_ACTIVATE_LINK, _CAP_BLINK_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_ACTIVATE_LINK,
        "public_action": "BROWSER_ACTIVATE_LINK",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "selector": selector,
        "href": identity.get("href"),
        "resolved_href": resolved_href,
        "pre_url": identity.get("url"),
        "post_url": post_url,
        "post_origin": str(post.get("origin") or _url_origin(post_url)),
        "browser_session_id": post_session_id,
        "page_id": post_page_id,
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BLINK_EXECUTE, OP_BROWSER_ACTIVATE_LINK, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            selector=selector,
            resolved_href=resolved_href,
            pre_url=identity.get("url"),
            post_url=post_url,
            proof_strength="STRONG",
            realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def _browser_disclosure_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "selector",
        "element_count", "tag_name", "role", "aria_expanded", "aria_controls",
        "open", "disclosure_class", "current_expanded", "text_sha256",
        "metadata_sha256", "visible", "enabled", "closed", "main_frame",
    )
    return {k: inspected.get(k) for k in keys}


def _browser_disclosure_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_SET_DISCLOSURE_PRE_STATE_V1",
        "browser_session_id": identity.get("browser_session_id") or "",
        "page_id": identity.get("page_id") or "",
        "pre_url": identity.get("url") or "",
        "pre_origin": identity.get("origin") or "",
        "selector": identity.get("selector") or "",
        "disclosure_class": identity.get("disclosure_class") or "",
        "current_expanded": identity.get("current_expanded"),
        "aria_controls": identity.get("aria_controls") or "",
        "metadata_sha256": identity.get("metadata_sha256") or "",
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_disclosure_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "PAGE_IDENTITY_MISSING:browser_session_id"
    if not identity.get("page_id"):
        return "PAGE_IDENTITY_MISSING:page_id"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("element_count") != 1:
        return "SELECTOR_COUNT_NOT_EXACTLY_ONE"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("main_frame") is not True:
        return "IFRAME_UNSUPPORTED"
    if identity.get("disclosure_class") not in {"DETAILS_OPEN", "ARIA_EXPANDED"}:
        return "UNSUPPORTED_DISCLOSURE_CLASS"
    if not isinstance(identity.get("current_expanded"), bool):
        return "DISCLOSURE_STATE_UNREADABLE"
    if identity.get("disclosure_class") == "ARIA_EXPANDED":
        if identity.get("aria_expanded") not in {"true", "false"}:
            return "ARIA_EXPANDED_INVALID"
    return ""


def _same_disclosure_identity(a: dict, b: dict) -> bool:
    for key in ("browser_session_id", "page_id", "url", "origin", "selector",
                "disclosure_class", "aria_controls", "metadata_sha256",
                "tag_name", "role"):
        if str(a.get(key) or "") != str(b.get(key) or ""):
            return False
    return a.get("element_count") == b.get("element_count")


def pc_v2_browser_set_disclosure_prepare(
        selector, target_expanded,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(selector, str) or not selector.strip():
        return _prep_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_PREPARE, "SELECTOR_REQUIRED", session_id)
    if not isinstance(target_expanded, bool):
        return _prep_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_PREPARE, "TARGET_EXPANDED_BOOL_REQUIRED", session_id)
    selector = selector.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_disclosure(selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_PREPARE,
                         "INSPECT_DISCLOSURE_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_disclosure_identity(inspected)
    reason = _validate_disclosure_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_PREPARE, reason, session_id)
    _, physical_state_anchor = _browser_disclosure_pre_state_anchor(identity)
    desc = {
        "operation_type": OP_BROWSER_SET_DISCLOSURE,
        "public_action": "BROWSER_SET_DISCLOSURE",
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "disclosure_class": identity["disclosure_class"],
        "element_identity": identity,
        "target_expanded": target_expanded,
        "popup_policy": "FAIL_CLOSED",
        "new_page_policy": "FAIL_CLOSED",
        "download_policy": "FAIL_CLOSED",
        "navigation_policy": "FAIL_CLOSED",
        "main_frame_only": True,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_BROWSER_SET_DISCLOSURE, desc)
    scope = _sha16(
        f"BROWSER_SET_DISCLOSURE:{selector}:{identity.get('disclosure_class')}:{identity.get('metadata_sha256')}:{target_expanded}"
    )
    child = _v2id("chd", eah + scope + "BROWSER_SET_DISCLOSURE")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_SET_DISCLOSURE")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_SET_DISCLOSURE, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_SET_DISCLOSURE,
        "public_action": "BROWSER_SET_DISCLOSURE",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "disclosure_class": identity["disclosure_class"],
        "current_expanded": identity["current_expanded"],
        "target_expanded": target_expanded,
        "element_identity": identity,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_BDISC_PREPARE, OP_BROWSER_SET_DISCLOSURE,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            browser_session_id=identity["browser_session_id"],
            page_id=identity["page_id"],
            selector=selector,
            disclosure_class=identity["disclosure_class"],
            current_expanded=identity["current_expanded"],
            target_expanded=target_expanded,
            metadata_sha256=identity.get("metadata_sha256"),
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_set_disclosure_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_SET_DISCLOSURE, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    identity = dict(d.get("element_identity") or {})
    selector = d.get("selector", "")
    target_expanded = d.get("target_expanded")
    toctou = executor.inspect_disclosure(selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_disclosure_identity(toctou)
    reason = _validate_disclosure_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, reason, session_id)
    if not _same_disclosure_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "ELEMENT_IDENTITY_DRIFT", session_id)
    if current_identity.get("current_expanded") is not identity.get("current_expanded"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "PRE_STATE_DRIFT", session_id)
    if current_identity.get("visible") is not True:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "ELEMENT_NOT_VISIBLE", session_id)
    if current_identity.get("enabled") is not True:
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "ELEMENT_NOT_ENABLED", session_id)
    _, current_psa = _browser_disclosure_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _sha16(
        f"BROWSER_SET_DISCLOSURE:{selector}:{identity.get('disclosure_class')}:{identity.get('metadata_sha256')}:{target_expanded}"
    )
    apr = _approval(v2id, child, exp_eah, scope_id + "BROWSER_SET_DISCLOSURE")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_SET_DISCLOSURE,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.set_disclosure(identity, bool(target_expanded))
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE,
                         "SET_DISCLOSURE_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("navigation_detected", "UNEXPECTED_NAVIGATION"),
                              ("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, reason_code, session_id)
    post = executor.inspect_disclosure(selector)
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE,
                         "POST_INSPECT_FAILED:" + str(post.get("error", "")), session_id)
    post_identity = _browser_disclosure_identity(post)
    if not post_identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_identity.get("browser_session_id") != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_identity.get("page_id") != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if not _same_disclosure_identity({**identity, "current_expanded": post_identity.get("current_expanded")}, post_identity):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, "POST_ELEMENT_IDENTITY_DRIFT", session_id)
    if post_identity.get("current_expanded") is not bool(target_expanded):
        return _exec_rej(OP_BROWSER_SET_DISCLOSURE, _CAP_BDISC_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_SET_DISCLOSURE,
        "public_action": "BROWSER_SET_DISCLOSURE",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "selector": selector,
        "disclosure_class": identity.get("disclosure_class"),
        "pre_url": identity.get("url"),
        "post_url": post_identity.get("url"),
        "browser_session_id": post_identity.get("browser_session_id"),
        "page_id": post_identity.get("page_id"),
        "current_expanded": post_identity.get("current_expanded"),
        "target_expanded": bool(target_expanded),
        "mutation_performed": bool(act.get("mutation_performed")),
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BDISC_EXECUTE, OP_BROWSER_SET_DISCLOSURE, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            selector=selector,
            disclosure_class=identity.get("disclosure_class"),
            target_expanded=bool(target_expanded),
            current_expanded=post_identity.get("current_expanded"),
            mutation_performed=bool(act.get("mutation_performed")),
            proof_strength="STRONG",
            realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }





def _browser_checkbox_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "selector",
        "element_count", "tag_name", "type", "role", "name", "id",
        "form_owner", "checked", "indeterminate_status", "metadata_sha256",
        "visible", "enabled", "closed", "main_frame",
    )
    return {k: inspected.get(k) for k in keys}


def _browser_checkbox_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_SET_CHECKED_PRE_STATE_V1",
        "browser_session_id": identity.get("browser_session_id") or "",
        "page_id": identity.get("page_id") or "",
        "pre_url": identity.get("url") or "",
        "pre_origin": identity.get("origin") or "",
        "selector": identity.get("selector") or "",
        "checked": identity.get("checked"),
        "indeterminate_status": identity.get("indeterminate_status") or "",
        "metadata_sha256": identity.get("metadata_sha256") or "",
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_checkbox_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "PAGE_IDENTITY_MISSING:browser_session_id"
    if not identity.get("page_id"):
        return "PAGE_IDENTITY_MISSING:page_id"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("element_count") != 1:
        return "SELECTOR_COUNT_NOT_EXACTLY_ONE"
    if identity.get("tag_name") != "input":
        return "UNSUPPORTED_CHECKBOX_TARGET"
    if identity.get("type") != "checkbox":
        return "UNSUPPORTED_CHECKBOX_TARGET"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("main_frame") is not True:
        return "IFRAME_UNSUPPORTED"
    if not isinstance(identity.get("checked"), bool):
        return "CHECKBOX_STATE_UNREADABLE"
    if identity.get("indeterminate_status") != "FALSE_PROVEN":
        return "INDETERMINATE_STATE_UNPROVABLE"
    return ""


def _validate_checkbox_semantics(semantic_intent, semantic_risk) -> str:
    if not isinstance(semantic_intent, str) or not semantic_intent.strip():
        return "SEMANTIC_INTENT_REQUIRED"
    if len(semantic_intent.strip()) > 160:
        return "SEMANTIC_INTENT_TOO_LONG"
    if semantic_risk not in {"LOW", "MEDIUM", "HIGH"}:
        return "SEMANTIC_RISK_INVALID"
    return ""


def _same_checkbox_identity(a: dict, b: dict) -> bool:
    for key in ("browser_session_id", "page_id", "url", "origin", "selector",
                "tag_name", "type", "role", "name", "id", "form_owner",
                "metadata_sha256"):
        if str(a.get(key) or "") != str(b.get(key) or ""):
            return False
    return a.get("element_count") == b.get("element_count")


def pc_v2_browser_set_checked_prepare(
        selector, target_checked, semantic_intent, semantic_risk,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(selector, str) or not selector.strip():
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE, "SELECTOR_REQUIRED", session_id)
    if not isinstance(target_checked, bool):
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE, "TARGET_CHECKED_BOOL_REQUIRED", session_id)
    reason = _validate_checkbox_semantics(semantic_intent, semantic_risk)
    if reason:
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE, reason, session_id)
    selector = selector.strip()
    semantic_intent = semantic_intent.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_checkbox(selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE,
                         "INSPECT_CHECKBOX_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_checkbox_identity(inspected)
    reason = _validate_checkbox_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_PREPARE, reason, session_id)
    _, physical_state_anchor = _browser_checkbox_pre_state_anchor(identity)
    desc = {
        "operation_type": OP_BROWSER_SET_CHECKED,
        "public_action": "BROWSER_SET_CHECKED",
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "element_identity": identity,
        "target_checked": target_checked,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "popup_policy": "FAIL_CLOSED",
        "new_page_policy": "FAIL_CLOSED",
        "download_policy": "FAIL_CLOSED",
        "navigation_policy": "FAIL_CLOSED",
        "main_frame_only": True,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_BROWSER_SET_CHECKED, desc)
    scope = _sha16(
        f"BROWSER_SET_CHECKED:{selector}:{identity.get('metadata_sha256')}:{target_checked}:{semantic_intent}:{semantic_risk}"
    )
    child = _v2id("chd", eah + scope + "BROWSER_SET_CHECKED")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_SET_CHECKED")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_SET_CHECKED, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_SET_CHECKED,
        "public_action": "BROWSER_SET_CHECKED",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "current_checked": identity["checked"],
        "target_checked": target_checked,
        "indeterminate_status": identity["indeterminate_status"],
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "element_identity": identity,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_BCHK_PREPARE, OP_BROWSER_SET_CHECKED,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            browser_session_id=identity["browser_session_id"],
            page_id=identity["page_id"],
            selector=selector,
            current_checked=identity["checked"],
            target_checked=target_checked,
            indeterminate_status=identity["indeterminate_status"],
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            metadata_sha256=identity.get("metadata_sha256"),
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_set_checked_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_SET_CHECKED, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    identity = dict(d.get("element_identity") or {})
    selector = d.get("selector", "")
    target_checked = d.get("target_checked")
    toctou = executor.inspect_checkbox(selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_checkbox_identity(toctou)
    reason = _validate_checkbox_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, reason, session_id)
    if not _same_checkbox_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "ELEMENT_IDENTITY_DRIFT", session_id)
    if current_identity.get("checked") is not identity.get("checked"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "PRE_CHECKED_DRIFT", session_id)
    _, current_psa = _browser_checkbox_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "PRE_STATE_DRIFT", session_id)
    semantic_intent = d.get("semantic_intent", "")
    semantic_risk = d.get("semantic_risk", "")
    reason = _validate_checkbox_semantics(semantic_intent, semantic_risk)
    if reason:
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, reason, session_id)
    scope_id = _sha16(
        f"BROWSER_SET_CHECKED:{selector}:{identity.get('metadata_sha256')}:{target_checked}:{semantic_intent}:{semantic_risk}"
    )
    apr = _approval(v2id, child, exp_eah, scope_id + "BROWSER_SET_CHECKED")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_SET_CHECKED,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.set_checkbox(identity, bool(target_checked))
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE,
                         "SET_CHECKBOX_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("navigation_detected", "UNEXPECTED_NAVIGATION"),
                              ("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, reason_code, session_id)
    post = executor.inspect_checkbox(selector)
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE,
                         "POST_INSPECT_FAILED:" + str(post.get("error", "")), session_id)
    post_identity = _browser_checkbox_identity(post)
    if not post_identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_identity.get("browser_session_id") != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_identity.get("page_id") != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if not _same_checkbox_identity({**identity, "checked": post_identity.get("checked")}, post_identity):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_ELEMENT_IDENTITY_DRIFT", session_id)
    if post_identity.get("indeterminate_status") != "FALSE_PROVEN":
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, "POST_INDETERMINATE_STATE_UNPROVABLE", session_id)
    if post_identity.get("checked") is not bool(target_checked):
        return _exec_rej(OP_BROWSER_SET_CHECKED, _CAP_BCHK_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_SET_CHECKED,
        "public_action": "BROWSER_SET_CHECKED",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "selector": selector,
        "pre_url": identity.get("url"),
        "post_url": post_identity.get("url"),
        "browser_session_id": post_identity.get("browser_session_id"),
        "page_id": post_identity.get("page_id"),
        "current_checked": post_identity.get("checked"),
        "target_checked": bool(target_checked),
        "indeterminate_status": post_identity.get("indeterminate_status"),
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "mutation_performed": bool(act.get("mutation_performed")),
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BCHK_EXECUTE, OP_BROWSER_SET_CHECKED, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            selector=selector,
            target_checked=bool(target_checked),
            current_checked=post_identity.get("checked"),
            indeterminate_status=post_identity.get("indeterminate_status"),
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            mutation_performed=bool(act.get("mutation_performed")),
            proof_strength="STRONG",
            realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def _browser_radio_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "selector",
        "element_count", "tag_name", "type", "role", "name", "id",
        "form_owner", "checked", "radio_group_identity", "metadata_sha256",
        "visible", "enabled", "closed", "main_frame",
    )
    return {k: inspected.get(k) for k in keys}


def _browser_radio_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_SELECT_RADIO_PRE_STATE_V1",
        "browser_session_id": identity.get("browser_session_id") or "",
        "page_id": identity.get("page_id") or "",
        "pre_url": identity.get("url") or "",
        "pre_origin": identity.get("origin") or "",
        "selector": identity.get("selector") or "",
        "checked": identity.get("checked"),
        "radio_group_identity": identity.get("radio_group_identity") or "",
        "metadata_sha256": identity.get("metadata_sha256") or "",
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_radio_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "PAGE_IDENTITY_MISSING:browser_session_id"
    if not identity.get("page_id"):
        return "PAGE_IDENTITY_MISSING:page_id"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("element_count") != 1:
        return "SELECTOR_COUNT_NOT_EXACTLY_ONE"
    if identity.get("tag_name") != "input":
        return "UNSUPPORTED_RADIO_TARGET"
    if identity.get("type") != "radio":
        return "UNSUPPORTED_RADIO_TARGET"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("main_frame") is not True:
        return "IFRAME_UNSUPPORTED"
    if not isinstance(identity.get("checked"), bool):
        return "RADIO_STATE_UNREADABLE"
    if not identity.get("name") or not identity.get("radio_group_identity"):
        return "RADIO_GROUP_IDENTITY_INVALID"
    return ""


def _validate_radio_semantics(semantic_intent, semantic_risk) -> str:
    if not isinstance(semantic_intent, str) or not semantic_intent.strip():
        return "SEMANTIC_INTENT_REQUIRED"
    if len(semantic_intent.strip()) > 160:
        return "SEMANTIC_INTENT_TOO_LONG"
    if semantic_risk not in {"LOW", "MEDIUM", "HIGH"}:
        return "SEMANTIC_RISK_INVALID"
    return ""


def _same_radio_identity(a: dict, b: dict) -> bool:
    for key in ("browser_session_id", "page_id", "url", "origin", "selector",
                "tag_name", "type", "role", "name", "id", "form_owner",
                "radio_group_identity", "metadata_sha256"):
        if str(a.get(key) or "") != str(b.get(key) or ""):
            return False
    return a.get("element_count") == b.get("element_count")


def pc_v2_browser_select_radio_prepare(
        selector, semantic_intent, semantic_risk,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(selector, str) or not selector.strip():
        return _prep_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_PREPARE, "SELECTOR_REQUIRED", session_id)
    reason = _validate_radio_semantics(semantic_intent, semantic_risk)
    if reason:
        return _prep_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_PREPARE, reason, session_id)
    selector = selector.strip()
    semantic_intent = semantic_intent.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_radio(selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_PREPARE,
                         "INSPECT_RADIO_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_radio_identity(inspected)
    reason = _validate_radio_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_PREPARE, reason, session_id)
    _, physical_state_anchor = _browser_radio_pre_state_anchor(identity)
    desc = {
        "operation_type": OP_BROWSER_SELECT_RADIO,
        "public_action": "BROWSER_SELECT_RADIO",
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "element_identity": identity,
        "radio_group_identity": identity["radio_group_identity"],
        "desired_selected": True,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "peer_deselection_proof": "DEFER_V1",
        "popup_policy": "FAIL_CLOSED",
        "new_page_policy": "FAIL_CLOSED",
        "download_policy": "FAIL_CLOSED",
        "navigation_policy": "FAIL_CLOSED",
        "main_frame_only": True,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_BROWSER_SELECT_RADIO, desc)
    scope = _sha16(
        f"BROWSER_SELECT_RADIO:{selector}:{identity.get('metadata_sha256')}:{identity.get('radio_group_identity')}:{semantic_intent}:{semantic_risk}"
    )
    child = _v2id("chd", eah + scope + "BROWSER_SELECT_RADIO")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_SELECT_RADIO")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_SELECT_RADIO, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_SELECT_RADIO,
        "public_action": "BROWSER_SELECT_RADIO",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "selector": selector,
        "current_checked": identity["checked"],
        "desired_selected": True,
        "radio_group_identity": identity["radio_group_identity"],
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "peer_deselection_proof": "DEFER_V1",
        "element_identity": identity,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_BRDO_PREPARE, OP_BROWSER_SELECT_RADIO,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            browser_session_id=identity["browser_session_id"],
            page_id=identity["page_id"],
            selector=selector,
            current_checked=identity["checked"],
            desired_selected=True,
            radio_group_identity=identity["radio_group_identity"],
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            metadata_sha256=identity.get("metadata_sha256"),
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_select_radio_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_SELECT_RADIO, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    identity = dict(d.get("element_identity") or {})
    selector = d.get("selector", "")
    toctou = executor.inspect_radio(selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_radio_identity(toctou)
    reason = _validate_radio_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, reason, session_id)
    if not _same_radio_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "ELEMENT_IDENTITY_DRIFT", session_id)
    if current_identity.get("checked") is not identity.get("checked"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "PRE_CHECKED_DRIFT", session_id)
    _, current_psa = _browser_radio_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "PRE_STATE_DRIFT", session_id)
    semantic_intent = d.get("semantic_intent", "")
    semantic_risk = d.get("semantic_risk", "")
    reason = _validate_radio_semantics(semantic_intent, semantic_risk)
    if reason:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, reason, session_id)
    scope_id = _sha16(
        f"BROWSER_SELECT_RADIO:{selector}:{identity.get('metadata_sha256')}:{identity.get('radio_group_identity')}:{semantic_intent}:{semantic_risk}"
    )
    apr = _approval(v2id, child, exp_eah, scope_id + "BROWSER_SELECT_RADIO")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_SELECT_RADIO,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.select_radio(identity)
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE,
                         "SELECT_RADIO_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("navigation_detected", "UNEXPECTED_NAVIGATION"),
                              ("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, reason_code, session_id)
    post = executor.inspect_radio(selector)
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE,
                         "POST_INSPECT_FAILED:" + str(post.get("error", "")), session_id)
    post_identity = _browser_radio_identity(post)
    if not post_identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_identity.get("browser_session_id") != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_identity.get("page_id") != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if not _same_radio_identity({**identity, "checked": post_identity.get("checked")}, post_identity):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_ELEMENT_IDENTITY_DRIFT", session_id)
    if post_identity.get("radio_group_identity") != identity.get("radio_group_identity"):
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, "POST_RADIO_GROUP_DRIFT", session_id)
    if post_identity.get("checked") is not True:
        return _exec_rej(OP_BROWSER_SELECT_RADIO, _CAP_BRDO_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_SELECT_RADIO,
        "public_action": "BROWSER_SELECT_RADIO",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "selector": selector,
        "pre_url": identity.get("url"),
        "post_url": post_identity.get("url"),
        "browser_session_id": post_identity.get("browser_session_id"),
        "page_id": post_identity.get("page_id"),
        "current_checked": post_identity.get("checked"),
        "desired_selected": True,
        "radio_group_identity": post_identity.get("radio_group_identity"),
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "peer_deselection_proof": "DEFER_V1",
        "mutation_performed": bool(act.get("mutation_performed")),
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BRDO_EXECUTE, OP_BROWSER_SELECT_RADIO, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            selector=selector,
            desired_selected=True,
            current_checked=post_identity.get("checked"),
            radio_group_identity=post_identity.get("radio_group_identity"),
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            peer_deselection_proof="DEFER_V1",
            mutation_performed=bool(act.get("mutation_performed")),
            proof_strength="STRONG",
            realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def _browser_select_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "select_selector",
        "select_count", "tag_name", "role", "name", "id", "form_owner",
        "multiple", "current_value", "current_selected_option",
        "metadata_sha256", "visible", "enabled", "closed", "main_frame",
    )
    return {k: inspected.get(k) for k in keys}


def _browser_select_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_SELECT_OPTION_PRE_STATE_V1",
        "browser_session_id": identity.get("browser_session_id") or "",
        "page_id": identity.get("page_id") or "",
        "pre_url": identity.get("url") or "",
        "pre_origin": identity.get("origin") or "",
        "select_selector": identity.get("select_selector") or "",
        "current_value": identity.get("current_value") or "",
        "current_selected_option": identity.get("current_selected_option") or {},
        "metadata_sha256": identity.get("metadata_sha256") or "",
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_select_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "PAGE_IDENTITY_MISSING:browser_session_id"
    if not identity.get("page_id"):
        return "PAGE_IDENTITY_MISSING:page_id"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("select_count") != 1:
        return "SELECTOR_COUNT_NOT_EXACTLY_ONE"
    if identity.get("tag_name") != "select":
        return "UNSUPPORTED_SELECT_TARGET"
    if identity.get("multiple") is True:
        return "UNSUPPORTED_MULTI_SELECT_V0"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("main_frame") is not True:
        return "IFRAME_UNSUPPORTED"
    if not isinstance(identity.get("current_selected_option"), dict):
        return "CURRENT_SELECTED_OPTION_UNREADABLE"
    return ""


def _validate_option_target_modes(option_value=None, option_label=None, option_text=None, option_index=None):
    supplied = [
        ("value", "option_value", option_value),
        ("label", "option_label", option_label),
        ("text", "option_text", option_text),
        ("index", "option_index", option_index),
    ]
    present = [(mode, key, value) for mode, key, value in supplied if value is not None]
    if len(present) != 1:
        raise ValueError("EXACTLY_ONE_OPTION_IDENTITY_MODE_REQUIRED")
    mode, key, value = present[0]
    if mode == "index":
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError("OPTION_INDEX_INVALID")
    elif not isinstance(value, str) or not value:
        raise ValueError("OPTION_IDENTITY_VALUE_REQUIRED")
    return mode, key, value


def _same_physical_option(a: dict, b: dict) -> bool:
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    for key in ("option_value", "option_label", "option_text", "option_index", "option_disabled"):
        if a.get(key) != b.get(key):
            return False
    return True


def _same_option_identity(a: dict, b: dict) -> bool:
    if not _same_physical_option(a, b):
        return False
    for key in ("match_kind", "match_value", "match_count"):
        if a.get(key) != b.get(key):
            return False
    return True


def _option_count(options: list, key: str, value: str) -> int:
    return sum(1 for option in options if str(option.get(key) or "") == value)


def _resolve_select_option(options: list, option_value=None, option_label=None, option_text=None, option_index=None) -> dict:
    mode, key, value = _validate_option_target_modes(option_value, option_label, option_text, option_index)
    if mode == "index":
        matches = [option for option in options if option.get("option_index") == value]
    else:
        matches = [option for option in options if str(option.get(key) or "") == str(value)]
    if len(matches) == 0:
        raise ValueError("OPTION_TARGET_NOT_FOUND")
    if len(matches) > 1:
        if mode == "value":
            raise ValueError("DUPLICATE_OPTION_VALUE")
        if mode == "label":
            raise ValueError("DUPLICATE_OPTION_LABEL")
        if mode == "text":
            raise ValueError("DUPLICATE_OPTION_TEXT")
        raise ValueError("DUPLICATE_OPTION_INDEX")
    option = dict(matches[0])
    if option.get("option_disabled") is True:
        raise ValueError("OPTION_DISABLED")
    option["match_kind"] = mode
    option["match_value"] = value
    option["match_count"] = 1
    if _option_count(options, "option_value", str(option.get("option_value") or "")) != 1:
        raise ValueError("DUPLICATE_OPTION_VALUE")
    return option


def _same_select_identity(a: dict, b: dict) -> bool:
    for key in ("browser_session_id", "page_id", "url", "origin", "select_selector",
                "tag_name", "role", "name", "id", "form_owner", "multiple",
                "metadata_sha256"):
        if a.get(key) != b.get(key):
            return False
    return a.get("select_count") == b.get("select_count")


def _validate_option_semantics(semantic_intent, semantic_risk) -> str:
    if not isinstance(semantic_intent, str) or not semantic_intent.strip():
        return "SEMANTIC_INTENT_REQUIRED"
    if len(semantic_intent.strip()) > 160:
        return "SEMANTIC_INTENT_TOO_LONG"
    if semantic_risk not in {"LOW", "MEDIUM", "HIGH"}:
        return "SEMANTIC_RISK_INVALID"
    return ""


def pc_v2_browser_select_option_prepare(
        select_selector, semantic_intent, semantic_risk,
        *, stores_base_dir, session_id="", executor=None,
        option_value=None, option_label=None, option_text=None, option_index=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(select_selector, str) or not select_selector.strip():
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, "SELECTOR_REQUIRED", session_id)
    reason = _validate_option_semantics(semantic_intent, semantic_risk)
    if reason:
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, reason, session_id)
    try:
        _validate_option_target_modes(option_value, option_label, option_text, option_index)
    except ValueError as exc:
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, str(exc), session_id)
    select_selector = select_selector.strip()
    semantic_intent = semantic_intent.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_select(select_selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE,
                         "INSPECT_SELECT_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_select_identity(inspected)
    reason = _validate_select_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, reason, session_id)
    try:
        option_identity = _resolve_select_option(
            list(inspected.get("options") or []),
            option_value=option_value, option_label=option_label,
            option_text=option_text, option_index=option_index)
    except ValueError as exc:
        return _prep_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_PREPARE, str(exc), session_id)
    _, physical_state_anchor = _browser_select_pre_state_anchor(identity)
    desc = {
        "operation_type": OP_BROWSER_SELECT_OPTION,
        "public_action": "BROWSER_SELECT_OPTION",
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "select_selector": select_selector,
        "select_identity": identity,
        "option_identity": option_identity,
        "desired_state": "TARGET_OPTION_SELECTED",
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "popup_policy": "FAIL_CLOSED",
        "new_page_policy": "FAIL_CLOSED",
        "download_policy": "FAIL_CLOSED",
        "navigation_policy": "FAIL_CLOSED",
        "main_frame_only": True,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah = _eah(OP_BROWSER_SELECT_OPTION, desc)
    scope = _sha16(
        f"BROWSER_SELECT_OPTION:{select_selector}:{identity.get('metadata_sha256')}:{json.dumps(option_identity, sort_keys=True)}:{semantic_intent}:{semantic_risk}"
    )
    child = _v2id("chd", eah + scope + "BROWSER_SELECT_OPTION")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_SELECT_OPTION")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_SELECT_OPTION, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_SELECT_OPTION,
        "public_action": "BROWSER_SELECT_OPTION",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": identity["browser_session_id"],
        "page_id": identity["page_id"],
        "pre_url": identity["url"],
        "pre_origin": identity["origin"],
        "select_selector": select_selector,
        "current_selected_option": identity["current_selected_option"],
        "target_option_identity": option_identity,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "select_identity": identity,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_BOPT_PREPARE, OP_BROWSER_SELECT_OPTION,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            browser_session_id=identity["browser_session_id"],
            page_id=identity["page_id"],
            select_selector=select_selector,
            target_option_identity=option_identity,
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            metadata_sha256=identity.get("metadata_sha256"),
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_select_option_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_SELECT_OPTION, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    identity = dict(d.get("select_identity") or {})
    option_identity = dict(d.get("option_identity") or {})
    select_selector = d.get("select_selector", "")
    toctou = executor.inspect_select(select_selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_select_identity(toctou)
    reason = _validate_select_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, reason, session_id)
    if not _same_select_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "SELECT_IDENTITY_DRIFT", session_id)
    if not _same_physical_option(current_identity.get("current_selected_option"), identity.get("current_selected_option")):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "PRE_SELECTED_DRIFT", session_id)
    try:
        current_option = _resolve_select_option(
            list(toctou.get("options") or []),
            **{"option_" + option_identity.get("match_kind"): option_identity.get("match_value")})
    except ValueError as exc:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, str(exc), session_id)
    if not _same_option_identity(current_option, option_identity):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "OPTION_IDENTITY_DRIFT", session_id)
    _, current_psa = _browser_select_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "PRE_STATE_DRIFT", session_id)
    semantic_intent = d.get("semantic_intent", "")
    semantic_risk = d.get("semantic_risk", "")
    reason = _validate_option_semantics(semantic_intent, semantic_risk)
    if reason:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, reason, session_id)
    scope_id = _sha16(
        f"BROWSER_SELECT_OPTION:{select_selector}:{identity.get('metadata_sha256')}:{json.dumps(option_identity, sort_keys=True)}:{semantic_intent}:{semantic_risk}"
    )
    apr = _approval(v2id, child, exp_eah, scope_id + "BROWSER_SELECT_OPTION")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_SELECT_OPTION,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.select_option(identity, option_identity)
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE,
                         "SELECT_OPTION_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("navigation_detected", "UNEXPECTED_NAVIGATION"),
                              ("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, reason_code, session_id)
    post = executor.inspect_select(select_selector)
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE,
                         "POST_INSPECT_FAILED:" + str(post.get("error", "")), session_id)
    post_identity = _browser_select_identity(post)
    if not post_identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_identity.get("browser_session_id") != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_identity.get("page_id") != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if not _same_select_identity({**identity, "current_selected_option": post_identity.get("current_selected_option")}, post_identity):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_SELECT_IDENTITY_DRIFT", session_id)
    try:
        post_option = _resolve_select_option(
            list(post.get("options") or []),
            **{"option_" + option_identity.get("match_kind"): option_identity.get("match_value")})
    except ValueError as exc:
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, str(exc), session_id)
    if not _same_option_identity(post_option, option_identity):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, "POST_OPTION_IDENTITY_DRIFT", session_id)
    if not _same_physical_option(post_identity.get("current_selected_option"), option_identity):
        return _exec_rej(OP_BROWSER_SELECT_OPTION, _CAP_BOPT_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_SELECT_OPTION,
        "public_action": "BROWSER_SELECT_OPTION",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "select_selector": select_selector,
        "pre_url": identity.get("url"),
        "post_url": post_identity.get("url"),
        "browser_session_id": post_identity.get("browser_session_id"),
        "page_id": post_identity.get("page_id"),
        "current_selected_option": post_identity.get("current_selected_option"),
        "target_option_identity": option_identity,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "mutation_performed": bool(act.get("mutation_performed")),
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BOPT_EXECUTE, OP_BROWSER_SELECT_OPTION, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            select_selector=select_selector,
            target_option_identity=option_identity,
            semantic_intent=semantic_intent,
            semantic_risk=semantic_risk,
            mutation_performed=bool(act.get("mutation_performed")),
            proof_strength="STRONG",
            realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


_BROWSER_FIELD_SUPPORTED_CLASSES = {"INPUT_TEXT", "INPUT_SEARCH", "INPUT_EMAIL", "INPUT_URL", "INPUT_TEL", "TEXTAREA"}
_BROWSER_FIELD_SENSITIVE_AUTOCOMPLETE = {
    "current-password", "new-password", "one-time-code",
    "cc-number", "cc-csc", "cc-exp", "cc-exp-month", "cc-exp-year",
}
_BROWSER_FIELD_MAX_TARGET_VALUE_LENGTH = 4096


def _browser_field_identity(inspected: dict) -> dict:
    keys = (
        "browser_session_id", "page_id", "url", "origin", "closed", "selector",
        "element_count", "tag_name", "type", "name", "id", "role",
        "autocomplete", "form_owner", "visible", "enabled", "editable",
        "readonly", "supported_field_class", "current_value_sha256",
        "current_value_length", "metadata_sha256", "main_frame",
    )
    return {key: inspected.get(key) for key in keys}


def _browser_field_pre_state_anchor(identity: dict):
    snapshot = {
        "anchor_schema": "BROWSER_SET_FIELD_VALUE_PRE_STATE_V1",
        "field_identity": {k: identity.get(k) for k in (
            "browser_session_id", "page_id", "url", "origin", "selector",
            "element_count", "tag_name", "type", "name", "id", "role",
            "autocomplete", "form_owner", "metadata_sha256", "main_frame",
            "supported_field_class",
        )},
        "visible": identity.get("visible"),
        "enabled": identity.get("enabled"),
        "editable": identity.get("editable"),
        "readonly": identity.get("readonly"),
        "current_value_sha256": identity.get("current_value_sha256"),
        "current_value_length": identity.get("current_value_length"),
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def _validate_field_semantics(semantic_intent, semantic_risk) -> str:
    if not isinstance(semantic_intent, str) or not semantic_intent.strip():
        return "SEMANTIC_INTENT_REQUIRED"
    if len(semantic_intent.strip()) > 160:
        return "SEMANTIC_INTENT_TOO_LONG"
    if semantic_risk not in {"LOW", "MEDIUM", "HIGH"}:
        return "SEMANTIC_RISK_INVALID"
    return ""


def _validate_field_identity(identity: dict) -> str:
    if not identity.get("browser_session_id"):
        return "SESSION_ID_MISSING"
    if not identity.get("page_id"):
        return "PAGE_ID_MISSING"
    if identity.get("closed"):
        return "PAGE_CLOSED"
    if identity.get("element_count") != 1:
        return "FIELD_COUNT_NOT_ONE"
    if identity.get("main_frame") is not True:
        return "IFRAME_UNSUPPORTED"
    field_class = identity.get("supported_field_class")
    field_type = identity.get("type")
    if field_class not in _BROWSER_FIELD_SUPPORTED_CLASSES:
        if field_type == "password":
            return "PASSWORD_FIELD_DEFERRED"
        if field_type == "file":
            return "FILE_FIELD_BLOCKED"
        if field_type == "hidden":
            return "HIDDEN_FIELD_BLOCKED"
        if field_type in {"number", "date", "time", "datetime-local"}:
            return "FIELD_TYPE_DEFERRED"
        return "UNSUPPORTED_FIELD_TARGET"
    if str(identity.get("autocomplete") or "").lower() in _BROWSER_FIELD_SENSITIVE_AUTOCOMPLETE:
        return "SENSITIVE_AUTOCOMPLETE_DEFERRED"
    if identity.get("visible") is not True:
        return "ELEMENT_NOT_VISIBLE"
    if identity.get("enabled") is not True:
        return "ELEMENT_NOT_ENABLED"
    if identity.get("editable") is not True:
        return "ELEMENT_NOT_EDITABLE"
    if identity.get("readonly") is True:
        return "ELEMENT_READONLY"
    if not isinstance(identity.get("current_value_sha256"), str) or not identity.get("current_value_sha256"):
        return "CURRENT_VALUE_HASH_MISSING"
    if not isinstance(identity.get("current_value_length"), int):
        return "CURRENT_VALUE_LENGTH_MISSING"
    return ""


def _same_field_identity(a: dict, b: dict) -> bool:
    for key in (
        "browser_session_id", "page_id", "url", "origin", "selector",
        "element_count", "tag_name", "type", "name", "id", "role",
        "autocomplete", "form_owner", "metadata_sha256", "main_frame",
        "supported_field_class",
    ):
        if a.get(key) != b.get(key):
            return False
    return True


def pc_v2_browser_set_field_value_prepare(
        selector, target_value, semantic_intent, semantic_risk, *,
        stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(selector, str) or not selector.strip():
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, "SELECTOR_REQUIRED", session_id)
    if not isinstance(target_value, str):
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, "TARGET_VALUE_STRING_REQUIRED", session_id)
    if len(target_value) > _BROWSER_FIELD_MAX_TARGET_VALUE_LENGTH:
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, "TARGET_VALUE_TOO_LONG", session_id)
    reason = _validate_field_semantics(semantic_intent, semantic_risk)
    if reason:
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, reason, session_id)
    selector = selector.strip()
    semantic_intent = semantic_intent.strip()
    st = _stores(stores_base_dir)
    inspected = executor.inspect_field(selector)
    if not inspected.get("ok"):
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE,
                         "INSPECT_FIELD_FAILED:" + str(inspected.get("error", "")), session_id)
    identity = _browser_field_identity(inspected)
    reason = _validate_field_identity(identity)
    if reason:
        return _prep_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_PREPARE, reason, session_id)
    target_hash = _sha256_text(target_value)
    target_length = len(target_value)
    _, physical_state_anchor = _browser_field_pre_state_anchor(identity)
    desc = {
        "operation_type": OP_BROWSER_SET_FIELD_VALUE,
        "public_action": "BROWSER_SET_FIELD_VALUE",
        "selector": selector,
        "field_identity": identity,
        "target_value_sha256": target_hash,
        "target_value_length": target_length,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "max_target_value_length": _BROWSER_FIELD_MAX_TARGET_VALUE_LENGTH,
        "sensitive_autocomplete_denylist": sorted(_BROWSER_FIELD_SENSITIVE_AUTOCOMPLETE),
    }
    eah = _eah(OP_BROWSER_SET_FIELD_VALUE, desc)
    scope = _sha16(f"BROWSER_SET_FIELD_VALUE:{selector}:{identity.get('metadata_sha256')}:{target_hash}:{target_length}:{semantic_intent}:{semantic_risk}")
    child = _v2id("chd", eah + scope + "BROWSER_SET_FIELD_VALUE")
    v2id = _v2id("v2x", eah + session_id + "BROWSER_SET_FIELD_VALUE")
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_BROWSER_SET_FIELD_VALUE, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_SET_FIELD_VALUE,
        "public_action": "BROWSER_SET_FIELD_VALUE",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "selector": selector,
        "field_identity": identity,
        "target_value_sha256": target_hash,
        "target_value_length": target_length,
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "target_plaintext_persisted": False,
        "sensitive_autocomplete_denylist": sorted(_BROWSER_FIELD_SENSITIVE_AUTOCOMPLETE),
        "receipt": _rcpt(
            _CAP_BFLD_PREPARE, OP_BROWSER_SET_FIELD_VALUE,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah, selector=selector,
            target_value_sha256=target_hash, target_value_length=target_length,
            pre_value_sha256=identity.get("current_value_sha256"),
            pre_value_length=identity.get("current_value_length"),
            semantic_intent=semantic_intent, semantic_risk=semantic_risk,
            physical_state_anchor=physical_state_anchor,
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


def pc_v2_browser_set_field_value_execute(
        prepared_result, human_authorized_eah, human_authorization_reference, target_value,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    if not isinstance(target_value, str):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "TARGET_VALUE_STRING_REQUIRED", session_id)
    if len(target_value) > _BROWSER_FIELD_MAX_TARGET_VALUE_LENGTH:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "TARGET_VALUE_TOO_LONG", session_id)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    st = _stores(stores_base_dir)
    desc_rec = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc_rec and desc_rec.get("eah") == exp_eah
                   and _eah(OP_BROWSER_SET_FIELD_VALUE, desc_rec.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d = desc_rec["descriptor"]
    target_hash = d.get("target_value_sha256", "")
    target_length = d.get("target_value_length")
    if _sha256_text(target_value) != target_hash or len(target_value) != target_length:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "TARGET_VALUE_HASH_MISMATCH", session_id)
    identity = dict(d.get("field_identity") or {})
    selector = d.get("selector", "")
    toctou = executor.inspect_field(selector)
    if not toctou.get("ok"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE,
                         "TOCTOU_INSPECT_FAILED:" + str(toctou.get("error", "")), session_id)
    current_identity = _browser_field_identity(toctou)
    reason = _validate_field_identity(current_identity)
    if reason:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, reason, session_id)
    if not _same_field_identity(identity, current_identity):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "FIELD_IDENTITY_DRIFT", session_id)
    if current_identity.get("current_value_sha256") != identity.get("current_value_sha256"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "PRE_VALUE_HASH_DRIFT", session_id)
    if current_identity.get("current_value_length") != identity.get("current_value_length"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "PRE_VALUE_LENGTH_DRIFT", session_id)
    _, current_psa = _browser_field_pre_state_anchor(current_identity)
    if current_psa != d.get("physical_state_anchor", ""):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "PRE_STATE_DRIFT", session_id)
    semantic_intent = d.get("semantic_intent", "")
    semantic_risk = d.get("semantic_risk", "")
    reason = _validate_field_semantics(semantic_intent, semantic_risk)
    if reason:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, reason, session_id)
    scope_id = _sha16(f"BROWSER_SET_FIELD_VALUE:{selector}:{identity.get('metadata_sha256')}:{target_hash}:{target_length}:{semantic_intent}:{semantic_risk}")
    apr = _approval(v2id, child, exp_eah, scope_id + target_hash)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_SET_FIELD_VALUE,
                    kxpre=st["kxpre"], physical_state_anchor=d.get("physical_state_anchor", ""),
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    act = executor.set_field_value(identity, target_value)
    if not act.get("ok"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE,
                         "SET_FIELD_VALUE_FAILED:" + str(act.get("error", "")), session_id)
    for flag, reason_code in (("navigation_detected", "UNEXPECTED_NAVIGATION"),
                              ("popup_detected", "UNEXPECTED_POPUP"),
                              ("new_page_detected", "UNEXPECTED_NEW_PAGE"),
                              ("download_detected", "UNEXPECTED_DOWNLOAD")):
        if act.get(flag):
            return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, reason_code, session_id)
    post = executor.inspect_field(selector)
    if not post.get("ok"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE,
                         "POST_INSPECT_FAILED:" + str(post.get("error", "")), session_id)
    post_identity = _browser_field_identity(post)
    if not post_identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_identity.get("browser_session_id") != identity.get("browser_session_id"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_identity.get("page_id") != identity.get("page_id"):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if not _same_field_identity({**identity, "current_value_sha256": post_identity.get("current_value_sha256"),
                                 "current_value_length": post_identity.get("current_value_length")}, post_identity):
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "POST_FIELD_IDENTITY_DRIFT", session_id)
    if post_identity.get("current_value_sha256") != target_hash:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, REALIZED_STATE_MISMATCH, session_id)
    if post_identity.get("current_value_length") != target_length:
        return _exec_rej(OP_BROWSER_SET_FIELD_VALUE, _CAP_BFLD_EXECUTE, "REALIZED_STATE_LENGTH_MISMATCH", session_id)
    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_SET_FIELD_VALUE,
        "public_action": "BROWSER_SET_FIELD_VALUE",
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "selector": selector,
        "target_value_sha256": target_hash,
        "post_value_sha256": post_identity.get("current_value_sha256"),
        "target_value_length": target_length,
        "post_value_length": post_identity.get("current_value_length"),
        "pre_value_sha256": identity.get("current_value_sha256"),
        "pre_value_length": identity.get("current_value_length"),
        "semantic_intent": semantic_intent,
        "semantic_risk": semantic_risk,
        "mutation_performed": bool(act.get("mutation_performed")),
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "independent_post_read": True,
        "plaintext_value_returned": False,
        "navigation_detected": False,
        "popup_detected": False,
        "new_page_detected": False,
        "download_detected": False,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_BFLD_EXECUTE, OP_BROWSER_SET_FIELD_VALUE, EXECUTED_OK, session_id,
            kx108_pre_gate=gate, selector=selector,
            target_value_sha256=target_hash, post_value_sha256=post_identity.get("current_value_sha256"),
            target_value_length=target_length, post_value_length=post_identity.get("current_value_length"),
            pre_value_sha256=identity.get("current_value_sha256"),
            pre_value_length=identity.get("current_value_length"),
            semantic_intent=semantic_intent, semantic_risk=semantic_risk,
            mutation_performed=bool(act.get("mutation_performed")),
            proof_strength="STRONG", realized_state_verified=True,
            independent_post_read=True,
            physical_state_anchor=d.get("physical_state_anchor", ""),
            state_anchor_kind="PHYSICAL_PRE_STATE",
        ),
    }


# ============================
# GOVERNED_BROWSER_READ
# ============================

def _browser_read_pre_state_anchor(browser_session_id, page_id, pre_url, pre_origin):
    snapshot = {
        "anchor_schema": "BROWSER_READ_PRE_STATE_V1",
        "browser_session_id": browser_session_id,
        "page_id": page_id,
        "pre_url": pre_url,
        "pre_origin": pre_origin,
    }
    return snapshot, _sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def pc_v2_browser_read_prepare(
        selector=None,
        *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE, "EXECUTOR_REQUIRED", session_id)
    if selector is not None and not isinstance(selector, str):
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE, "SELECTOR_MUST_BE_STRING", session_id)
    if selector and _is_sensitive_selector(selector):
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE, "SENSITIVE_SELECTOR_FORBIDDEN", session_id)
    st = _stores(stores_base_dir)
    pre_r = executor.read_browser_state()
    if not pre_r.get("ok"):
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE,
                         "PRE_STATE_READ_FAILED:" + str(pre_r.get("error", "")), session_id)
    browser_session_id = str(pre_r.get("browser_session_id") or "")
    page_id            = str(pre_r.get("page_id") or "")
    if not browser_session_id:
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE,
                         "PAGE_IDENTITY_MISSING:browser_session_id", session_id)
    if not page_id:
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE,
                         "PAGE_IDENTITY_MISSING:page_id", session_id)
    if pre_r.get("closed"):
        return _prep_rej(OP_BROWSER_READ, _CAP_BRAD_PREPARE, "PAGE_CLOSED", session_id)
    pre_url    = str(pre_r.get("url") or "")
    pre_origin = str(pre_r.get("origin") or _url_origin(pre_url))
    read_scope = "SELECTOR" if selector else "FULL_PAGE"
    _, physical_state_anchor = _browser_read_pre_state_anchor(
        browser_session_id, page_id, pre_url, pre_origin)
    desc = {
        "operation_type": OP_BROWSER_READ,
        "browser_session_id": browser_session_id,
        "page_id": page_id,
        "pre_url": pre_url,
        "pre_origin": pre_origin,
        "selector": selector,
        "read_scope": read_scope,
        "session_id": session_id,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
    }
    eah   = _eah(OP_BROWSER_READ, desc)
    scope = _sha16(f"BROWSER_READ:{read_scope}:{selector or ''}")
    child = _v2id("chd", eah + scope + "BROWSER_READ")
    v2id  = _v2id("v2x", eah + session_id + "BROWSER_READ")
    mh    = _sha16(json.dumps(desc, sort_keys=True))
    dh    = _persist_desc(v2id, OP_BROWSER_READ, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL, "j5_phase": "PREPARE",
        "operation_type": OP_BROWSER_READ, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "browser_session_id": browser_session_id, "page_id": page_id,
        "pre_url": pre_url, "pre_origin": pre_origin,
        "selector": selector, "read_scope": read_scope,
        "physical_state_anchor": physical_state_anchor,
        "state_anchor_kind": "PHYSICAL_PRE_STATE",
        "v2_exec_id": v2id, "child_id": child, "manifest_hash": mh, "desc_hash": dh,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(_CAP_BRAD_PREPARE, OP_BROWSER_READ,
                          PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
                          execution_authority_hash=eah,
                          browser_session_id=browser_session_id, page_id=page_id,
                          pre_url=pre_url, pre_origin=pre_origin,
                          selector=selector, read_scope=read_scope,
                          physical_state_anchor=physical_state_anchor,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }

def pc_v2_browser_read_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE,
                         "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE,
                         "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "EXECUTOR_REQUIRED", session_id)
    v2id  = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh    = prepared_result.get("manifest_hash", "")
    dh    = prepared_result.get("desc_hash", "")
    st    = _stores(stores_base_dir)
    desc  = _load_desc(v2id, st["v2exec"])
    desc_eah_ok = (desc and desc.get("eah") == exp_eah
                   and _eah(OP_BROWSER_READ, desc.get("descriptor", {})) == exp_eah)
    if not desc_eah_ok:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    d                 = desc["descriptor"]
    stored_session_id = d.get("browser_session_id", "")
    stored_page_id    = d.get("page_id", "")
    stored_pre_url    = d.get("pre_url", "")
    stored_pre_origin = d.get("pre_origin", "")
    stored_psa        = d.get("physical_state_anchor", "")
    selector          = d.get("selector")
    read_scope        = d.get("read_scope", "FULL_PAGE")
    toctou_r = executor.read_browser_state()
    if not toctou_r.get("ok"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE,
                         "TOCTOU_READ_FAILED:" + str(toctou_r.get("error", "")), session_id)
    if toctou_r.get("closed"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "PAGE_CLOSED_AT_EXECUTE", session_id)
    current_session_id = str(toctou_r.get("browser_session_id") or "")
    current_page_id    = str(toctou_r.get("page_id") or "")
    current_url        = str(toctou_r.get("url") or "")
    current_origin     = str(toctou_r.get("origin") or _url_origin(current_url))
    _, current_psa     = _browser_read_pre_state_anchor(
        current_session_id, current_page_id, current_url, current_origin)
    if current_psa != stored_psa:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "PRE_STATE_DRIFT", session_id)
    scope_id = _sha16(f"BROWSER_READ:{read_scope}:{selector or ''}")
    apr      = _approval(v2id, child, exp_eah, scope_id + "BROWSER_READ")
    apv_id   = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "APPROVAL_STORE_FAILED", session_id)
    kx = _kx108_pre(v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_BROWSER_READ,
                    kxpre=st["kxpre"], physical_state_anchor=stored_psa,
                    state_anchor_kind="PHYSICAL_PRE_STATE")
    if not kx.get("verify_ok"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)
    read_r = executor.read_page(selector)
    if not read_r.get("ok"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE,
                         "READ_PAGE_FAILED:" + str(read_r.get("error", "")), session_id)
    if read_r.get("closed"):
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "PAGE_CLOSED_DURING_READ", session_id)
    post_page_id = str(read_r.get("page_id") or "")
    post_session_id = str(read_r.get("browser_session_id") or "")
    if not post_session_id:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "POST_SESSION_ID_MISSING", session_id)
    if not post_page_id:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "POST_PAGE_ID_MISSING", session_id)
    if post_session_id != stored_session_id:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "POST_SESSION_ID_DRIFT", session_id)
    if post_page_id != stored_page_id:
        return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "POST_PAGE_ID_DRIFT", session_id)
    if selector is not None:
        element_count = read_r.get("element_count")
        if element_count is None:
            return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE,
                             "SELECTOR_COUNT_UNAVAILABLE", session_id)
        if element_count == 0:
            return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "SELECTOR_NO_MATCH", session_id)
        if element_count > 1:
            return _exec_rej(OP_BROWSER_READ, _CAP_BRAD_EXECUTE, "SELECTOR_AMBIGUOUS", session_id)
    text           = str(read_r.get("text") or "")
    text_sha256    = _sha256(text.encode("utf-8"))
    content_length = len(text)
    post_url       = str(read_r.get("url") or "")
    post_origin    = str(read_r.get("origin") or _url_origin(post_url))
    return {
        "status": EXECUTED_OK, "j5_phase": "EXECUTE",
        "operation_type": OP_BROWSER_READ, "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate, "human_authorization_consumed": True,
        "browser_session_id": stored_session_id, "page_id": stored_page_id,
        "url": post_url, "origin": post_origin,
        "title": read_r.get("title"),
        "selector": selector, "read_scope": read_scope,
        "text": text,
        "text_sha256": text_sha256, "content_length": content_length,
        "element_count": read_r.get("element_count"),
        "proof_strength": "STRONG", "read_observed_proof": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(_CAP_BRAD_EXECUTE, OP_BROWSER_READ, EXECUTED_OK, session_id,
                          kx108_pre_gate=gate,
                          browser_session_id=stored_session_id, page_id=stored_page_id,
                          pre_url=stored_pre_url, url=post_url, origin=post_origin,
                          selector=selector, read_scope=read_scope,
                          text_sha256=text_sha256, content_length=content_length,
                          proof_strength="STRONG", read_observed_proof=True,
                          physical_state_anchor=stored_psa,
                          state_anchor_kind="PHYSICAL_PRE_STATE"),
    }


# ============================
# GOVERNED_AUDIO_VOLUME
# ============================
def _audio_state_anchor(volume_percent: int, muted: bool) -> str:
    raw = json.dumps(
        {
            "anchor_schema": "AUDIO_MASTER_VOLUME_PRE_STATE_V0",
            "scope_id": "OS_AUDIO:MASTER_VOLUME",
            "volume_percent": int(volume_percent),
            "muted": bool(muted),
        },
        sort_keys=True,
    ).encode()
    return _sha256(raw)


def pc_v2_audio_volume_prepare(
        delta=None, percent=None, *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_AUDIO_VOLUME, _CAP_AVOL_PREPARE, "EXECUTOR_REQUIRED", session_id)
    has_delta = isinstance(delta, int) and not isinstance(delta, bool)
    has_percent = isinstance(percent, int) and not isinstance(percent, bool)
    if has_delta == has_percent:
        return _prep_rej(OP_AUDIO_VOLUME, _CAP_AVOL_PREPARE, "EXACTLY_ONE_VOLUME_TARGET_REQUIRED", session_id)

    pre = executor.audio_status()
    if not pre.get("ok"):
        return _prep_rej(
            OP_AUDIO_VOLUME, _CAP_AVOL_PREPARE,
            "PRE_STATE_READ_FAILED:" + str(pre.get("error", "")), session_id,
        )
    before = pre.get("volume_percent")
    muted = pre.get("muted")
    if not isinstance(before, int) or not 0 <= before <= 100:
        return _prep_rej(OP_AUDIO_VOLUME, _CAP_AVOL_PREPARE, "PRE_STATE_INVALID", session_id)

    if has_delta:
        target = max(0, min(100, before + int(delta)))
        request_kind = "DELTA"
        request_value = int(delta)
    else:
        if not 0 <= int(percent) <= 100:
            return _prep_rej(OP_AUDIO_VOLUME, _CAP_AVOL_PREPARE, "TARGET_OUT_OF_RANGE", session_id)
        target = int(percent)
        request_kind = "ABSOLUTE"
        request_value = int(percent)

    scope_id = "OS_AUDIO:MASTER_VOLUME"
    psa = _audio_state_anchor(before, bool(muted))
    desc = {
        "scope_id": scope_id,
        "pre_volume_percent": before,
        "pre_muted": bool(muted),
        "target_volume_percent": target,
        "request_kind": request_kind,
        "request_value": request_value,
        "physical_state_anchor": psa,
        "session_id": session_id,
        "operation_type": OP_AUDIO_VOLUME,
    }
    st = _stores(stores_base_dir)
    eah = _eah(OP_AUDIO_VOLUME, desc)
    child = _v2id("chd", eah + scope_id)
    v2id = _v2id("v2x", eah + session_id)
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_AUDIO_VOLUME, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_AUDIO_VOLUME,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "scope_id": scope_id,
        "pre_volume_percent": before,
        "target_volume_percent": target,
        "physical_state_anchor": psa,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_AVOL_PREPARE, OP_AUDIO_VOLUME,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah,
            scope_id=scope_id,
            pre_volume_percent=before,
            target_volume_percent=target,
            physical_state_anchor=psa,
        ),
    }


def pc_v2_audio_volume_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "EXECUTOR_REQUIRED", session_id)

    st = _stores(stores_base_dir)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    desc_rec = _load_desc(v2id, st["v2exec"])
    if not desc_rec or desc_rec.get("eah") != exp_eah:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)
    desc = desc_rec.get("descriptor", {})
    if _eah(OP_AUDIO_VOLUME, desc) != exp_eah:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "DESCRIPTOR_EAH_RECOMPUTE_MISMATCH", session_id)

    scope_id = desc.get("scope_id", "")
    target = desc.get("target_volume_percent")
    before = desc.get("pre_volume_percent")
    stored_psa = desc.get("physical_state_anchor", "")
    if scope_id != "OS_AUDIO:MASTER_VOLUME" or not isinstance(target, int) or not 0 <= target <= 100:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "DESCRIPTOR_INVALID", session_id)

    current = executor.audio_status()
    if not current.get("ok"):
        return _exec_rej(
            OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE,
            "PRE_STATE_READ_FAILED:" + str(current.get("error", "")), session_id,
        )
    current_volume = current.get("volume_percent")
    current_muted = bool(current.get("muted"))
    if not isinstance(current_volume, int):
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "PRE_STATE_INVALID", session_id)
    current_psa = _audio_state_anchor(current_volume, current_muted)
    if current_psa != stored_psa:
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "PRE_STATE_DRIFT", session_id)

    apr = _approval(v2id, child, exp_eah, scope_id + ":" + str(target))
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "APPROVAL_STORE_FAILED", session_id)

    kx = _kx108_pre(
        v2id, child, exp_eah, apv_id, dh, "", mh, [scope_id], OP_AUDIO_VOLUME,
        kxpre=st["kxpre"],
        physical_state_anchor=stored_psa,
        state_anchor_kind="PHYSICAL_PRE_STATE",
    )
    if not kx.get("verify_ok"):
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)

    ex = executor.set_volume(target)
    if not ex.get("ok"):
        return _exec_rej(
            OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE,
            "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error", "")), session_id,
        )

    post = executor.audio_status()
    if not post.get("ok"):
        return _exec_rej(OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE, "POST_STATE_READ_FAILED", session_id)
    after = post.get("volume_percent")
    if after != target:
        return _exec_rej(
            OP_AUDIO_VOLUME, _CAP_AVOL_EXECUTE,
            "REALIZED_STATE_MISMATCH:expected=%s,got=%s" % (target, after),
            session_id,
        )

    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_AUDIO_VOLUME,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "scope_id": scope_id,
        "pre_volume_percent": before,
        "post_volume_percent": after,
        "target_volume_percent": target,
        "rollback_volume_percent": before,
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "executor_capability": "audio.set_volume",
        "receipt": _rcpt(
            _CAP_AVOL_EXECUTE, OP_AUDIO_VOLUME, EXECUTED_OK, session_id,
            kx108_pre_gate=gate,
            scope_id=scope_id,
            pre_volume_percent=before,
            post_volume_percent=after,
            target_volume_percent=target,
            rollback_volume_percent=before,
            proof_strength="STRONG",
            realized_state_verified=True,
        ),
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
        _CAP_SCHK_PREPARE:   pc_v2_uia_set_checked_prepare,
        _CAP_SCHK_EXECUTE:   pc_v2_uia_set_checked_execute,
        _CAP_SRAD_PREPARE:   pc_v2_uia_select_radio_prepare,
        _CAP_SRAD_EXECUTE:   pc_v2_uia_select_radio_execute,
        _CAP_STAB_PREPARE:   pc_v2_uia_select_tab_prepare,
        _CAP_STAB_EXECUTE:   pc_v2_uia_select_tab_execute,
        _CAP_BNAV_PREPARE:   pc_v2_browser_navigate_prepare,
        _CAP_BNAV_EXECUTE:   pc_v2_browser_navigate_execute,
        _CAP_BRAD_PREPARE:   pc_v2_browser_read_prepare,
        _CAP_BRAD_EXECUTE:   pc_v2_browser_read_execute,
        _CAP_BLINK_PREPARE:  pc_v2_browser_activate_link_prepare,
        _CAP_BLINK_EXECUTE:  pc_v2_browser_activate_link_execute,
        _CAP_BDISC_PREPARE:  pc_v2_browser_set_disclosure_prepare,
        _CAP_BDISC_EXECUTE:  pc_v2_browser_set_disclosure_execute,
        _CAP_BCHK_PREPARE:   pc_v2_browser_set_checked_prepare,
        _CAP_BCHK_EXECUTE:   pc_v2_browser_set_checked_execute,
        _CAP_BRDO_PREPARE:   pc_v2_browser_select_radio_prepare,
        _CAP_BRDO_EXECUTE:   pc_v2_browser_select_radio_execute,
        _CAP_BOPT_PREPARE:   pc_v2_browser_select_option_prepare,
        _CAP_BOPT_EXECUTE:   pc_v2_browser_select_option_execute,
        _CAP_BFLD_PREPARE:   pc_v2_browser_set_field_value_prepare,
        _CAP_BFLD_EXECUTE:   pc_v2_browser_set_field_value_execute,
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
        "operations": [OP_CREATE_FILE, OP_MOVE_FILE, OP_APPLY_PATCH, OP_CREATE_DIR, OP_WINDOW_FOCUS, OP_APP_OPEN, OP_AUDIO_VOLUME, OP_UIA_SET_TEXT, OP_UIA_SET_CHECKED, OP_UIA_SELECT_RADIO, OP_UIA_SELECT_TAB, OP_BROWSER_NAVIGATE, OP_BROWSER_READ, OP_BROWSER_ACTIVATE_LINK, OP_BROWSER_SET_DISCLOSURE, OP_BROWSER_SET_CHECKED, OP_BROWSER_SELECT_RADIO, OP_BROWSER_SELECT_OPTION, OP_BROWSER_SET_FIELD_VALUE],
        "new_parallel_mutation_engine": False,
        "generic_write_file_enabled": False,
        "openjarvis_authority": JARVIS_AUTHORITY,
        "kx108_only": True,
    }

# === G13 governed media ===
import uuid as _g13_uuid

OP_MEDIA_CONTROL = "V2_MEDIA_CONTROL"
_CAP_MEDIA_PREPARE = "PC_V2_MEDIA_CONTROL_PREPARE"
_CAP_MEDIA_EXECUTE = "PC_V2_MEDIA_CONTROL_EXECUTE"

def pc_v2_media_control_prepare(action, *, stores_base_dir, session_id="", executor=None):
    if executor is None:
        return _prep_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_PREPARE, "EXECUTOR_REQUIRED", session_id)
    allowed = {
        "play_pause": "media.play_pause",
        "next": "media.next",
        "previous": "media.previous",
    }
    capability = allowed.get(str(action or "").strip().lower())
    if capability is None:
        return _prep_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_PREPARE, "MEDIA_ACTION_UNSUPPORTED", session_id)

    st = _stores(stores_base_dir)
    invocation_id = _g13_uuid.uuid4().hex
    desc = {
        "action": action,
        "capability": capability,
        "session_id": session_id,
        "invocation_id": invocation_id,
        "operation_type": OP_MEDIA_CONTROL,
    }
    eah = _eah(OP_MEDIA_CONTROL, desc)
    child = _v2id("chd", eah + capability + invocation_id)
    v2id = _v2id("v2x", eah + session_id + invocation_id)
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_MEDIA_CONTROL, eah, desc, st["v2exec"])
    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_MEDIA_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "capability": capability,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_MEDIA_PREPARE,
            OP_MEDIA_CONTROL,
            PREPARED_AWAITING_HUMAN_APPROVAL,
            session_id,
            execution_authority_hash=eah,
            capability=capability,
        ),
    }


def pc_v2_media_control_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)

    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "EXECUTOR_REQUIRED", session_id)

    st = _stores(stores_base_dir)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    desc_rec = _load_desc(v2id, st["v2exec"])
    if not desc_rec or desc_rec.get("eah") != exp_eah:
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)

    desc = desc_rec["descriptor"]
    capability = desc["capability"]

    apr = _approval(v2id, child, exp_eah, capability)
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "APPROVAL_STORE_FAILED", session_id)

    kx = _kx108_pre(
        v2id, child, exp_eah, apv_id, dh, "", mh,
        [f"OS_MEDIA:{capability}"], OP_MEDIA_CONTROL, kxpre=st["kxpre"],
        physical_state_anchor="MEDIA_COMMAND",
        state_anchor_kind="PHYSICAL_PRE_STATE",
    )
    if not kx.get("verify_ok"):
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)

    ex = executor.media_execute(capability)
    if not ex.get("ok"):
        return _exec_rej(
            OP_MEDIA_CONTROL, _CAP_MEDIA_EXECUTE,
            "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error") or ex.get("message") or ""),
            session_id,
        )

    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_MEDIA_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "capability": capability,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_MEDIA_EXECUTE,
            OP_MEDIA_CONTROL,
            EXECUTED_OK,
            session_id,
            kx108_pre_gate=gate,
            capability=capability,
        ),
    }

# === G13 governed connectivity ===
import uuid as _g13_conn_uuid
import time as _g13_conn_time

OP_CONNECTIVITY_CONTROL = "V2_CONNECTIVITY_CONTROL"
_CAP_CONN_PREPARE = "PC_V2_CONNECTIVITY_CONTROL_PREPARE"
_CAP_CONN_EXECUTE = "PC_V2_CONNECTIVITY_CONTROL_EXECUTE"


def _g13_conn_observed_enabled(family, status):
    data = status.get("data") or {}
    if family == "wifi":
        adapters = data.get("adapters") or []
        if not adapters:
            return None
        states = [str(a.get("Status") or "").strip().casefold() for a in adapters]
        if any(s == "disabled" for s in states):
            return False
        if any(s in {"up", "disconnected", "connected"} for s in states):
            return True
        return None

    devices = data.get("devices") or []

    def _bt_radio_candidate(d):
        name = d.get("FriendlyName")
        instance_id = d.get("InstanceId")
        if not isinstance(name, str) or not isinstance(instance_id, str):
            return False
        folded = name.casefold()
        if instance_id.upper().startswith("BTHENUM"):
            return False
        if any(tok in folded for tok in ("enumerator", "rfcomm", "protocol", "service", "avrcp", "gatt")):
            return False
        return (
            any(tok in folded for tok in ("adapter", "radio", "bluetooth"))
            or instance_id.upper().startswith(("USB\\\\", "PCI\\\\"))
        )

    radios = [d for d in devices if _bt_radio_candidate(d)]
    if not radios:
        return None
    states = [str(d.get("Status") or "").strip().casefold() for d in radios]
    if any(s == "ok" for s in states):
        return True
    if all(s and s != "ok" for s in states):
        return False
    return None


def pc_v2_connectivity_prepare(family, enabled, *, stores_base_dir, session_id="", executor=None):
    family = str(family or "").strip().lower()
    if family not in {"wifi", "bluetooth"}:
        return _prep_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_PREPARE, "CONNECTIVITY_FAMILY_UNSUPPORTED", session_id)
    if not isinstance(enabled, bool):
        return _prep_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_PREPARE, "ENABLED_BOOL_REQUIRED", session_id)
    if executor is None:
        return _prep_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_PREPARE, "EXECUTOR_REQUIRED", session_id)

    pre = executor.connectivity_status(family)
    if not pre.get("ok"):
        return _prep_rej(
            OP_CONNECTIVITY_CONTROL, _CAP_CONN_PREPARE,
            "PRE_STATE_READ_FAILED:" + str(pre.get("error") or pre.get("message") or ""),
            session_id,
        )

    invocation_id = _g13_conn_uuid.uuid4().hex
    pre_enabled = _g13_conn_observed_enabled(family, pre)
    desc = {
        "family": family,
        "enabled": enabled,
        "pre_enabled": pre_enabled,
        "session_id": session_id,
        "invocation_id": invocation_id,
        "operation_type": OP_CONNECTIVITY_CONTROL,
    }
    eah = _eah(OP_CONNECTIVITY_CONTROL, desc)
    child = _v2id("chd", eah + family + invocation_id)
    v2id = _v2id("v2x", eah + session_id + invocation_id)
    mh = _sha16(json.dumps(desc, sort_keys=True))
    dh = _persist_desc(v2id, OP_CONNECTIVITY_CONTROL, eah, desc, _stores(stores_base_dir)["v2exec"])

    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_CONNECTIVITY_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "family": family,
        "enabled": enabled,
        "pre_enabled": pre_enabled,
        "_stores_base_dir": str(stores_base_dir),
        "receipt": _rcpt(
            _CAP_CONN_PREPARE, OP_CONNECTIVITY_CONTROL,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            execution_authority_hash=eah, family=family, enabled=enabled,
            pre_enabled=pre_enabled,
        ),
    }


def pc_v2_connectivity_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)

    exp_eah = prepared_result.get("execution_authority_hash", "")
    if not exp_eah or human_authorized_eah != exp_eah:
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "EXECUTOR_REQUIRED", session_id)

    st = _stores(stores_base_dir)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    rec = _load_desc(v2id, st["v2exec"])
    if not rec or rec.get("eah") != exp_eah:
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)

    desc = rec["descriptor"]
    family = desc["family"]
    enabled = bool(desc["enabled"])

    pre_now = executor.connectivity_status(family)
    if not pre_now.get("ok"):
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "PRE_STATE_RECHECK_FAILED", session_id)
    pre_now_enabled = _g13_conn_observed_enabled(family, pre_now)
    if desc.get("pre_enabled") is not None and pre_now_enabled != desc.get("pre_enabled"):
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "PRE_STATE_DRIFT", session_id)

    apr = _approval(v2id, child, exp_eah, f"{family}:{enabled}")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "APPROVAL_STORE_FAILED", session_id)

    kx = _kx108_pre(
        v2id, child, exp_eah, apv_id, dh, "", mh,
        [f"OS_CONNECTIVITY:{family}"], OP_CONNECTIVITY_CONTROL, kxpre=st["kxpre"],
        physical_state_anchor=f"{family}:{pre_now_enabled}",
        state_anchor_kind="PHYSICAL_PRE_STATE",
    )
    if not kx.get("verify_ok"):
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)

    ex = executor.connectivity_set(family, enabled)
    if not ex.get("ok"):
        return _exec_rej(
            OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE,
            "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error") or ex.get("message") or ""),
            session_id,
        )

    post = None
    post_enabled = None
    # Windows network/PnP state can settle asynchronously after the mutation.
    # Re-read a bounded number of times; never convert an unresolved state into PASS.
    for _attempt in range(6):
        post = executor.connectivity_status(family)
        if not post.get("ok"):
            return _exec_rej(OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE, "POST_STATE_READ_FAILED", session_id)
        post_enabled = _g13_conn_observed_enabled(family, post)
        if post_enabled is enabled:
            break
        _g13_conn_time.sleep(0.5)

    if post_enabled is not enabled:
        return _exec_rej(
            OP_CONNECTIVITY_CONTROL, _CAP_CONN_EXECUTE,
            "REALIZED_STATE_MISMATCH:" + str(post_enabled),
            session_id,
        )

    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_CONNECTIVITY_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "family": family,
        "pre_enabled": pre_now_enabled,
        "post_enabled": post_enabled,
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "executor_provider": executor.EXECUTOR_PROVIDER,
        "executor_backend": executor.EXECUTOR_BACKEND,
        "receipt": _rcpt(
            _CAP_CONN_EXECUTE, OP_CONNECTIVITY_CONTROL, EXECUTED_OK, session_id,
            kx108_pre_gate=gate, family=family, enabled=enabled,
            pre_enabled=pre_now_enabled, post_enabled=post_enabled,
        ),
    }

# === G13 governed window control ===
import uuid as _g13_window_uuid

OP_WINDOW_CONTROL = "V2_WINDOW_CONTROL"
_CAP_WINDOW_CONTROL_PREPARE = "PC_V2_WINDOW_CONTROL_PREPARE"
_CAP_WINDOW_CONTROL_EXECUTE = "PC_V2_WINDOW_CONTROL_EXECUTE"


def pc_v2_window_control_prepare(
        action, title, *, stores_base_dir, session_id="", monitor_index=None, executor=None):
    if executor is None:
        return _prep_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_PREPARE, "EXECUTOR_REQUIRED", session_id)

    action = str(action or "").strip().lower()
    if action not in {"minimize", "maximize", "restore", "move_monitor"}:
        return _prep_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_PREPARE, "WINDOW_ACTION_UNSUPPORTED", session_id)

    if action == "move_monitor" and (not isinstance(monitor_index, int) or monitor_index < 1):
        return _prep_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_PREPARE, "MONITOR_INDEX_REQUIRED", session_id)

    resolved = executor.find_window(str(title or "").strip())
    if not resolved.get("ok"):
        return _prep_rej(
            OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_PREPARE,
            str(resolved.get("error") or "WINDOW_NOT_FOUND"), session_id,
        )

    invocation_id = _g13_window_uuid.uuid4().hex
    hwnd = int(resolved["hwnd"])
    obs = executor.window_observe(hwnd)
    if not obs.get("ok"):
        return _prep_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_PREPARE, "WINDOW_PRE_STATE_READ_FAILED", session_id)

    desc = {
        "action": action,
        "title": title,
        "resolved_title": resolved.get("title") or title,
        "hwnd": hwnd,
        "monitor_index": monitor_index,
        "pre_state": obs,
        "session_id": session_id,
        "invocation_id": invocation_id,
        "operation_type": OP_WINDOW_CONTROL,
    }
    eah = _eah(OP_WINDOW_CONTROL, desc)
    child = _v2id("chd", eah + str(hwnd) + invocation_id)
    v2id = _v2id("v2x", eah + session_id + invocation_id)
    mh = _sha16(json.dumps(desc, sort_keys=True, default=str))
    dh = _persist_desc(v2id, OP_WINDOW_CONTROL, eah, desc, _stores(stores_base_dir)["v2exec"])

    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "operation_type": OP_WINDOW_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "execution_authority_hash": eah,
        "v2_exec_id": v2id,
        "child_id": child,
        "manifest_hash": mh,
        "desc_hash": dh,
        "action": action,
        "resolved_title": desc["resolved_title"],
        "hwnd": hwnd,
        "monitor_index": monitor_index,
        "receipt": _rcpt(
            _CAP_WINDOW_CONTROL_PREPARE, OP_WINDOW_CONTROL,
            PREPARED_AWAITING_HUMAN_APPROVAL, session_id,
            action=action, resolved_title=desc["resolved_title"], hwnd=hwnd,
            monitor_index=monitor_index,
        ),
    }


def pc_v2_window_control_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, session_id="", executor=None):
    if prepared_result.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED", session_id)
    if prepared_result.get("j5_phase") != "PREPARE":
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "PREPARE_PHASE_REQUIRED", session_id)

    exp_eah = prepared_result.get("execution_authority_hash", "")
    if human_authorized_eah != exp_eah:
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, EAH_MISMATCH, session_id)
    if not (human_authorization_reference or "").strip():
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED", session_id)
    if executor is None:
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "EXECUTOR_REQUIRED", session_id)

    st = _stores(stores_base_dir)
    v2id = prepared_result.get("v2_exec_id", "")
    child = prepared_result.get("child_id", "")
    mh = prepared_result.get("manifest_hash", "")
    dh = prepared_result.get("desc_hash", "")
    rec = _load_desc(v2id, st["v2exec"])
    if not rec or rec.get("eah") != exp_eah:
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "DESCRIPTOR_EAH_MISMATCH", session_id)

    desc = rec["descriptor"]
    hwnd = int(desc["hwnd"])
    action = desc["action"]
    monitor_index = desc.get("monitor_index")

    pre_now = executor.window_observe(hwnd)
    if not pre_now.get("ok"):
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "WINDOW_PRE_STATE_DRIFT", session_id)

    apr = _approval(v2id, child, exp_eah, f"{action}:{hwnd}")
    apv_id = apr["approval_id"]
    ar = _E.store_approval_artifact(apr, st["approval"])
    if ar.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "APPROVAL_STORE_FAILED", session_id)

    kx = _kx108_pre(
        v2id, child, exp_eah, apv_id, dh, "", mh,
        [f"OS_WINDOW:{action}"], OP_WINDOW_CONTROL, kxpre=st["kxpre"],
        physical_state_anchor=f"{hwnd}:{pre_now.get('is_iconic')}:{pre_now.get('is_zoomed')}:{pre_now.get('rect')}",
        state_anchor_kind="PHYSICAL_PRE_STATE",
    )
    if not kx.get("verify_ok"):
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "KX108_PRE_FAILED", session_id)
    gate = kx.get("x108_gate", "")
    if gate != "ALLOW":
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "KX108_PRE_GATE:" + gate, session_id)

    ex = executor.window_control_by_hwnd(hwnd, action, monitor_index)
    if not ex.get("ok"):
        return _exec_rej(
            OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE,
            "JARJAR_EXECUTOR_FAILED:" + str(ex.get("error") or ""),
            session_id,
        )

    post = executor.window_observe(hwnd)
    if not post.get("ok"):
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "POST_STATE_READ_FAILED", session_id)

    verified = False
    if action == "minimize":
        verified = post.get("is_iconic") is True
    elif action == "maximize":
        verified = post.get("is_zoomed") is True
    elif action == "restore":
        verified = post.get("is_iconic") is False and post.get("is_zoomed") is False
    elif action == "move_monitor":
        before_rect = tuple(desc.get("pre_state", {}).get("rect") or ())
        after_rect = tuple(post.get("rect") or ())
        verified = bool(before_rect and after_rect and before_rect != after_rect)

    if not verified:
        return _exec_rej(OP_WINDOW_CONTROL, _CAP_WINDOW_CONTROL_EXECUTE, "REALIZED_STATE_MISMATCH", session_id)

    return {
        "status": EXECUTED_OK,
        "j5_phase": "EXECUTE",
        "operation_type": OP_WINDOW_CONTROL,
        "jarvis_authority": JARVIS_AUTHORITY,
        "decision_authority": KX_DECISION_AUTHORITY,
        "kx108_pre_gate": gate,
        "human_authorization_consumed": True,
        "action": action,
        "resolved_title": desc.get("resolved_title"),
        "hwnd": hwnd,
        "monitor_index": monitor_index,
        "proof_strength": "STRONG",
        "realized_state_verified": True,
        "post_state": post,
        "receipt": _rcpt(
            _CAP_WINDOW_CONTROL_EXECUTE, OP_WINDOW_CONTROL, EXECUTED_OK, session_id,
            kx108_pre_gate=gate, action=action, hwnd=hwnd,
            monitor_index=monitor_index, realized_state_verified=True,
        ),
    }
