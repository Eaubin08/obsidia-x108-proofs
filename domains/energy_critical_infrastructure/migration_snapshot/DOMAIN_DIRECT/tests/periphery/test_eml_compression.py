from periphery.common import ActionCandidate
from periphery.eml_compression import run_eml_compression
def test_eml():
 p=run_eml_compression(ActionCandidate('a','bank','x','i','act',True,'',payload={})); assert p.extra_metrics['eml_is_candidate_only']
