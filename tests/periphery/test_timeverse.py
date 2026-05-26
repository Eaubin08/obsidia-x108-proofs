from periphery.common import ActionCandidate
from periphery.timeverse import run_timeverse
def test_async():
 p=run_timeverse(ActionCandidate('a','trading','x','i','act',True,'',payload={'async_action':True})); assert 'ASYNC_RECHECK_REQUIRED' in p.unknowns
