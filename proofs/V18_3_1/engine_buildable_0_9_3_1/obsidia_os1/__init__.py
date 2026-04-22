"""Obsidia OS1 minimal (guardian structurel).

OS1 ne décide pas à la place de l'humain :
- il valide le contrat
- il applique X108 (HOLD/ACT)
- il délègue l'exécution à OS0 sandbox
- il produit une SSR (explication)
"""

from .os1 import run_request, OS1Decision
