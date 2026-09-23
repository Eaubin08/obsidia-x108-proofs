from periphery.common import ActionCandidate
from periphery.energy_thermo import run_energy_thermo
def test_mismatch():
 p=run_energy_thermo(ActionCandidate('a','gps','x','i','act',True,'',payload={'truth_score':0,'sigma_score':1})); assert 'SIGMA_TRUTH_MISMATCH' in p.risk_flags
