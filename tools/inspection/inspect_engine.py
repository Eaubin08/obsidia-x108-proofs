
# -*- coding: utf-8 -*-
from periphery.engine_gates.v4_structure.gate_engine_v4 import *
import types

print('--- AUDIT DES OBJETS DU MOTEUR ---')
# On itère sur une copie pour éviter le RuntimeError
for name in list(globals().keys()):
    if not name.startswith('__'):
        obj = globals()[name]
        print(f'Disponible: {name} | Type: {type(obj)}')

