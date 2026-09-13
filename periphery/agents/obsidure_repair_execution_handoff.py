import hashlib,os,re
from pathlib import Path
from typing import Any

AUTHORITY="NON_SOVEREIGN"
OPERATION_TYPE="UPDATE_TARGET_FROM_SOURCE"
SOURCE_KIND="REPAIR_SANDBOX_FILE"
STATUS_READY="REPAIR_HANDOFF_READY"
STATUS_HOLD="REPAIR_HANDOFF_HOLD"
_ACCEPTABLE_C278=frozenset({"CONTINUOUS"})
_HEX64=re.compile(r'^[0-9a-f]{64}$')

def _hold(reason,**extra):
    return {"status":STATUS_HOLD,"reason":reason,"child":None,
            "authority":AUTHORITY,"write_capability":False,**extra}

def _sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()


def _g(obj,attr,default=""):
    if isinstance(obj,dict): return obj.get(attr,default)
    return getattr(obj,attr,default)

def build_repair_execution_handoff(*,request,proposal,c278_evidence,verdict,repo_root=None):
    root=Path(repo_root).resolve() if repo_root else Path(".").resolve()
    proposal_id=str(_g(proposal,"proposal_id") or "")
    req_request_id=str(_g(request,"request_id") or "")
    if c278_evidence is None: return _hold("C278_EVIDENCE_ABSENT",proposal_id=proposal_id)
    c278_ev=_g(c278_evidence,"evidence",None)
    if c278_ev is None: return _hold("C278_EVIDENCE_MALFORMED",proposal_id=proposal_id)
    if c278_ev not in _ACCEPTABLE_C278:
        return _hold("C278_EVIDENCE_NOT_CONTINUOUS",c278_evidence=c278_ev,proposal_id=proposal_id)
    c278_req_id=str(_g(c278_evidence,"request_id") or "")
    c278_prop_id=str(_g(c278_evidence,"proposal_id") or "")
    if not c278_req_id: return _hold("C278_REQUEST_ID_ABSENT")
    if not c278_prop_id: return _hold("C278_PROPOSAL_ID_ABSENT")
    if c278_req_id!=req_request_id: return _hold("C278_REQUEST_ID_MISMATCH",c278=c278_req_id,expected=req_request_id)
    if c278_prop_id!=proposal_id: return _hold("C278_PROPOSAL_ID_MISMATCH",c278=c278_prop_id,expected=proposal_id)
    verdict_id=str(_g(verdict,"verdict_id") or "")
    verdict_status=str(_g(verdict,"status") or "")
    sandbox_dir_str=str(_g(verdict,"sandbox_dir") or "")
    if verdict_status!="PASS":
        return _hold("VERDICT_NOT_PASS",verdict_status=verdict_status,proposal_id=proposal_id,verdict_id=verdict_id)
    vp_id=str(_g(verdict,"proposal_id") or "")
    vr_id=str(_g(verdict,"request_id") or "")
    if not verdict_id: return _hold("VERDICT_ID_ABSENT")
    if not vp_id: return _hold("VERDICT_PROPOSAL_ID_ABSENT",verdict_id=verdict_id)
    if not vr_id: return _hold("VERDICT_REQUEST_ID_ABSENT",verdict_id=verdict_id)
    if vp_id!=proposal_id: return _hold("PROVENANCE_MISMATCH_PROPOSAL_ID",expected=proposal_id,actual=vp_id)
    if vr_id!=req_request_id: return _hold("PROVENANCE_MISMATCH_REQUEST_ID",expected=req_request_id,actual=vr_id)
    candidate_files=list(_g(proposal,"candidate_files") or [])
    if len(candidate_files)==0: return _hold("NO_CANDIDATE_FILES",proposal_id=proposal_id)
    if len(candidate_files)>1: return _hold("MULTI_PATCH_AMBIGUITY",patch_count=len(candidate_files),proposal_id=proposal_id)
    cand=candidate_files[0]
    bs=chr(92)
    target_rel=str(_g(cand,"path") or "").replace(bs,"/").lstrip("./")
    if not target_rel: return _hold("CANDIDATE_PATH_MISSING")
    if not sandbox_dir_str: return _hold("SANDBOX_DIR_ABSENT",verdict_id=verdict_id)
    sb=Path(sandbox_dir_str)
    src=sb/target_rel
    try: resolved_sb=sb.resolve(); resolved_src=src.resolve()
    except OSError as exc: return _hold(f"SANDBOX_PATH_UNRESOLVABLE:{exc}")
    try: resolved_src.relative_to(resolved_sb)
    except ValueError: return _hold("SANDBOX_PATH_ESCAPE",resolved=str(resolved_src))
    if os.path.islink(str(src)): return _hold("SANDBOX_SYMLINK_REJECTED",path=str(src))
    if not resolved_src.exists(): return _hold("SANDBOX_FILE_MISSING",resolved=str(resolved_src))
    if not resolved_src.is_file(): return _hold("SANDBOX_NOT_REGULAR_FILE",resolved=str(resolved_src))
    try: src_bytes=resolved_src.read_bytes()
    except OSError as exc: return _hold(f"SANDBOX_UNREADABLE:{exc}")
    current_sha256=_sha256(src_bytes)
    tested_artifacts=list(_g(verdict,"tested_artifacts") or [])
    expected_sha256=None
    for art in tested_artifacts:
        art_path=str(_g(art,"path") or "").replace(chr(92),"/").lstrip("./")
        if art_path==target_rel:
            expected_sha256=str(_g(art,"sha256") or "")
            break
    if not expected_sha256:
        return _hold("TESTED_ARTIFACT_SHA256_ABSENT",path=target_rel,verdict_id=verdict_id)
    if not _HEX64.match(expected_sha256):
        return _hold("TESTED_ARTIFACT_SHA256_MALFORMED",path=target_rel,sha256_len=len(expected_sha256))
    if current_sha256!=expected_sha256:
        return _hold("SANDBOX_BYTES_CHANGED_SINCE_VERDICT",path=target_rel,
                     expected=expected_sha256[:16],actual=current_sha256[:16])
    source_content_sha256=current_sha256
    target_abs=root/target_rel
    base_sha256=str(_g(cand,"base_sha256") or "")
    if target_abs.exists() and target_abs.is_file():
        try: target_pre_sha256=_sha256(target_abs.read_bytes())
        except OSError as exc: return _hold(f"TARGET_UNREADABLE:{exc}")
        if base_sha256 and target_pre_sha256!=base_sha256:
            return _hold("TARGET_DRIFT_SINCE_REPAIR_TEST",path=target_rel,
                         base=base_sha256[:16],current=target_pre_sha256[:16])
    elif target_abs.exists(): return _hold("TARGET_NOT_REGULAR_FILE",path=target_rel)
    else: target_pre_sha256=None
    sandbox_artifact_path=str(resolved_src)
    provenance_refs={
        "operation_type":OPERATION_TYPE,
        "repair_request_id":req_request_id,
        "repair_proposal_id":proposal_id,
        "repair_verdict_id":verdict_id,
        "c278_evidence":c278_ev,
    }
    return {
        "status":STATUS_READY,"reason":None,
        "proposal_id":proposal_id,
        "request_id":req_request_id,
        "verdict_id":verdict_id,
        "target_path":target_rel,
        "sandbox_artifact_path":sandbox_artifact_path,
        "source_content_sha256":source_content_sha256,
        "source_bytes_len":len(src_bytes),
        "target_pre_sha256":target_pre_sha256,
        "operation_type":OPERATION_TYPE,
        "operation_reason":"repair: "+target_rel,
        "provenance_refs":provenance_refs,
        "authority":AUTHORITY,
        "write_capability":False,
        "handoff_report":{
            "target_path":target_rel,"operation_type":OPERATION_TYPE,
            "source_kind":SOURCE_KIND,"sandbox_dir":sandbox_dir_str,
            "sandbox_artifact_path":sandbox_artifact_path,
            "source_bytes":len(src_bytes),
            "target_pre_state":("EXISTS" if target_pre_sha256 else "ABSENT"),
            "c278_evidence":c278_ev,
        },
    }


__all__=["STATUS_READY","STATUS_HOLD","build_repair_execution_handoff"]
