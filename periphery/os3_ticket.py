import hashlib,json,uuid
from dataclasses import dataclass, asdict
from typing import Any
@dataclass
class OS3ProofTicket:
    ticket_id:str; action_id:str; domain:str; x108_gate:str; reason_code:str; severity:str; scores:dict[str,Any]; unknowns:list[str]; risk_flags:list[str]; contradictions:list[str]; evidence_refs:list[str]; input_hash:str; output_hash:str; trace_hash:str; merkle_root:str; replay_status:str
    def to_dict(self): return asdict(self)
def sha256_obj(obj:Any)->str: return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()
def _obj_dict(obj:Any): return dict(obj.__dict__) if hasattr(obj,'__dict__') else str(obj)
def build_os3_ticket(action_candidate:Any, packet:Any, envelope:Any)->OS3ProofTicket:
    ih=sha256_obj(_obj_dict(action_candidate)); oh=sha256_obj(_obj_dict(envelope)); th=sha256_obj({'input_hash':ih,'output_hash':oh,'packet':_obj_dict(packet)}); mr=sha256_obj([ih,oh,th])
    return OS3ProofTicket(uuid.uuid4().hex,action_candidate.action_id,action_candidate.domain,getattr(envelope,'x108_gate','UNKNOWN'),getattr(envelope,'reason_code','UNKNOWN'),getattr(envelope,'severity','INFO'),dict(getattr(envelope,'metrics',{}) or {}),list(getattr(envelope,'unknowns',[]) or []),list(getattr(envelope,'risk_flags',[]) or []),list(getattr(envelope,'contradictions',[]) or []),list(getattr(envelope,'evidence_refs',[]) or []),ih,oh,th,mr,'NOT_RUN')
def ticket_is_valid(ticket:OS3ProofTicket)->bool: return all([ticket.input_hash,ticket.output_hash,ticket.trace_hash,ticket.merkle_root])
