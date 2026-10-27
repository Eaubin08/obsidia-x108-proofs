# Obsidia_Live_Test_Math_3_Niveaux.docx

Source: `C:\Users\User\Desktop\BUREAU_OBSIDIA_2026\2_DOCS_OBSIDIA\02_Architecture_Moteur\ARCHI_DOCS\bazar_2023_arbo\Obsidia_Live_Test_Math_3_Niveaux.docx`

SHA256: `7fb0fd30cc50c5697fe17418de3624f4d342d1d1f72783d0a37da07eaee40361`

TruthScore: 302

Status: CANONICAL_CANDIDATE

Hits: Φ:2, λ:5, dérive:2, AVDR:9, ROM:5, énergie:2, invariant:9, PATH+:Architecture_Moteur, PATH+:ARCHI_DOCS

---

OBSIDIA — Test Mathématique Live (3 Niveaux)

Protocole de démonstration publique — Calibration sur IA neutre (sans historique)

1) Objectif & Principe

Montrer en direct qu’un LLM neutre, une fois « branché » sur la méthode obsidienne, adopte un comportement structuré et cohérent à trois niveaux de complexité mathématique. On prouve ainsi que c’est la MÉTHODE (AVDR + Double Filtre + Balance λ(t) + Réciprocité) qui opère — pas l’historique du compte.

2) Protocole de calibration (à coller en premier dans une session vierge)

🧩 Calibration Obsidienne — Version neutre

Tu es un moteur cognitif nommé Obsidia.
Résous tout problème en 4 étapes AVDR :
A — Observation : identifie la tension principale.
V — Validation : extrais les invariants/lois/constantes.
D — Déduction : applique la Balance exponentielle λ(t) pour proposer un équilibre.
R — Résonance : vérifie l’intégration harmonieuse au système global (généralisation / test / métrique).

Règles :
- Tu penses AVANT de produire.
- Tu appliques le Double Filtre (logique + éthique : transparence des hypothèses, pas d’affirmations gratuites).
- Tu testes la Réciprocité (contre-exemple ou cas inverse) si pertinent.
- Réponse courte, structurée A/V/D/R.

Commence par demander : « Quel est le problème ? »

3) Les 3 niveaux progressifs

Niveau 1 — Élémentaire (5–7 min)

Objectif : vérifier que le modèle suit bien AVDR et identifie une loi d’équilibre simple.

Problème proposé (au choix) :

1A) Montrer que la somme des n premiers entiers impairs vaut n².

1B) Déduire le nombre d’or φ à partir de la suite de Fibonacci (modèle d’équilibre de croissance).

🔧 Prompt à coller (choix 1A) :
« Applique AVDR à : Prouver que 1+3+5+…+(2n−1)=n².
A : identifier la tension (structure récurrente / aire d’un carré),
V : invariant (différences constantes = 2 ; construction géométrique),
D : équilibre (réécriture récurrente → carré parfait),
R : généralisation / test pour n=1..5 ; réciprocité : que se passe-t-il pour somme des pairs ? »

🔧 Prompt à coller (choix 1B) :
« Applique AVDR à : Retrouver φ (≈1,618) depuis Fibonacci.
A : tension croissance/équilibre ;
V : invariant récurrent F_{n+1}/F_n → limite ;
D : équilibre λ(t) → x = 1 + 1/x ;
R : vérif numérique (n=8..13) + réciprocité : que devient la suite si on brise l’invariant ? »

Niveau 2 — Intermédiaire (analyse / algèbre — 7–10 min)

Objectif : montrer un raisonnement par invariants + métrique de justesse (borne, norme).

Problème proposé : « Jensen simple / convexité → borne sur moyenne non-linéaire » OU « Convergence de ∑ 1/n² et majoration de l’erreur de troncature ».

🔧 Prompt à coller (exemple série p=2) :
« Applique AVDR à : montrer la convergence de la série ∑_{n≥1} 1/n² et donner une borne simple de l’erreur après N termes.
A : tension (série vs intégrale),
V : invariants : test intégral / comparaison ;
D : équilibre : borne de l’erreur via ∫_{N}^{∞} 1/x² dx = 1/N ;
R : test numérique pour N=10,100 ; réciprocité : pourquoi p=1 diverge ? »

Niveau 3 — Avancé (PDE / dynamique — 8–12 min)

Objectif : dériver une inégalité d’énergie (invariant) et montrer la stabilisation — schéma général transposable à Navier–Stokes.

Problème proposé : Burgers visqueuse 1D : u_t + u u_x = ν u_xx, données lisses à décroissance rapide.

🔧 Prompt à coller :
« Applique AVDR à l’énergie L² pour Burgers visqueuse 1D : u_t + u u_x = ν u_{xx}.
A : tension (non-linéarité vs dissipation),
V : invariant/identité : dériver (1/2) d/dt ∥u∥₂² ;
D : équilibre : montrer d/dt ∥u∥₂² = −2ν ∥u_x∥₂² ≤ 0 (après intégration par parties et annulation du terme convectif),
R : conséquences : décroissance L², pas d’explosion ; réciprocité : que change ν→0 ? »

4) Grille d’évaluation (par niveau — sur 10)

Critère

Description

Score (0–2)

A — Observation

Tension correctement identifiée (désordre / objectif).

V — Validation

Invariants / identités / tests posés explicitement.

D — Déduction

Usage de λ(t) / équilibre / dérivation rigoureuse.

R — Résonance

Vérification globale / test numérique / généralisation.

Réciprocité

Contre-exemple ou cas inverse traité.

Transparence

Hypothèses claires, pas d’affirmations gratuites.

Total par niveau : /10 — Total sur 3 niveaux : /30. Seuil de réussite fort : ≥24/30 et aucun critère à 0.

5) Variante contrôle (sans calibration)

Dans une deuxième fenêtre, posez exactement le même problème AU MÊME MODÈLE, sans le prompt de calibration. Comparez : structure AVDR, transparence, métriques. L’écart de qualité montre l’apport de la méthode obsidienne.

6) Script live (3 minutes d’intro)

1. « Cette démo prouve que la structure obsidienne fonctionne sur n’importe quel modèle. »
2. « Je calibre le moteur avec AVDR + Double Filtre + λ(t) (20 secondes). »
3. « On résout 3 problèmes croissants : élémentaire → intermédiaire → avancé. »
4. « À chaque fois, on coche Observation, Validation, Déduction, Résonance, Réciprocité. »
5. « Puis on refait sans calibration : vous verrez la différence. »

7) Notes & Conseils

• Chrono : 5–7 min / 7–10 min / 8–12 min (total 20–30 min).

• Si le modèle hésite : reformule « Identifie A puis V » (forcer la structure pas-à-pas).

• Toujours expliciter les hypothèses (domaines, régularité, bornes).

• Conclure : « Ce que vous avez vu, c’est la méthode — pas l’historique. »
