# CANONICAL CONTEXT JSON V1

```
status:          PROPOSED_NOT_CANONICAL
canonical_after: CONTEXT_OS_ARCHITECTURE_ACCEPTED
palier:          T0.3-B
document_id:     F03
version:         1.0.0
produced_by:     T0_3_B_EXEC_20260718
```

Ce document est PROPOSED_NOT_CANONICAL. Il ne devient canonique qu'après la gate CONTEXT_OS_ARCHITECTURE_ACCEPTED.

---

## A. ENCODAGE

```
encoding:       UTF-8
bom:            interdit
null_bytes:     interdits
control_chars:  interdits_sauf_LF_CR_TAB_dans_valeurs_string
```

---

## B. UNICODE ET ORDRE DES CLÉS

### B.1 Normalisation Unicode (HD-02 — HUMAN_ACCEPTED_FOR_T0_3_B_CONTRACT)

```
normalization: NFC
```

### B.2 Validité scalaire

Seules les valeurs scalaires Unicode valides sont acceptées (U+0000–U+D7FF et U+E000–U+10FFFF). Les surrogates non appariés sont interdits.

```
INVALID_UNICODE_SCALAR -> CANONICALIZATION_FAILED
```

### B.3 Traitement des clés dupliquées

```
DUPLICATE_INPUT_KEY -> CANONICALIZATION_FAILED
```

La résolution silencieuse (ni première clé, ni dernière clé, ni fusion) est interdite.

### B.4 Collision après NFC

Si deux clés source distinctes deviennent identiques après normalisation NFC :

```
NORMALIZED_KEY_COLLISION -> CANONICALIZATION_FAILED
```

### B.5 Ordre des clés (HD-03 — HUMAN_ACCEPTED_FOR_T0_3_B_CONTRACT)

Procédure canonique en 5 étapes :

```
etape_1: valider_les_valeurs_scalaires_Unicode
etape_2: normaliser_les_cles_en_NFC
etape_3: rejeter_toute_collision_apres_NFC
etape_4: encoder_les_cles_en_UTF-8
etape_5: trier_lexicographiquement_selon_octets_UTF-8_non_signes
```

Aucune autre politique de tri n'est autorisée.

### B.6 Vecteurs de test unicode requis

```
VEC-U01: cle_ASCII_simple             -> CANONICALIZATION_OK
VEC-U02: cle_NFC_valide               -> CANONICALIZATION_OK
VEC-U03: equivalent_NFD_de_VEC-U02    -> meme_hash_NFC_que_VEC-U02
VEC-U04: collision_NFC                -> NORMALIZED_KEY_COLLISION -> CANONICALIZATION_FAILED
VEC-U05: cle_dupliquee_en_entree      -> DUPLICATE_INPUT_KEY -> CANONICALIZATION_FAILED
VEC-U06: surrogate_U+D800_seul        -> INVALID_UNICODE_SCALAR -> CANONICALIZATION_FAILED
```

---

## C. NOMBRES

```
decimal_sign:          point_ASCII (.)
integer_part:          sans_zero_initial (sauf "0")
negative_zero_policy:  NORMALIZE_TO_ZERO
NaN:                   interdit
Infinity:              interdit
notation_scientifique: interdite
```

### C.1 Chaînes décimales

Pour les quantités non entières représentées comme chaînes :
- séparateur : point ASCII
- aucun signe plus explicite
- zéro initial interdit sauf `"0"`
- zéros finaux fractionnaires supprimés
- si la fraction devient vide, supprimer également le point
- notation scientifique interdite
- NaN et Infinity interdits
- précision déclarée par le schéma métier

### C.2 Vecteurs de test nombres

```
VEC-N01: negative_zero      -> NORMALIZE_TO_ZERO (0)
VEC-N02: trailing_zeros     -> "1.50" -> "1.5"  /  "1.00" -> "1"
```

---

## D. DATES ET HORODATAGES

```
format:      YYYY-MM-DDTHH:MM:SS.ffffffZ
timezone:    UTC uniquement
offset:      Z explicite (jamais +00:00 ni offset local)
decimales:   6 fixes (microsecondes)
```

### D.1 Vecteur de test dates

```
VEC-D01: "2026-07-18T00:28:50.823748Z" -> VALIDE
VEC-D02: "2026-07-18T00:28:50+00:00"   -> INVALIDE (offset non Z)
VEC-D03: "2026-07-18T00:28:50Z"        -> INVALIDE (decimales manquantes)
```

---

## E. NULL, ABSENCE ET ÉTATS INCONNUS

Cinq états distincts — jamais substituables :

```
null:          valeur_explicitement_nulle (JSON null)
UNKNOWN:       valeur_existante_mais_non_connue (string "UNKNOWN")
absent:        champ_non_present_dans_l_objet
REDACTED:      valeur_existante_mais_cachee (string "REDACTED")
UNAVAILABLE:   valeur_temporairement_inaccessible (string "UNAVAILABLE")
```

Chaque champ nullable déclare dans son schéma :

```
nullable:              bool
unknown_representation: string | null
absent_semantic:       string
```

---

## F. CHEMINS

Quatre champs séparés — jamais confondus :

```
display_path:               chemin_humain_affichage
canonical_path:             chemin_normalise
repository_relative_path:   relatif_a_la_racine_depot
source_uri:                 URI_source_si_applicable
```

### F.1 Règles de normalisation

```
separateur:        forward-slash (/)
lettres_lecteur:   conservees (C:/)
UNC:               prefixe // conserve
resolution:        . et .. resolus par rapport a une racine declaree
symlinks:          jamais suivis silencieusement
normalisation:     NFC
```

### F.2 Règle d'échappement de racine

Si la résolution de `..` sort de la racine déclarée :

```
PATH_ESCAPES_DECLARED_ROOT -> CANONICALIZATION_FAILED
```

Ne jamais suivre silencieusement un lien symbolique.

---

## G. HASH

```
hash_algorithm:   SHA-256 (HD-04 — HUMAN_ACCEPTED_FOR_T0_3_B_CONTRACT)
hash_encoding:    lowercase_hexadecimal
hash_length:      64_caracteres
```

### G.1 Enveloppe de hash canonique

```
hash_algorithm:           SHA-256
canonicalization_version: CANONICAL_CONTEXT_JSON_V1
hash_scope:               FULL_OBJECT | DECLARED_FIELDS_ONLY
excluded_fields:          liste_explicite_obligatoire
content_hash:             null_pendant_ecriture -> calcule_apres
```

Champs exclus par défaut (lorsqu'ils existent) :
`content_hash`, `signature`, `detached_sidecar_hash`, `checkpoint_sha256`

### G.2 Deux modes de hash

```
EMBEDDED_HASH_WITH_EXCLUSION_RULE:
  content_hash dans le JSON
  excluded_fields declare
  recalculable avec les memes exclusions

DETACHED_SHA256_SIDECAR:
  checkpoint_sha256 = null dans le JSON
  empreinte dans fichier .sha256 externe
  sidecar jamais autorefentiel
```

### G.3 Vecteur de test hash

```
VEC-H01: meme_payload -> meme_hash (TEST_B5)
VEC-H02: payloads_differents -> hashes_differents (TEST_B6)
```

---

## H. CANONICAL_HASH_ENVELOPE — APPLICATION

Objets soumis à l'enveloppe de hash :

```
ContextNode, ContextIR, ContextView, ContextPack,
ContextReceipt, ContextCompilationReport, ContextDriftEvent,
Unified_Decision_IR, vecteurs_de_test
```
