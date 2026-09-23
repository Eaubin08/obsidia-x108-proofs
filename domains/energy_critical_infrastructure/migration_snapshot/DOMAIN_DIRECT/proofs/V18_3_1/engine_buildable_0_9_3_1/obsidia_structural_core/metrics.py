"""
Obsidia Structural Core — graph-theoretic equilibrium gate.

Implements:
- Strong triangle detection and scoring (local closure)
- Radial hexagon detection and scoring (meso/global anchoring)
- Weighted-degree asymmetry penalty (anti-domination)
- Core-fixed evaluation for strict invariance under World changes

All graphs are treated as weighted, undirected adjacency matrices W with weights in [0,1].
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import List, Tuple, Optional, Sequence

Number = float

@dataclass(frozen=True)
class Triangle:
    i: int; j: int; k: int; score: float

@dataclass(frozen=True)
class Hexagon:
    p: int
    ring: Tuple[int,int,int,int,int,int]
    radial_mean: float
    radial_var: float
    score: float

@dataclass(frozen=True)
class Metrics:
    strong_triangles: List[Triangle]
    strong_triangle_mean: float
    best_hexagon: Optional[Hexagon]
    asymmetry: float
    S: float

def _mean(xs: List[Number]) -> float:
    return sum(xs)/len(xs) if xs else 0.0

def _var(xs: List[Number]) -> float:
    if not xs: return 0.0
    m=_mean(xs)
    return sum((x-m)**2 for x in xs)/len(xs)

def triangle_score(W: List[List[Number]], i: int, j: int, k: int) -> float:
    return (W[i][j]+W[j][k]+W[k][i])/3.0

def find_strong_triangles(W: List[List[Number]], theta_T: float) -> List[Triangle]:
    n=len(W)
    out=[]
    for i,j,k in combinations(range(n),3):
        if W[i][j]>0 and W[j][k]>0 and W[k][i]>0:
            t=triangle_score(W,i,j,k)
            if t>=theta_T:
                out.append(Triangle(i,j,k,t))
    out.sort(key=lambda t:t.score, reverse=True)
    return out

def find_best_hexagon(W: List[List[Number]], theta_R: float, theta_A: float, lam: float,
                      max_candidates_per_p: int = 2000) -> Optional[Hexagon]:
    n=len(W)
    best=None
    for p in range(n):
        cand=[h for h in range(n) if h!=p and W[p][h]>=theta_R]
        if len(cand)<6: continue
        tried=0
        for subset in combinations(cand,6):
            first=subset[0]; others=subset[1:]
            for perm in permutations(others,5):
                ring=(first,)+perm
                ok=True
                for i in range(6):
                    a=ring[i]; b=ring[(i+1)%6]
                    if W[a][b]<theta_A:
                        ok=False; break
                if not ok: continue
                radial=[W[p][h] for h in ring]
                rmean=_mean(radial); rvar=_var(radial)
                score=rmean - lam*rvar
                hx=Hexagon(p, ring, rmean, rvar, score)
                if best is None or hx.score>best.score:
                    best=hx
                tried += 1
                if tried>=max_candidates_per_p: break
            if tried>=max_candidates_per_p: break
    return best

def asymmetry_weighted_degree(W: List[List[Number]]) -> float:
    n=len(W)
    s=[sum(W[i][j] for j in range(n)) for i in range(n)]
    sbar=sum(s)/n
    return sum(abs(si-sbar) for si in s)/n

def compute_metrics(W: List[List[Number]], theta_T=0.7, theta_R=0.7, theta_A=0.6,
                    alpha=1.0, beta=1.0, gamma=1.0, lam=1.0) -> Metrics:
    strong=find_strong_triangles(W, theta_T)
    tmean=_mean([t.score for t in strong]) if strong else 0.0
    hx=find_best_hexagon(W, theta_R, theta_A, lam)
    hstar=hx.score if hx else 0.0
    A=asymmetry_weighted_degree(W)
    S=alpha*tmean + beta*hstar - gamma*A
    return Metrics(strong, tmean, hx, A, S)

def submatrix(W: List[List[Number]], nodes: Sequence[int]) -> List[List[Number]]:
    nodes=list(nodes)
    return [[W[i][j] for j in nodes] for i in nodes]

def relabel_metrics(metrics: Metrics, nodes: Sequence[int]) -> Metrics:
    nodes=list(nodes)
    strong=[Triangle(nodes[t.i], nodes[t.j], nodes[t.k], t.score) for t in metrics.strong_triangles]
    hx=None
    if metrics.best_hexagon:
        h=metrics.best_hexagon
        hx=Hexagon(nodes[h.p], tuple(nodes[x] for x in h.ring), h.radial_mean, h.radial_var, h.score)
    return Metrics(strong, metrics.strong_triangle_mean, hx, metrics.asymmetry, metrics.S)

def compute_metrics_core_fixed(W_full: List[List[Number]], core_nodes: Sequence[int], **kwargs) -> Metrics:
    Wc=submatrix(W_full, core_nodes)
    m=compute_metrics(Wc, **kwargs)
    return relabel_metrics(m, core_nodes)

def decision_act_hold(metrics: Metrics, theta_S: float) -> str:
    return "ACT" if metrics.S >= theta_S else "HOLD"
