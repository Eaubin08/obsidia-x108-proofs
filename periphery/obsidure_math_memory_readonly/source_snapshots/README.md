# source_snapshots/README.md
## Obsidia X-108 — Instructions pour les snapshots de sources
## Date : 2026-06-25

---

## Ce dossier

Ce dossier est destiné à recevoir les exports lisibles des sources binaires référencées dans SOURCE_LEDGER.md.

---

## Sources déjà disponibles (fichiers .md dans le repo)

Les pépites suivantes sont déjà lisibles par la machine — elles sont dans `periphery/pepites_search_algo/` :

- `P36__Quintuplet_detat_canonique_S_I_L.md`
- `P42__Seuil_G1_ACT_si_S.md`
- `P88__Non_contradiction.md`
- `P100__Stabilite_de_Lyapunov_Ls_Ls.md`
- `P107__Stabilite_Lyapunov.md`
- `P161__Calibration_energetique_temporelle_loi_finale.md`

La source `extracted_text_all.md` est dans :
`periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/01_SOURCES/extracted_text_all.md`

---

## Sources illisibles — MISSING_CONTEXT

Les fichiers suivants sont au format .docx binaire. La machine ne peut PAS les lire. Tout concept provenant de ces fichiers est MISSING_CONTEXT jusqu'à export :

| Fichier source | Chemin | Concepts bloqués |
|---|---|---|
| `SECTION_V_Maths_Verite.docx` | `C:\Users\User\Desktop\Obsidia Master\OBSIDIA_SECTIONS_I_VII\` | Tout le contenu |
| `v1cano.docx` | `C:\Users\User\Desktop\Obsidia Master\obsidia\` | BALMA, SYRIQ |
| `formalisermath.docx` | `C:\Users\User\Desktop\Obsidia Master\obsidia\` | BALMA, SYRIQ, formules détaillées |
| Autres .docx dans `obsidia\` | `C:\Users\User\Desktop\Obsidia Master\obsidia\` | Contenu inconnu |

---

## Ce qu'Étienne doit faire pour rendre ces fichiers lisibles

### Option 1 — Export Word natif (recommandé)
1. Ouvrir le fichier .docx dans Microsoft Word
2. Fichier → Enregistrer sous → Format : Texte brut (.txt) ou Markdown (.md) si le plugin est disponible
3. Déposer le fichier exporté dans ce dossier (`periphery/obsidure_math_memory_readonly/source_snapshots/`)
4. Mettre à jour SOURCE_LEDGER.md pour passer le statut de MISSING_CONTEXT à PROVISIONAL (après vérification)
5. Mettre à jour MATH_MEMORY_INDEX.json avec les nouveaux concepts

### Option 2 — Export pandoc (ligne de commande)
```powershell
# Depuis PowerShell 7, en ayant pandoc installé
pandoc "C:\Users\User\Desktop\Obsidia Master\obsidia\v1cano.docx" -o "periphery\obsidure_math_memory_readonly\source_snapshots\v1cano_export.md"
pandoc "C:\Users\User\Desktop\Obsidia Master\obsidia\formalisermath.docx" -o "periphery\obsidure_math_memory_readonly\source_snapshots\formalisermath_export.md"
```

### Option 3 — Copier-coller manuel
Copier le contenu pertinent du .docx et le coller dans un fichier .md dans ce dossier.

---

## Règle après export

Une fois un fichier exporté ici :
1. Ne pas l'éditer — c'est un snapshot de source, pas un fichier de travail
2. Mettre à jour SOURCE_LEDGER.md pour refléter le nouveau statut
3. Si BALMA ou SYRIQ sont définis dans l'export, mettre à jour MATH_MEMORY_INDEX.json avec leur définition réelle
4. Ne jamais passer un item de MISSING_CONTEXT à CANONICAL_CANDIDATE sans avoir lu la source

---

## Interdiction

Ne jamais créer un fichier dans ce dossier qui invente ou interpole le contenu des .docx. Ce dossier ne contient que des exports fidèles des sources originales.
