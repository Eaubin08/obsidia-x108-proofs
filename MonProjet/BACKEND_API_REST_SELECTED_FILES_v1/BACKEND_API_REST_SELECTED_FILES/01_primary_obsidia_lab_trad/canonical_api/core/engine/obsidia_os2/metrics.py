"""
OS2 – Structural Metrics Layer (pure, deterministic, no side-effects)

Implements:
- Triangle closure score
- Radial hexagon score
- Asymmetry penalty
- Core-fixed invariance computation
"""

from dataclasses import dataclass
from typing import List
import math

@dataclass
class Metrics:
    T_mean: float
    H_score: float
    A_score: float
    S: float

def triangle_mean(W: List[List[float]], theta: float = 0.0) -> float:
    n = len(W)
    triangles = []
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n):
                t = (W[i][j] + W[j][k] + W[k][i]) / 3.0
                if t >= theta:
                    triangles.append(t)
    return sum(triangles)/len(triangles) if triangles else 0.0

def asymmetry_weighted_degree(W: List[List[float]]) -> float:
    degrees = [sum(row) for row in W]
    mean = sum(degrees)/len(degrees)
    return sum(abs(d-mean) for d in degrees)/len(degrees)

def compute_metrics_core_fixed(W_full: List[List[float]], core_nodes: List[int],
                               alpha=1.0, beta=1.0, gamma=0.5) -> Metrics:
    W = [[W_full[i][j] for j in core_nodes] for i in core_nodes]
    T = triangle_mean(W)
    H = sum(sum(row) for row in W)/len(W)**2  # simplified meso proxy
    A = asymmetry_weighted_degree(W)
    S = alpha*T + beta*H - gamma*A
    return Metrics(T, H, A, S)

def decision_act_hold(metrics: Metrics, theta_S: float = 0.25) -> str:
    return "ACT" if metrics.S >= theta_S else "HOLD"
