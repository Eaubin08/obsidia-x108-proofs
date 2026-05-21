from dataclasses import dataclass
from enum import Enum

class State(str, Enum):
    START = "START"
    ON = "ON"
    HOLD = "HOLD"
    SAFE_OFF = "SAFE_OFF"
    FALSE_ON = "FALSE_ON"
    ASSISTED_ON = "ASSISTED_ON"
    DECAY = "DECAY"
    REJECTED = "REJECTED"
    OFF = "OFF"


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def safe_div(a, b):
    return 0.0 if abs(b) < 1e-12 else a / b

@dataclass
class System:
    pin_raw: float = 0.0
    paux: float = 0.0
    pstorage_in: float = 0.0
    pstorage_out: float = 0.0
    L_M2: float = 0.0
    L_storage: float = 0.0
    eta_min: float = 0.5
    eta_nom: float = 0.75
    eta_max: float = 0.9
    M3_threshold: float = 0.1
    M3_sat_high: float = 1e9
    topology_loss_base: float = 0.0
    constriction_ratio: float = 0.0
    turbulence: float = 0.0
    R_storage: float = 0.0
    R_storage_max: float = 100.0
    theta_on: float = 1.0
    theta_hold: float = 0.5
    theta_off: float = 0.1
    state: State = State.START
    pout: float = 0.0
    assisted_ratio: float = 0.0
    sigma_score: float = 0.0
    truth_score: float = 0.0
    delta_g: float = 0.0
    L_total: float = 0.0


def topology_losses(system: System) -> float:
    penalty = system.topology_loss_base
    penalty += max(0.0, system.constriction_ratio - 0.5) * 0.1 * max(system.pin_raw, 1.0)
    penalty += max(0.0, system.turbulence - 0.5) * 0.1 * max(system.pin_raw, 1.0)
    return max(0.0, penalty)


def compute_sigma(system: System, pout: float) -> float:
    stability = 1.0 if pout > 0 else 0.0
    continuity = 1.0 if system.pin_raw >= system.theta_hold else 0.3
    coherence = 1.0 if system.assisted_ratio <= 0.5 else 0.4
    saturation = 1.0 if system.pin_raw > system.M3_sat_high else 0.0
    noise = min(1.0, system.turbulence)
    sigma = 0.30*stability + 0.25*continuity + 0.25*coherence - 0.10*saturation - 0.10*noise
    return clamp(sigma, 0.0, 1.0)


def compute_truth(system: System, assisted_ratio: float) -> float:
    hidden_loss = clamp(system.L_total / max(system.pin_raw + system.paux + system.pstorage_out, 1.0), 0.0, 1.0)
    relaunch_dependency = clamp(system.paux / max(system.pin_raw + system.paux + system.pstorage_out, 1.0), 0.0, 1.0)
    truth = 1.0 - 0.45*assisted_ratio - 0.30*hidden_loss - 0.25*relaunch_dependency
    return clamp(truth, 0.0, 1.0)


def transition(state, pin_real, pout, assisted_ratio, sigma_score, truth_score, system: System):
    if truth_score < 0.5 and pout > 0:
        return State.FALSE_ON
    if assisted_ratio > 0.5 and pout > 0:
        return State.FALSE_ON
    if system.paux > system.pin_raw and assisted_ratio > 0.5:
        return State.REJECTED
    if pin_real < system.theta_off:
        return State.OFF if state in {State.START, State.HOLD} else State.HOLD
    if pin_real < system.theta_hold:
        return State.HOLD
    if pin_real >= system.theta_on and truth_score >= 0.8 and sigma_score >= 0.7:
        return State.ON
    if sigma_score < 0.4:
        return State.DECAY
    return State.HOLD


def step(system: System, dt: float = 1.0) -> System:
    pin_real = max(0.0, system.pin_raw - system.L_M2)

    if pin_real < system.M3_threshold:
        pout_conv = 0.0
    else:
        eta = clamp(system.eta_nom, system.eta_min, system.eta_max)
        if pin_real > system.M3_sat_high:
            pin_effective = system.M3_sat_high
        else:
            pin_effective = pin_real
        pout_conv = eta * pin_effective

    L_M3 = max(0.0, pin_real - pout_conv)
    L_M4 = topology_losses(system)
    pout = max(0.0, pout_conv - L_M4)

    system.R_storage += (system.pstorage_in - system.pstorage_out - system.L_storage) * dt
    system.R_storage = clamp(system.R_storage, 0.0, system.R_storage_max)

    total_input = system.pin_raw + system.paux + system.pstorage_out
    assisted_ratio = safe_div(system.paux + system.pstorage_out, total_input)

    system.assisted_ratio = assisted_ratio
    system.L_total = system.L_M2 + L_M3 + L_M4 + system.L_storage
    sigma_score = compute_sigma(system, pout)
    truth_score = compute_truth(system, assisted_ratio)
    delta_g = safe_div(pout, total_input)

    system.state = transition(system.state, pin_real, pout, assisted_ratio, sigma_score, truth_score, system)
    system.pout = pout
    system.sigma_score = sigma_score
    system.truth_score = truth_score
    system.delta_g = delta_g
    system.L_total = system.L_M2 + L_M3 + L_M4 + system.L_storage
    return system

if __name__ == "__main__":
    s = System(pin_raw=10, paux=0, L_M2=0.5, topology_loss_base=0.5, state=State.START)
    for i in range(5):
        s = step(s, dt=1.0)
        print(i, s.state, round(s.pout, 3), round(s.delta_g, 3), round(s.truth_score, 3), round(s.sigma_score, 3), round(s.assisted_ratio, 3))
