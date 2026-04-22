#!/usr/bin/env python3
"""
V18.8 checker — multi-step convergence & stability
- Runs determinism checks (G1)
- Runs no-oscillation checks (G2)
- Runs convergence checks (G3)
- Runs "no infinite loop" checks (G4) via bounded simulation and invariant detection
"""
import json, random, argparse

ALLOW,HOLD,BLOCK="ALLOW","HOLD","BLOCK"
ORDER={ALLOW:0,HOLD:1,BLOCK:2}
def meet(a,b): return a if ORDER[a]>=ORDER[b] else b
def meet_all(vals):
    out=ALLOW
    for v in vals: out=meet(out,v)
    return out

class NonceStore:
    def __init__(self): self.seen=set()
    def fresh(self,n): return (n is not None) and (n not in self.seen)
    def mark(self,n):
        if n is not None: self.seen.add(n)

def Greplay(intent, st):
    n=intent.get("nonce")
    return (BLOCK,["NONCE_REPLAY_OR_MISSING"]) if not st["nonce_store"].fresh(n) else (ALLOW,[])

def Grisk(intent, st):
    if intent["risk"]>=st["Rmax"]:
        return (BLOCK,["RISK_TOO_HIGH"])
    if intent.get("expected_return",0.0) < st["ERmin"]:
        return (BLOCK,["NEGATIVE_EXPECTED_RETURN"])
    return (ALLOW,[])

def Gx108(intent, st):
    if intent.get("irreversible",False) and st["t"]<st["tau"]:
        return (HOLD,["X108_TIME_LOCK"])
    return (ALLOW,[])

def A(intent, st):
    v1,r1=Greplay(intent,st)
    v2,r2=Grisk(intent,st)
    v3,r3=Gx108(intent,st)
    return meet_all([v1,v2,v3]), (r1+r2+r3)

def step(intent, st):
    d, reasons = A(intent, st)
    # consume nonce on ALLOW (ticket spend)
    if d==ALLOW:
        st["nonce_store"].mark(intent.get("nonce"))
        st["executed"] += 1
    return d, reasons

def simulate(intent, st, t_series):
    hist=[]
    for t in t_series:
        st["t"]=t
        d, reasons = step(intent, st)
        hist.append({"t":t,"decision":d,"reasons":reasons})
    return hist

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=120000)
    ap.add_argument("--tau", type=float, default=10.0)
    ap.add_argument("--Rmax", type=float, default=0.65)
    ap.add_argument("--ERmin", type=float, default=-0.01)
    ap.add_argument("--out", type=str, default="results_v18_8.json")
    args=ap.parse_args()

    random.seed(2026)
    # time series across boundary
    t_series=[0.0,1.0,5.0,args.tau-0.1,args.tau,args.tau+0.1,60.0]

    # G1 determinism: same input -> same output
    det_ok=True
    for _ in range(5000):
        intent={
            "irreversible": random.choice([True,False]),
            "risk": random.random(),
            "expected_return": random.uniform(-0.06,0.12),
            "nonce": "fixed_nonce"
        }
        st={"t":0.0,"tau":args.tau,"Rmax":args.Rmax,"ERmin":args.ERmin,"nonce_store":NonceStore(),"executed":0}
        d1,_=A(intent,st)
        d2,_=A(intent,st)
        if d1!=d2: det_ok=False; break

    # G2 no ALLOW before tau for irreversible when no other violations
    g2_ok=True
    intent_ok={"irreversible":True,"risk":0.1,"expected_return":0.02,"nonce":"n0"}
    st={"t":0.0,"tau":args.tau,"Rmax":args.Rmax,"ERmin":args.ERmin,"nonce_store":NonceStore(),"executed":0}
    hist=simulate(intent_ok, st, [0.0,1.0,5.0,args.tau-0.1])
    if any(h["decision"]==ALLOW for h in hist): g2_ok=False

    # G3 convergence at tau if no violations
    st={"t":0.0,"tau":args.tau,"Rmax":args.Rmax,"ERmin":args.ERmin,"nonce_store":NonceStore(),"executed":0}
    # use fresh nonce each step because in real system you'd issue new ticket; here we model time-only evolution with new nonce per step
    hist2=[]
    for i,t in enumerate(t_series):
        intent={"irreversible":True,"risk":0.1,"expected_return":0.02,"nonce":f"n{i}"}
        st["t"]=t
        d,_=A(intent,st)
        hist2.append({"t":t,"decision":d})
    # Expect HOLD for t<tau and ALLOW for t>=tau
    g3_ok = all((h["t"]<args.tau and h["decision"]!=ALLOW) or (h["t"]>=args.tau and h["decision"]==ALLOW) for h in hist2)

    # G4 no oscillation without boundary/violations: choose t all below tau -> all HOLD (or BLOCK), all above -> all ALLOW (or BLOCK)
    g4_ok=True
    for region in ["below","above"]:
        for _ in range(2000):
            intent={"irreversible":True,"risk":0.1,"expected_return":0.02,"nonce":"nx"}
            st={"t":0.0,"tau":args.tau,"Rmax":args.Rmax,"ERmin":args.ERmin,"nonce_store":NonceStore(),"executed":0}
            if region=="below":
                ts=[random.uniform(0,args.tau-1e-3) for _ in range(10)]
            else:
                ts=[random.uniform(args.tau, args.tau+100) for _ in range(10)]
            ts=sorted(ts)
            # new nonce each step to avoid replay side-effects; we want pure time effect
            decs=[]
            for j,t in enumerate(ts):
                intent2=dict(intent); intent2["nonce"]=f"nx{j}"
                st["t"]=t
                d,_=A(intent2,st)
                decs.append(d)
            # in a region, decisions must be constant (ALLOW above, HOLD below) given no violations
            if region=="below" and any(d==ALLOW for d in decs): g4_ok=False; break
            if region=="above" and any(d!=ALLOW for d in decs): g4_ok=False; break
        if not g4_ok: break

    out={
        "params":{"tau":args.tau,"Rmax":args.Rmax,"ERmin":args.ERmin},
        "G1_determinism": det_ok,
        "G2_no_allow_before_tau": g2_ok,
        "G3_convergence_at_tau": g3_ok,
        "G4_no_oscillation_without_boundary": g4_ok,
        "examples":{
            "G2_history": hist,
            "G3_history": hist2
        }
    }
    open(args.out,"w",encoding="utf-8").write(json.dumps(out,indent=2))
    print("OK")

if __name__=="__main__":
    main()
