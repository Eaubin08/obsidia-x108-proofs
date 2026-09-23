# OBSIDIA_TERMINAL_LARGE_DOC_READ_V2 (tranche V2A) — spécification

## 0. Identité

Scope : `LARGE_DOC_READ_V2A` — moitié (a) du design
`OBSIDIA_TERMINAL_LARGE_DOC_READ_V2_DESIGN` : navigation de gros documents.
Première couche où le terminal **lit réellement** des fichiers texte du
repo, en lecture seule bornée. Non souverain, KX108_ONLY, aucun droit
d'action irréversible.

## 1. Objectif V2A

Lire par fenêtre/range, chercher, montrer le contexte, lister un dossier —
sur des fichiers texte du repo, sans jamais tout charger ni tout afficher.

## 2. Différence V1 guide-only / V2A lecture réelle bornée

V1 affichait la commande PowerShell sans rien lire. V2A lit via streaming
pur (`open` + itération ligne à ligne) et affiche une fenêtre bornée.
Tous les refus V1 (secrets, mutations) restent identiques.

## 3. Capacité gros documents

À l'ouverture : nombre de lignes total (compté en streaming), fenêtre
courante, phrase de navigation `suite : lis les lignes N a M de <fichier>`.
Un document de 800 pages est navigable fenêtre par fenêtre ; le full dump
est structurellement impossible (formateur borné).

## 4. Fenêtres / ranges

`READ_LOCAL_WINDOW` (défaut 120 lignes), `READ_LOCAL_RANGE`
(`lis les lignes 20 à 60 de X`). Bornes : fenêtre max 400 lignes, ligne
max 300 caractères, budget réponse ~64 Ko. Streaming O(fenêtre) mémoire —
jamais `read()`/`readlines()`/`read_text()` sur chemin utilisateur.

## 5. Recherche et contexte

`SEARCH_LOCAL_TEXT` (`cherche <mot> dans X`) : max 50 correspondances,
arrêt de lecture au 50e. `SEARCH_LOCAL_CONTEXT` (`montre le contexte autour
de <mot> dans X`) : ±3 lignes, max 10 contextes. Chaque ligne affichée
passe par le masquage de secrets.

## 6. Listing dossier

`LIST_LOCAL_DIR` (`regarde docs/specs`) : 100 entrées max, non récursif,
noms seulement.

## 7. Sécurité chemin

`local_path_policy()` : résolution absolue puis confinement `relative_to`
sous REPO_ROOT (tue `../` et symlinks sortants), racines lisibles
(`docs/ scripts/ tests/ periphery/ apps/obsidia_api/ proofs/lean/`),
segments interdits (`.git node_modules venv .venv __pycache__
_PATCH_PROPOSALS .local_obsidia _BACKUP_* _EPHEMERAL_*`), noms sensibles
(`MANIFEST_SHA256.json merkle_seal.json`), extensions autorisées
(`.md .txt .json .yaml .yml .py .lean .ps1`). Verdicts : ALLOWED /
DENIED_SECRET / DENIED_OUT_OF_REPO / DENIED_OUT_OF_ROOT / DENIED_SEGMENT /
DENIED_SENSITIVE / DENIED_EXTENSION / DENIED_FORMAT / NOT_FOUND / IS_DIR.

## 8. Sécurité secrets

Deux couches. Nom (avant toute I/O) : `.env .pem .key id_rsa credential*
token* secret* ssh` → POLICY_DENY sec, aucune lecture. Contenu (pendant le
streaming) : motifs `api_key password authorization bearer BEGIN PRIVATE
KEY ghp_ sk- AKIA` → ligne remplacée par `[SECRET_MASQUE ligne N]` ;
> 3 lignes masquées → arrêt, verdict `DENIED_SECRET_DENSITY`. Le contenu
masqué n'apparaît jamais, même en verbose.

## 9. PDF/DOCX refusés en V2A

Extensions `.pdf .doc .docx .odt` et binaires (`.bin .exe .zip png/jpg/
jpeg/webp`) → `DENIED_FORMAT`, aucune lecture. Détection aussi par contenu
(octet nul dans les 8 premiers Ko → binaire non lu). Réponse GUIDE :
convertir en .txt/.md soi-même ; adapter PDF/DOCX = V3 (scope séparé, pas
de dépendance, pas d'OCR).

## 10. Capacités reportées V2B/V3

V2B : `SUMMARIZE_LOCAL_CHUNK`, `SUMMARIZE_LOCAL_PROGRESSIVE`,
`EXPLAIN_LOCAL_SECTION`, `COMPARE_LOCAL_EXCERPTS` (renvoient GUIDE en V2A).
V3 : `DOC_ADAPTER_PDF_DOCX`.

## 11. Receipts non souverains

Champs (jamais le contenu lu) : `action_locale`, `local_read_meta`
(verdict_policy, type_fichier, range_lignes, lignes_affichees, match_count,
secrets_masques, truncated). Toujours `sovereign: false`.

## 12. Tests de sécurité

`tests/gates/test_obsidia_large_doc_read_policy.py`, tout en tmp_path avec
REPO_ROOT monkeypatché : gros fichier 50 000 lignes borné, range exact,
fenêtre max, search borné 50, contexte borné 10, lignes tronquées, secret
masqué, densité secrets, .env/id_rsa/token refusés avant I/O, traversal,
absolu hors repo, extension refusée, PDF/DOCX, binaire, hors racine, aucune
écriture, statiques anti-subprocess et anti-lecture-complète.

## 13. Limites

Sortie EXECUTE (lecture réelle readonly, comme doctor), mode interne
ANSWER_LOCAL avec `corpus_utilise = [chemin]`. Curseur de navigation :
range explicite en one-shot (pas de `continue` persistant en V2A ; le
suivi de session `continue`/`page suivante` viendra avec V2B si utile).
Détection de chemin lexicale. Aucune récursivité de listing.
