from periphery.common import ActionCandidate
from periphery.provenance_gate import run_provenance_gate
def test_fake():
 p=run_provenance_gate(ActionCandidate('a','bank','x','i','act',True,'',payload={'fake_provenance_detected':True})); assert 'FAKE_PROVENANCE' in p.contradictions
