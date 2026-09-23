from periphery.common import ActionCandidate
from periphery.permission_economic import run_permission_economic
def test_limit():
 p=run_permission_economic(ActionCandidate('a','bank','x','i','act',True,'',payload={'spending_limit_ok':False})); assert 'PAYMENT_LIMIT_FAIL' in p.contradictions
