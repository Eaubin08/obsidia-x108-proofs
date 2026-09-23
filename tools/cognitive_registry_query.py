#!/usr/bin/env python3
"""Readonly query utility for the Obsidia cognitive convergence registry.
Safety: reads JSON only; performs no writes, imports no runtime modules, touches no git, opens no network, invokes no KX108/provider/model, and executes no referenced file.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'docs/architecture/cognitive_convergence/COGNITIVE_CONVERGENCE_MASTER_REGISTRY.json'
FIELDS=('id','canonical_name','aliases','summary','role','source_locations','code_locations','documentation_locations','historical_locations','target_layer','target_hook','target_layer_candidate','blockers','next_action')
def load_entries(): return list(json.loads(REGISTRY.read_text(encoding='utf-8')).get('entries',[]))
def flat(v:Any)->str:
    if v is None: return ''
    if isinstance(v,list): return ' '.join(flat(x) for x in v)
    if isinstance(v,dict): return ' '.join(f'{k} {flat(x)}' for k,x in v.items())
    return str(v)
def match(e,needle):
    n=needle.lower(); return any(n in flat(e.get(f)).lower() for f in FIELDS)
def row(e):
    target=e.get('target_hook') or e.get('target_layer') or e.get('target_layer_candidate') or 'UNRESOLVED'
    blocker='; '.join(e.get('blockers') or []) or e.get('required_audit') or '-'
    locs=e.get('code_locations') or e.get('source_locations') or e.get('documentation_locations') or ['-']
    return f"{e.get('id'):<28} {e.get('status'):<32} {e.get('component_type'):<18} target={target} loc={locs[0]} blocker={blocker}"
def main():
    p=argparse.ArgumentParser(description='Query the Obsidia cognitive convergence registry (readonly).')
    p.add_argument('--find'); p.add_argument('--status'); p.add_argument('--target'); p.add_argument('--blocked',action='store_true'); p.add_argument('--unresolved',action='store_true'); p.add_argument('--all',action='store_true')
    a=p.parse_args(); r=load_entries()
    if a.find: r=[e for e in r if match(e,a.find)]
    if a.status: r=[e for e in r if str(e.get('status','')).upper()==a.status.upper()]
    if a.target:
        t=a.target.lower(); r=[e for e in r if t in flat([e.get('target_layer'),e.get('target_hook'),e.get('target_layer_candidate')]).lower()]
    if a.blocked: r=[e for e in r if str(e.get('status','')).startswith('BLOCKED')]
    if a.unresolved: r=[e for e in r if e.get('target_hook_status')=='UNRESOLVED']
    if not any([a.find,a.status,a.target,a.blocked,a.unresolved,a.all]): p.error('provide --find, --status, --target, --blocked, --unresolved, or --all')
    print(f'REGISTRY={REGISTRY}'); print(f'RESULTS={len(r)}')
    for e in r: print(row(e))
if __name__=='__main__': main()
