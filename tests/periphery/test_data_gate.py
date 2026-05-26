from periphery.common import ActionCandidate
from periphery.data_gate import run_data_gate
def test_stale_data_holds():
 p=run_data_gate(ActionCandidate('a','bank','x','i','act',True,'',payload={'freshness_score':0.1})); assert 'STALE_DATA' in p.unknowns and p.recommended_gate=='HOLD'
