# Runtime Terrain BANK / TRADING / GPS

## Statut

Ce dossier contient la surface Ragnarok terrain dédiée aux flux :
- BANK
- BOURSE / TRADING
- GPS / AVIATION

## Distinction

KERNEL_ROOT_TRINITY :
- Path : ../server.kernel.sealed.cjs
- Rôle : kernel racine repo / proof / Trinity
- Ne pas confondre avec cette surface terrain.

KERNEL_TERRAIN_RAGNAROK :
- Path : ./server.kernel.sealed.cjs
- Rôle : serveur terrain sous pression
- Endpoint : /kernel/ragnarok
- Port : 3001
- Domaines : bank / trading / gps_defense_aviation

BRODY_RUNTIME :
- Rôle : opérateur / interface / mémoire / readonly
- Autorité : aucune
- Branchement terrain : non prouvé

## Règle

Ne pas écraser le kernel racine.
Ne pas mélanger Brody avec Ragnarok.
Ne pas importer allData massif dans Git.
