from periphery.common import ActionCandidate
from periphery.operational_constance import run_operational_constance
def test_fake():
 p=run_operational_constance(ActionCandidate('a','bank','x','i','act',True,'',payload={'fake_stability':True})); assert 'FAKE_STABILITY' in p.risk_flags
