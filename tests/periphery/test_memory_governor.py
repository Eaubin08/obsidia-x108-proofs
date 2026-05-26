from periphery.common import ActionCandidate
from periphery.memory_governor import run_memory_governor
def test_memory():
 p=run_memory_governor(ActionCandidate('a','bank','x','i','act',True,'',payload={'delta_R':1,'delta_I':1,'delta_C':1})); assert p.extra_metrics['memory_write_policy']=='FROZEN'
