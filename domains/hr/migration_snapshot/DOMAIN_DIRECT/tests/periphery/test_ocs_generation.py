from periphery.common import ActionCandidate
from periphery.ocs_generation import run_ocs_generation
def test_voice():
 p=run_ocs_generation(ActionCandidate('a','bank','x','i','act',True,'',payload={'voice_intent_ambiguous':True})); assert p.recommended_gate=='HOLD'
