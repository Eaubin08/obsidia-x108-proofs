from periphery.failure_mapping import classify_failure
def test_map():
 assert classify_failure('STALE_DATA')=='unknown'; assert classify_failure('PERMISSION_MISSING')=='contradiction'
