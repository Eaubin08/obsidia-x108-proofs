# OBSIDIA_TERMINAL_DOCX_ADAPTER_V3

> Couche : TERMINAL / DOC-ADAPTER  
> Statut : APPLIED — OBSIDIA_TERMINAL_DOCX_ADAPTER_V3_APPLY_COMPLETE  
> Scope : DOCX uniquement. PDF non supporté en V3.

---

## 1. Résumé

V3 ajoute le support de lecture DOCX au terminal Obsidia via extraction stdlib-only
(`zipfile` + `xml.etree.ElementTree`). Les paragraphes DOCX sont traités comme des
lignes texte et traités par les mêmes bornes, politiques secrets et fonctions
extractives que V2A/V2B. PDF reste refusé (GUIDE) — stdlib insuffisante.

---

## 2. Périmètre

| Format | Comportement V3 |
|---|---|
| `.docx` valide | EXECUTE — extraction texte brut, fenêtre bornée |
| `.docx` corrompu / non standard | GUIDE — refus gracieux |
| `.pdf` | GUIDE — non pris en charge (V3b scope séparé) |
| autres binaires | inchangé — DENIED_FORMAT |

---

## 3. Extraction DOCX

**Bibliothèques** : `zipfile` (stdlib) + `xml.etree.ElementTree` (stdlib).  
**Aucune dépendance externe. Aucun `pip install`.**

Algorithme :
1. Vérification taille ≤ `_DOCX_SIZE_CAP` (10 Mo)
2. `zipfile.ZipFile(abs_path, "r")` — lecture seule
3. `zf.open("word/document.xml")` — accès par clé nominale uniquement
4. `ET.parse(f)` — parse XML en mémoire
5. `iter('{…}p')` → `iter('{…}t')` → `''.join(t.text)` par paragraphe

**Ce qui est extrait** : texte brut des paragraphes `<w:p>` / runs `<w:t>`.

**Ce qui est exclu** : images, tableaux, headers, footers, notes de bas de page,
objets embarqués, propriétés du document, macros, champs calculés.

---

## 4. Confinement et sécurité

`_try_docx_adapter(pstr)` réplique les contrôles de `local_path_policy` sans
modifier cette fonction (V2A intact) :

- Secret par nom : `_LOCAL_SECRET_TOKENS` vérifiés avant toute I/O
- Résolution absolue + `relative_to(REPO_ROOT)` — traversal tué
- Segments interdits : `_LOCAL_DENY_SEGMENTS`
- Racines autorisées : `_LOCAL_ROOTS`
- Existence fichier vérifiée avant ouverture

**`local_path_policy` retourne toujours `DENIED_FORMAT` pour `.docx`** — invariant
V2A préservé. L'adapter V3 vit au-dessus, intercepte avant l'appel à la policy core.

---

## 5. Politique secrets

Identique V2A/V2B sans exception :

- `_SECRET_CONTENT_RE` appliqué sur chaque paragraphe extrait
- Paragraphe sensible → `[SECRET_MASQUE ligne N]`
- >3 paragraphes masqués → `DENIED_SECRET_DENSITY` / `POLICY_DENY`
- Contenu masqué jamais affiché

---

## 6. Bornage paragraphes

Les constantes V2 s'appliquent identiquement :

| Constante | Valeur | Usage DOCX |
|---|---|---|
| `_WIN_DEFAULT` | 120 | fenêtre par défaut |
| `_WIN_MAX` | 400 | cap absolu |
| `_LINE_MAX` | 300 | caractères par paragraphe |
| `_SEARCH_MAX` | 50 | correspondances max |
| `_CTX_MAX` | 10 | occurrences contexte max |
| `_CTX_LINES` | 3 | paragraphes ±contexte |

---

## 7. Opérations supportées

| Opération | Fonction DOCX | Comportement |
|---|---|---|
| `READ_LOCAL_WINDOW` | `_read_docx_window` | fenêtre paragraphes 1-120 |
| `READ_LOCAL_RANGE` | `_read_docx_window` | paragraphes X-Y |
| `SEARCH_LOCAL_TEXT` | `_search_docx_lines` | recherche bornée 50 |
| `SEARCH_LOCAL_CONTEXT` | `_context_docx_lines` | ±3 paragraphes, 10 max |
| `SUMMARIZE_LOCAL_PROGRESSIVE` | `_summarize_docx_lines` | extractif, keypoints |
| `EXPLAIN_LOCAL_PROGRESSIVE` | `_explain_docx_lines` | structure + termes |
| `COMPARE_LOCAL_BOUNDED` | `_compare_docx_lines` | DOCX vs DOCX uniquement |

Comparaison mixte DOCX/TXT : GUIDE (non supportée en V3).

---

## 8. Refus gracieux

| Cas | Message |
|---|---|
| ZIP corrompu | "DOCX illisible (ZIP corrompu)" |
| `word/document.xml` absent | "DOCX non standard (word/document.xml absent)" |
| XML invalide | "DOCX XML illisible (ParseError)" |
| Erreur I/O | "Erreur lecture DOCX (…)" |
| >10 Mo | "DOCX trop volumineux (>10 Mo)" |
| 0 paragraphe | "Aucun texte extractible dans ce DOCX (0 paragraphe)" |

---

## 9. Invariants garantis par construction

- **Aucun subprocess** — `zipfile` + `ET` sont des appels Python directs
- **Aucun `extractall()`** — accès uniquement `zf.open("word/document.xml")`
- **Aucune écriture disque** — extraction 100 % en mémoire
- **Aucune dépendance externe** — stdlib uniquement
- **Aucun modèle externe, aucun POST Brody, aucune URL**
- **Pas de dump complet** — fenêtres bornées sur la liste de paragraphes
- **Pas de mutation Kernel/Sigma/X108**
- **`decision_authority = KX108_ONLY`** — inchangé
- **Anti-hallucination** : bannière obligatoire `"Extraction DOCX : texte brut uniquement"`
  + `"fenetre PARTIELLE — pas une synthese globale du document"` si fenêtre incomplète

---

## 10. Tests

Fichier : `tests/gates/test_obsidia_docx_adapter_v3.py` (19 tests)

| Test | Vérifie |
|---|---|
| `test_docx_summarize_bounded_execute` | DOCX valide → EXECUTE, fenêtre bornée |
| `test_docx_explain_bounded_execute` | explication extractive bornée |
| `test_docx_compare_bounded_execute` | comparaison DOCX vs DOCX bornée |
| `test_docx_read_window_bounded` | lecture fenêtre ≤ `_WIN_DEFAULT` |
| `test_docx_search_bounded` | recherche ≤ `_SEARCH_MAX` |
| `test_docx_context_bounded` | contexte ≤ `_CTX_MAX` |
| `test_docx_extract_secret_masked` | api_key → SECRET_MASQUE |
| `test_docx_density_denied` | densité secrets → POLICY_DENY |
| `test_docx_bad_zip_graceful_guide` | ZIP corrompu → GUIDE propre |
| `test_docx_no_document_xml_graceful_guide` | ZIP sans document.xml → GUIDE |
| `test_docx_empty_paragraphs_guide` | 0 paragraphe → GUIDE |
| `test_docx_size_cap_guide` | >taille cap → GUIDE |
| `test_pdf_still_guide_after_v3` | PDF toujours GUIDE |
| `test_v2a_policy_docx_still_denied_format` | `local_path_policy` inchangée |
| `test_static_no_subprocess_v3` | pas d'import subprocess |
| `test_static_no_extractall_v3` | pas d'extractall |
| `test_static_no_pdf_deps_v3` | pas de dep PDF externe |
| `test_docx_anti_hallucination` | bannière extraction, pas de "document complet" |
| `test_py_compile` | compilation Python sans erreur |

V2B mis à jour : `test_pdf_docx_still_guide_v3_required` → scindé en
`test_pdf_still_guide_after_docx_adapter_v3` + `test_docx_valid_now_execute_after_v3`.

---

## 11. Fonctions ajoutées (`scripts/obsidia_cli.py`)

| Fonction | Rôle |
|---|---|
| `_extract_docx_lines(abs_path)` | extraction stdlib paragraphes DOCX |
| `_docx_window(lines, start, count)` | fenêtre bornée sur liste paragraphes |
| `_try_docx_adapter(pstr)` | confinement repo + extraction |
| `_summarize_docx_lines(rel, lines, start, count)` | résumé extractif |
| `_explain_docx_lines(rel, lines, start, count)` | explication extractive |
| `_compare_docx_lines(rel_a, lines_a, rel_b, lines_b, start, count)` | comparaison bornée |
| `_read_docx_window(rel, lines, start, count, kind)` | lecture fenêtre |
| `_search_docx_lines(rel, lines, query)` | recherche bornée |
| `_context_docx_lines(rel, lines, query)` | contexte ±3 paragraphes |

---

## 12. PDF — position V3

PDF n'est **pas** supporté en V3. Raison : aucun parseur PDF dans la stdlib Python.
Toute dépendance externe (`pypdf`, `pdfminer`, `fitz`) exige un GO explicite
et un scope séparé (V3b).

Message retourné :
```
PDF non pris en charge (stdlib insuffisante ; adapter PDF = scope V3b separe).
Convertis en .txt/.md puis relance.
```
