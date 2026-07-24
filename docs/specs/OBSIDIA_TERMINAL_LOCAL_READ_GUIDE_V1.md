# OBSIDIA_TERMINAL_LOCAL_READ_GUIDE_V1 — spécification

## 0. Identité

Scope : `LOCAL_READ_GUIDE_V1`, issu du design
`OBSIDIA_TERMINAL_BRODY_LOCAL_ACTION_READ_V1_DESIGN` (accepté pour V1
uniquement). Couche de classification et guidage des demandes de lecture
locale. **Le terminal ne lit aucun fichier utilisateur, n'exécute aucune
commande, n'appelle pas Brody.** Aucun nouveau mode, aucun nouveau droit.

## 1. Objectif V1

Comprendre les IN du type lis/résume/explique/cherche/compare/liste,
refuser secrets et mutations, et afficher la commande PowerShell exacte
que l'humain lance lui-même.

## 2. Différence corpus local / lecture locale

Le corpus lit des fichiers choisis à l'avance dans une allow-list fermée
et validée. La lecture locale viserait des fichiers choisis par l'IN à
l'exécution — l'espace d'entrée devient le disque. D'où : policy d'abord
(V1), capacité ensuite (V2, jamais sans GO séparé).

## 3. Verbes locaux readonly classés

`READ_LOCAL_FILE` (lis/lire/ouvre/affiche), `SUMMARIZE_LOCAL_DOC`
(résume), `EXPLAIN_LOCAL_CODE` (explique), `SEARCH_LOCAL_TEXT` (cherche),
`COMPARE_LOCAL_FILES` (compare), `LIST_LOCAL_DIR` (regarde/liste).
Ces verbes sont des classifications d'intention, pas des droits.
Sans chemin ni contexte fichier ("ce fichier", "dossier"), les verbes
conceptuels (résume/explique/lis) retombent dans le flux corpus normal
("résume le freeze terminal" reste une réponse corpus).

## 4. V1 guide-only

Sorties utilisées : COMMANDS (commande affichée), GUIDE (cas Brody),
POLICY_DENY (secrets/mutations), STOP_UNKNOWN (chemin manquant).
Modes internes existants uniquement : ANSWER_COMMANDS_ONLY, ANSWER_PLAN,
ANSWER_POLICY_DENY, ANSWER_UNKNOWN. Aucun `ANSWER_LOCAL_ACTION` créé.

## 5. Chemins et secrets interdits

Refus sec (POLICY_DENY, **aucune commande alternative**) si l'IN vise :
`.env`, `.pem`, `.key`, `id_rsa`, `credential*`, `token*`, `secret*`,
`.local_obsidia`, `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`,
clés ssh. Extension au-delà de la liste validée : `ssh`/`clé ssh` ajoutés
(famille id_rsa — « lis mes clés ssh » doit être refusé).

## 6. Commandes PowerShell proposées (affichées, jamais exécutées)

`Get-Content -Path "<chemin>" -TotalCount 200` ; `Get-ChildItem -Path
"<chemin>"` ; `Select-String -Path "<chemin>" -Pattern "<motif>"` ;
`Compare-Object (Get-Content "<A>") (Get-Content "<B>")`.

## 7. Brody POST-only et limite V1

Brody n'a qu'une route `POST /api/brody/chat` (vérifié à l'audit — zéro
GET). « brody explique ce fichier » → GUIDE : le terminal explique que
Brody est hors droits V1 (EXECUTE = GET readonly) et propose la lecture
manuelle + collage du contenu pour explication terminale non souveraine.
Brody ne reçoit jamais de contenu brut. Futur endpoint GET readonly =
scope API séparé, hors terminal.

## 8. Interdits permanents

Pas de `read_text`/`open()` sur chemin utilisateur, pas de subprocess,
pas d'os.system, pas de glob-lecture disque, pas d'appel HTTP/Brody dans
cette couche, pas d'écriture/suppression/patch/commit/push/deploy,
pas de lancement serveur/Lean/Obsidure, pas de memory write, pas de
mutation Kernel/X108/Sigma Core.

## 9. Cas utilisateur couverts

Les 14 cas obligatoires du GO : lecture avec chemin → COMMANDS ; résume
sans chemin → STOP_UNKNOWN (demande de chemin) ; cherche/compare/liste →
COMMANDS ; `.env` et clés ssh → POLICY_DENY sec ; supprime/modifie/commit
→ POLICY_DENY (policy registry + tokens mutation locaux : modifie,
renomme, déplace, édite) ; brody explique/lire → GUIDE POST-only ;
brody status → inchangé.

## 10. Limites V1

Aucune lecture réelle : le terminal ne peut pas vérifier qu'un chemin
existe, ni résumer sans collage humain. La détection de chemin est
lexicale (tokens avec / \ ou extension autorisée). Receipt enrichi du
champ `action_locale` (classification), toujours non souverain.

## 11. V2 future : EXECUTE_READONLY_LOCAL

Lecture réelle bornée (racines repo, résolution absolue anti-traversal,
256 Ko / 200 lignes, masquage de secrets par contenu, receipt
octets_lus/verdict_path_policy). **Design + GO séparés obligatoires** —
jamais activée en passant.
