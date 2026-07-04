# OBSIDIA_TERMINAL_LARGE_DOC_READ_V2B — spécification

## Identité

Scope : `LARGE_DOC_READ_V2B`. Implémente `SUMMARIZE_LOCAL_PROGRESSIVE`,
`EXPLAIN_LOCAL_PROGRESSIVE`, `COMPARE_LOCAL_BOUNDED` — reconnus mais
différés en V2B_REQUIRED depuis le NL-intent V2. **V2B = lecture locale
extractive bornée** : pas de résumé global, pas de modèle externe, pas de
lecture complète, aucun droit nouveau. Réutilise entièrement la plomberie
V2A (`_stream_window`, `local_path_policy`, `_is_binary`, `_stream_count_lines`,
`_parse_range`). Seul ajout d'import : `difflib` (stdlib) pour la comparaison.

## Principe extractif-first (anti-hallucination)

Le terminal n'affirme que ce qui est **présent dans la fenêtre lue** :
titres/puces/signatures pour le résumé, sections + identifiants techniques
pour l'explication, `difflib.unified_diff` borné pour la comparaison.
Règles dures : toujours afficher « lignes X-Y sur T » ; bannière
« fenêtre PARTIELLE » si Y < T ; jamais « le document dit » ni « document
complet » sur fenêtre partielle ; toujours « dans la fenêtre lue ».

## Bornage (hérité V2A)

Fenêtre 120 défaut / 400 max, ligne 300 car., points clés ≤ 12, termes
techniques ≤ 15, sections ≤ 12, diff ≤ 120 lignes, compare = 2 fenêtres.
Streaming pur — aucun `read()`/`readlines()`/`read_text()` sur chemin
utilisateur. Range explicite honoré (`résume les lignes 20 à 40 de X`).

## SUMMARIZE_LOCAL_PROGRESSIVE

`résume/synthétise/essentiel <fichier>` → EXECUTE. Extrait titres, puces,
signatures def/class, sinon premières phrases. Affiche points clés +
Limites + Next (résumer la fenêtre suivante si partielle).

## EXPLAIN_LOCAL_PROGRESSIVE

`explique/détaille/clarifie <fichier>` → EXECUTE. Carte des sections
visibles (avec type), identifiants techniques repérés (MAJ, snake_case,
CamelCase), lecture prudente strictement dérivée du visible. Cible absente
→ STOP_UNKNOWN.

## COMPARE_LOCAL_BOUNDED

`compare/différence/écart A et B` → EXECUTE. Lit une fenêtre bornée de
chaque fichier, `difflib.unified_diff` plafonné 120 lignes, points communs
échantillonnés, Limites + Next. Exactement 2 fichiers ; >2 → GUIDE
clarification ; fichier invalide → POLICY_DENY/GUIDE via `local_path_policy`.

## Refus / GUIDE / POLICY_DENY

PDF/DOCX/binaire → GUIDE (adapter V3, non implémenté). `.env`/`id_rsa`/
`token`/hors-repo/hors-racine/segment/extension → POLICY_DENY avant I/O.
Densité de secrets → DENIED_SECRET_DENSITY. Cible absente → STOP_UNKNOWN.
`résume le freeze terminal` (sans chemin) → reste corpus.

## Limites

Résumé/explication = fenêtre lue uniquement, jamais le fichier entier.
Extraction déterministe (pas de modèle). Comparaison = fenêtres, pas
fichiers entiers. Navigation par range/Next pour couvrir un gros document.

## Tests

`tests/gates/test_obsidia_large_doc_read_v2b.py` : résumé petit/gros/range,
explication, comparaison bornée + diff plafonné, >2 fichiers→GUIDE, cible
absente→STOP_UNKNOWN, secrets→DENY, PDF/DOCX→GUIDE, statiques
anti-subprocess et anti-lecture-complète, anti-hallucination (pas de claim
global sur fenêtre partielle), NL résume/explique/compare→EXECUTE.

## Backlog V3

`DOC_ADAPTER_PDF_DOCX` : lecture de PDF/DOCX (conversion), scope dédié avec
décision de dépendance — non couvert ici, pas d'OCR, pas de dépendance
ajoutée en V2B.
