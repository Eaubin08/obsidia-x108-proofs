CORE_1BASED = [2,6,10,20,24,25,26,27,29,31,32,34]
WORLD_1BASED = [1,3,4,5,7,8,9,11,12,13,14,15,16,17,18,19,21,22,23,28,30,33]

def core_nodes_0based():
    return [i-1 for i in CORE_1BASED]

def world_nodes_0based():
    return [i-1 for i in WORLD_1BASED]
