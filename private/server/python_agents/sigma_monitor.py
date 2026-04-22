import time
from typing import List, Dict, Any


class SigmaMonitor:
    """
    Basic Sigma Dynamic Stability monitor.
    Tracks a latent scalar state derived from severity, risk flags,
    and contradictions, then computes velocity/acceleration bounds.
    """

    def __init__(self, tau_min: float = 0.05, tau_max: float = 0.75, accel_limit: float = 0.4):
        self.tau_min = tau_min
        self.tau_max = tau_max
        self.accel_limit = accel_limit
        self.history = []
        self.severity_map = {"S0": 0.0, "S1": 0.25, "S2": 0.5, "S3": 0.75, "S4": 1.0}

    def _to_vector(self, severity: str, risk_count: int, contra_count: int) -> float:
        base = self.severity_map.get(severity, 0.0)
        return base + (risk_count * 0.05) + (contra_count * 0.1)

    def update(self, severity: str, risk_flags: List[Any], contradictions: List[Any]) -> Dict[str, Any]:
        z_t = self._to_vector(severity, len(risk_flags), len(contradictions))
        t_t = time.time()

        report: Dict[str, Any] = {
            "velocity": 0.0,
            "acceleration": 0.0,
            "stability_status": "STABLE",
            "violations": [],
        }

        if len(self.history) >= 1:
            dt = t_t - self.history[-1]["ts"]
            if dt > 0:
                v_t = abs(z_t - self.history[-1]["val"]) / dt
                report["velocity"] = v_t

                if v_t < self.tau_min:
                    report["violations"].append("POTENTIAL_COLLAPSE")
                elif v_t > self.tau_max:
                    report["violations"].append("LATENT_DRIFT")

            if len(self.history) >= 2 and dt > 0:
                dt_prev = self.history[-1]["ts"] - self.history[-2]["ts"]
                if dt_prev > 0:
                    v_prev = abs(self.history[-1]["val"] - self.history[-2]["val"]) / dt_prev
                    a_t = abs(report["velocity"] - v_prev) / dt
                    report["acceleration"] = a_t
                    if a_t > self.accel_limit:
                        report["violations"].append("HIGH_CURVATURE_INSTABILITY")

        self.history.append({"val": z_t, "ts": t_t})
        if len(self.history) > 5:
            self.history.pop(0)

        if report["violations"]:
            report["stability_status"] = "UNSTABLE"

        return report

    def check_coherence_stationarity(self, current_hash: str, expected_hash: str) -> bool:
        return current_hash == expected_hash
