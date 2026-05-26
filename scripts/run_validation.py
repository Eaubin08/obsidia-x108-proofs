
import importlib
modules_to_test = [
    'periphery.brody_memory_readonly.readonly_session_test.brody_readonly_session_test_v1',
    'periphery.specs'
]
print('--- LANCEMENT DE LA VALIDATION DE BUILD ---')
for mod_name in modules_to_test:
    try:
        mod = importlib.import_module(mod_name)
        # On cherche une fonction 'run' ou 'test' standard dans tes specs
        if hasattr(mod, 'run'):
            print(f'TEST {mod_name}: {mod.run()}')
        else:
            print(f'TEST {mod_name}: [OK] Module chargé (pas de fonction run)')
    except Exception as e:
        print(f'ERREUR TEST {mod_name}: {e}')

