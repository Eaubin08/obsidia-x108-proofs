import pytest
from periphery.math_core.governed_state import GovernedStateVector
from periphery.math_core.lyapunov import compute_lyapunov


def test_stable_low_violations():
    # L = α*ΔE + β*ΔC + γ*V_inst + δ*Δτ - η*I; all zero → L=0, |L|<0.05 → stable
    sv = GovernedStateVector(I=0.0, delta_E=0.0, delta_C=0.0, V_inst=0.0, delta_tau=0.0, F=0.0)
    result = compute_lyapunov("x", sv)
    assert abs(result.L_value) <= 0.05
    assert result.is_stable
    assert result.partition == "X_A"


def test_violence_maps_to_xb():
    sv = GovernedStateVector(V_inst=0.9)
    result = compute_lyapunov("x", sv)
    assert result.partition == "X_B"


def test_timeline_drift_maps_to_xh():
    sv = GovernedStateVector(delta_tau=0.8)
    result = compute_lyapunov("x", sv)
    assert result.partition == "X_H"


def test_l_value_computed():
    sv = GovernedStateVector(delta_E=1.0, delta_C=1.0)
    result = compute_lyapunov("x", sv)
    assert result.L_value > 0
