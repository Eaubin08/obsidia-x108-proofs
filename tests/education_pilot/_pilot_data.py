"""Experimental, NON-canonical data for the Oxygen textual pilot "force" (RED V0).

Sense inventory F1-F7 is PROVISIONAL (OXYGEN_TEXTUAL_LEARNING_PILOT_SPEC_V0 §2) and
awaits validation by a human author. No proprietary dictionary content is included.

Sets are strictly separated:
  E  teaching (lessons and exercises)
  C  corrections, derived ONLY from exercises of E
  V, X0..X4  validation and exams: PRIVATE, outside the repository (see below)
Each item: (item_id, word, sentence, expected, domain, register).
expected is a sense id, or "HOLD" when the context does not allow a decision.
"""
from __future__ import annotations

FORCE_SENSES = {
    "F1": "vigueur physique d'un être",
    "F2": "énergie morale, courage, volonté",
    "F3": "contrainte, violence",
    "F4": "groupe organisé, effectif (souvent au pluriel)",
    "F5": "grandeur physique (mécanique)",
    "F6": "intensité, degré",
    "F7": "locution (« à force de », « de toutes ses forces », « en force »)",
}
CHEMIN_SENSES = {"C1": "voie concrète", "C2": "manière, parcours figuré"}
CORRIGER_SENSES = {"R1": "rectifier une erreur", "R2": "punir, châtier"}
TABLE_SENSES = {"T1": "meuble"}

# --- E : teaching (lessons) ------------------------------------------------
E_LESSONS = [
    ("E-F1-1", "force", "Il n'a plus la force de marcher après la course.", "F1", "corps", "courant"),
    ("E-F1-2", "force", "Le vieil homme manque de force pour soulever le sac.", "F1", "corps", "courant"),
    ("E-F2-1", "force", "Elle a trouvé la force de pardonner à son frère.", "F2", "moral", "courant"),
    ("E-F2-2", "force", "Il faut de la force pour avouer une erreur.", "F2", "moral", "courant"),
    ("E-F3-1", "force", "Les voleurs sont entrés de force dans la maison.", "F3", "contrainte", "courant"),
    ("E-F3-2", "force", "On l'a fait signer par la force.", "F3", "contrainte", "courant"),
    ("E-F4-1", "force", "Les forces de l'ordre ont bouclé le quartier.", "F4", "institution", "journalistique"),
    ("E-F4-2", "force", "Les forces armées défilent le 14 juillet.", "F4", "institution", "journalistique"),
    ("E-F5-1", "force", "Le ressort exerce une force de dix newtons.", "F5", "physique", "technique"),
    ("E-F5-2", "force", "La force de gravité attire la pomme vers le sol.", "F5", "physique", "technique"),
    ("E-F6-1", "force", "La force du vent a cassé la branche.", "F6", "intensité", "courant"),
    ("E-F6-2", "force", "La force de son argument a convaincu le jury.", "F6", "intensité", "courant"),
    ("E-F7-1", "force", "À force de répéter, il a compris la leçon.", "F7", "locution", "courant"),
    ("E-F7-2", "force", "Elle a crié de toutes ses forces.", "F7", "locution", "courant"),
]
# Exercises are drawn from E only; their errors produce C.
E_EXERCISES = [
    ("EX-F1", "force", "Après la maladie, il reprend des forces lentement.", "F1", "corps", "courant"),
    ("EX-F3", "force", "Ils ont ouvert la porte de force.", "F3", "contrainte", "courant"),
    ("EX-F4", "force", "Les forces de police sont arrivées vite.", "F4", "institution", "journalistique"),
    ("EX-F6", "force", "La force du courant emporte le bateau.", "F6", "intensité", "courant"),
]

# --- C : corrections, origin = an E exercise -------------------------------
C_CORRECTIONS = [
    ("C-1", "EX-F1", "« reprendre des forces » parle de vigueur physique (F1), pas de courage (F2)."),
    ("C-2", "EX-F3", "« de force » marque la contrainte (F3), pas l'intensité (F6)."),
    ("C-3", "EX-F4", "« les forces de police » désigne un groupe organisé (F4)."),
    ("C-4", "EX-F6", "« la force du courant » exprime une intensité (F6), pas une grandeur mesurée (F5)."),
]

# Validation and exam items (V, X0-X4, X1-far) and their answer keys are PRIVATE:
# they live OUTSIDE the repository (path in OXYGEN_PILOT_EXAMS) and are loaded only by
# the host examiner. The student never receives them.

# Concurrent learning material (T3), never mixed with "force" sets.
CONCURRENT_LESSONS = [
    ("E-C1-1", "chemin", "Le chemin de terre traverse la forêt.", "C1", "lieu", "courant"),
    ("E-C2-1", "chemin", "Elle a fait un long chemin pour guérir.", "C2", "figuré", "courant"),
    ("E-R1-1", "corriger", "Il corrige les fautes de son texte.", "R1", "école", "courant"),
    ("E-R2-1", "corriger", "Autrefois on corrigeait les enfants désobéissants.", "R2", "punition", "courant"),
]

# A contradicting correction used to test revision history (no truth claim).
CONTRADICTION = ("C-X", "EX-F6", "Révision : dans « la force du courant », lecture F5 admise en contexte hydraulique.")

TEACHING_SETS = {"E": E_LESSONS + E_EXERCISES, "CONC": CONCURRENT_LESSONS}
